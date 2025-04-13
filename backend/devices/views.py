import json
import uuid
import logging
from datetime import timedelta

from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from django.shortcuts import get_object_or_404

from .models import Device, AuthorizationToken, Command, ActionParameter
from .crypto import (
    decrypt_with_private_key,
    encrypt_with_public_key,
    get_server_public_key_pem
)

# Configure logging
logger = logging.getLogger(__name__)


# Django views for APIs

@csrf_exempt
@require_POST
def generate_token(request):
    """Generate a new authorization token for device registration"""
    try:
        data = json.loads(request.body)
        admin_key = data.get('adminKey')

        # In production, use a proper authentication mechanism
        # This is just a simple example
        if admin_key != 'your-admin-secret-key':
            return JsonResponse({'error': 'Unauthorized'}, status=403)

        # Generate token
        token_value = uuid.uuid4().hex
        expires_at = timezone.now() + timedelta(hours=24)

        # Save token
        token = AuthorizationToken.objects.create(
            token=token_value,
            expires_at=expires_at,
            created_by=request.META.get('REMOTE_ADDR')
        )

        return JsonResponse({
            'token': token_value,
            'expiresAt': expires_at.isoformat()
        })
    except Exception as e:
        logger.error(f"Token generation error: {str(e)}")
        return JsonResponse({'error': 'Error generating token'}, status=500)


@csrf_exempt
@require_POST
def register_device(request):
    """Register a new device using an authorization token"""
    try:
        data = json.loads(request.body)
        encrypted_data = data.get('data')

        if not encrypted_data:
            return JsonResponse({'error': 'Missing encrypted data'}, status=400)

        # Decrypt the registration data
        registration_data = decrypt_with_private_key(encrypted_data)

        device_info = registration_data.get('deviceInfo', {})
        auth_token = registration_data.get('authToken')

        # Validate token
        try:
            token = AuthorizationToken.objects.get(token=auth_token)
            if not token.is_valid:
                return JsonResponse({'error': 'Invalid or expired token'}, status=403)
        except AuthorizationToken.DoesNotExist:
            return JsonResponse({'error': 'Invalid token'}, status=403)

        # Extract device information
        device_id = device_info.get('deviceId')
        public_key = device_info.get('publicKey')
        metadata = device_info.get('metadata', {})
        capabilities = device_info.get('capabilities', [])

        # Generate a session key
        session_key = uuid.uuid4().hex + uuid.uuid4().hex  # 64 bytes (32 hex chars * 2)

        # Create the device record
        device, created = Device.objects.update_or_create(
            device_id=device_id,
            defaults={
                'public_key': public_key,
                'session_key': session_key,
                'device_type': metadata.get('type', 'unknown'),
                'capabilities': capabilities,
                'metadata': metadata,
                'is_active': True
            }
        )

        # Mark the token as used if this is a new device
        if created:
            token.is_used = True
            token.save()

        # Prepare response
        response_data = {
            'sessionKey': session_key,
            'message': 'Registration successful',
            'serverTime': timezone.now().isoformat()
        }

        # Encrypt the response with the device's public key
        encrypted_response = encrypt_with_public_key(response_data, public_key)

        logger.info(f"Device registered: {device_id} ({metadata.get('type')})")
        return JsonResponse(encrypted_response, safe=False)

    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return JsonResponse({'error': 'Registration failed'}, status=500)


@require_GET
def get_devices(request):
    """API to get list of registered devices"""
    devices = Device.objects.filter(is_active=True)
    device_list = []

    for device in devices:
        device_list.append({
            'id': str(device.id),
            'deviceId': device.device_id,
            'deviceType': device.device_type,
            'capabilities': device.capabilities,
            'lastSeen': device.last_seen.isoformat()
        })

    return JsonResponse({'devices': device_list})


@require_GET
def get_device_capabilities(request, device_id):
    """Get capabilities for a specific device"""
    try:
        device = get_object_or_404(Device, device_id=device_id, is_active=True)

        return JsonResponse({
            'deviceId': device.device_id,
            'deviceType': device.device_type,
            'capabilities': device.capabilities
        })
    except Exception as e:
        logger.error(f"Error getting device capabilities: {str(e)}")
        return JsonResponse({'error': str(e)}, status=404)


@require_GET
def get_action_parameters(request, action_name):
    """Get required parameters for a specific action"""
    try:
        # Try to get from database
        action_param = ActionParameter.objects.filter(action_name=action_name).first()

        if action_param:
            return JsonResponse({
                'action': action_name,
                'parameters': action_param.parameters,
                'description': action_param.description
            })

        # If not in database, use default parameter structure
        # This allows for dynamic support of actions even if they aren't pre-defined
        default_params = [
            {"name": "num1", "type": "number", "required": True},
            {"name": "num2", "type": "number", "required": True}
        ]

        # Special cases for certain operations
        if action_name == "factorial":
            default_params = [
                {"name": "num1", "type": "number", "required": True}
            ]

        return JsonResponse({
            'action': action_name,
            'parameters': default_params,
            'description': f"Execute {action_name} operation"
        })
    except Exception as e:
        logger.error(f"Error getting action parameters: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_POST
def execute_command(request):
    """Execute a command on a device"""
    try:
        data = json.loads(request.body)
        device_id = data.get('deviceId')
        command_name = data.get('command')
        params = data.get('params', {})

        # Validate required fields
        if not device_id or not command_name:
            return JsonResponse({'error': 'Missing required fields'}, status=400)

        # Get the device
        try:
            device = Device.objects.get(device_id=device_id, is_active=True)
        except Device.DoesNotExist:
            return JsonResponse({'error': 'Device not found'}, status=404)

        # Validate the command is supported by the device
        if command_name not in device.capabilities:
            return JsonResponse({
                'error': f"Command '{command_name}' not supported by this device"
            }, status=400)

        # Create the command
        command = Command.objects.create(
            device=device,
            name=command_name,
            params=params,
            status='pending'
        )

        # In a real implementation, you would send this command to the device
        # For now, we'll just return the command ID
        logger.info(f"Command {command_name} created for device {device_id}")

        return JsonResponse({
            'status': 'Command queued',
            'commandId': str(command.id)
        })

    except Exception as e:
        logger.error(f"Execute command error: {str(e)}")
        return JsonResponse({'error': 'Error processing command'}, status=500)


@require_GET
def get_command_status(request, command_id):
    """Get the status of a command"""
    try:
        command = get_object_or_404(Command, id=command_id)

        return JsonResponse({
            'id': str(command.id),
            'deviceId': command.device.device_id,
            'name': command.name,
            'params': command.params,
            'status': command.status,
            'result': command.result,
            'createdAt': command.created_at.isoformat(),
            'updatedAt': command.updated_at.isoformat()
        })
    except Exception as e:
        logger.error(f"Error getting command status: {str(e)}")
        return JsonResponse({'error': str(e)}, status=404)


@csrf_exempt
@require_POST
def update_command_status(request, command_id):
    """Update the status and result of a command (called by device)"""
    try:
        data = json.loads(request.body)
        device_id = data.get('deviceId')
        encrypted_data = data.get('data')

        # Validate required fields
        if not device_id or not encrypted_data:
            return JsonResponse({'error': 'Missing required fields'}, status=400)

        # Get the device
        try:
            device = Device.objects.get(device_id=device_id, is_active=True)
        except Device.DoesNotExist:
            return JsonResponse({'error': 'Device not found'}, status=404)

        # Get the command
        try:
            command = Command.objects.get(id=command_id, device=device)
        except Command.DoesNotExist:
            return JsonResponse({'error': 'Command not found'}, status=404)

        # Decrypt the result data
        from .crypto import decrypt_with_session_key
        result_data = decrypt_with_session_key(json.loads(encrypted_data), device.session_key)

        # Update the command
        status = 'completed' if result_data.get('status') == 'success' else 'failed'
        command.status = status
        command.result = result_data
        command.save()

        logger.info(f"Command {command_id} updated to {status}")

        return JsonResponse({'status': 'Command updated'})
    except Exception as e:
        logger.error(f"Update command error: {str(e)}")
        return JsonResponse({'error': 'Error updating command'}, status=500)


@require_GET
def get_device_commands(request, device_id):
    """Get all commands for a specific device"""
    try:
        device = get_object_or_404(Device, device_id=device_id, is_active=True)
        commands = Command.objects.filter(device=device).order_by('-created_at')[:100]

        command_list = []
        for command in commands:
            command_list.append({
                'id': str(command.id),
                'name': command.name,
                'params': command.params,
                'status': command.status,
                'result': command.result,
                'createdAt': command.created_at.isoformat(),
                'updatedAt': command.updated_at.isoformat()
            })

        return JsonResponse({'commands': command_list})
    except Exception as e:
        logger.error(f"Error getting device commands: {str(e)}")
        return JsonResponse({'error': str(e)}, status=404)


@require_GET
def get_server_public_key(request):
    """Return the server's public key"""
    try:
        return JsonResponse({
            'publicKey': get_server_public_key_pem()
        })
    except Exception as e:
        logger.error(f"Error getting server public key: {str(e)}")
        return JsonResponse({'error': 'Error retrieving public key'}, status=500)


@require_GET
def get_pending_commands(request, device_id):
    """Get pending commands for a device (called by device)"""
    try:
        device = get_object_or_404(Device, device_id=device_id, is_active=True)
        pending_commands = Command.objects.filter(device=device, status='pending')

        command_list = []
        for command in pending_commands:
            # Mark as sent
            command.status = 'sent'
            command.save()

            command_list.append({
                'id': str(command.id),
                'name': command.name,
                'params': command.params
            })

        return JsonResponse({'commands': command_list})
    except Exception as e:
        logger.error(f"Error getting pending commands: {str(e)}")
        return JsonResponse({'error': str(e)}, status=404)