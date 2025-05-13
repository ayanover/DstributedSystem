from django.core.management import call_command
from django.http import JsonResponse
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from .forms import SignupForm
from rest_framework.permissions import AllowAny

@api_view(['GET'])
def me(request):
    return JsonResponse({
        'id': request.user.id,
        'name': request.user.name,
        'email': request.user.email,
        'is_staff': request.user.is_staff,
    })


@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def register(request):
    data = request.data
    message = 'success'
    errors = {}

    form = SignupForm({
        'email': data.get('email'),
        'name': data.get('name'),
        'password1': data.get('password1'),
        'password2': data.get('password2'),
    })

    password = data.get('password1', '')
    if password and password.isdigit():
        if not 'password1' in form.errors:
            form.errors['password1'] = []
        form.errors['password1'].append('Password cannot consist of only numbers.')

    if form.is_valid():
        form.save()
        return JsonResponse({'message': message})
    else:
        for field, error_list in form.errors.items():
            errors[field] = [str(error) for error in error_list]

        return JsonResponse({
            'message': 'error',
            'errors': errors
        })
import json
import uuid
import logging
from datetime import timedelta
from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Device, AuthorizationToken, Command, ActionParameter
from .crypto import (
    decrypt_with_private_key,
    encrypt_with_public_key,
    get_server_public_key_pem, encrypt_with_session_key, decrypt_with_session_key
)

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_commands(request):
    """Get command history across all devices"""
    try:
        # Fetch commands from all devices, with most recent first
        commands = Command.objects.all().order_by('-created_at')[:200]  # Limit to most recent 200 commands

        # Prepare data with device information included
        command_list = []
        for command in commands:
            command_list.append({
                'id': str(command.id),
                'deviceId': command.device.device_id,
                'deviceType': command.device.device_type,
                'name': command.name,
                'params': command.params,
                'status': command.status,
                'result': command.result,
                'createdAt': command.created_at.isoformat(),
                'updatedAt': command.updated_at.isoformat()
            })

        return Response({'commands': command_list})
    except Exception as e:
        logger.error(f"Error retrieving command history: {str(e)}")
        return Response(
            {'error': 'An error occurred while retrieving command history'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_devices(request):
    call_command('mark_inactive_devices', timeout=60)
    """API to get list of all devices (both active and inactive)"""
    devices = Device.objects.all()
    device_list = []

    for device in devices:
        device_list.append({
            'id': str(device.id),
            'deviceId': device.device_id,
            'deviceType': device.device_type,
            'capabilities': device.capabilities,
            'lastSeen': device.last_seen.isoformat(),
            'isActive': device.is_active
        })

    return Response({'devices': device_list})


@api_view(['POST'])
@permission_classes([AllowAny])
def device_heartbeat(request, device_id):
    """Update the device's last_seen timestamp (heartbeat mechanism)"""
    try:
        try:
            device = Device.objects.get(device_id=device_id)
        except Device.DoesNotExist:
            return Response({'error': 'Device not found'}, status=status.HTTP_404_NOT_FOUND)

        # Verify the device identity (optional - can use session key or other method)
        data = json.loads(request.body)
        if 'data' in data:
            try:
                encrypted_data = data.get('data')
                decrypt_with_session_key(encrypted_data, device.session_key)
                # Just verifying encryption works, not using the data
            except Exception as e:
                logger.warning(f"Error decrypting heartbeat data: {str(e)}")
                return Response({'error': 'Authentication failed'}, status=status.HTTP_403_FORBIDDEN)

        # If previously inactive, reactivate the device
        was_inactive = not device.is_active
        if was_inactive:
            device.is_active = True
            logger.info(f"Device reactivated via heartbeat: {device_id}")

        # Save the device to update the last_seen timestamp (auto_now field)
        device.save()

        return Response({'status': 'ok', 'active': True})
    except Exception as e:
        logger.error(f"Error processing heartbeat: {str(e)}")
        return Response({'error': 'Heartbeat failed'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def reconnect_device(request):
    """Reconnect a previously registered device"""
    try:
        data = json.loads(request.body)
        device_id = data.get('deviceId')
        public_key_pem = data.get('publicKey')

        if not device_id or not public_key_pem:
            return Response({'error': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)

        # Find the device in the database
        try:
            device = Device.objects.get(device_id=device_id)
        except Device.DoesNotExist:
            return Response({'error': 'Device not found', 'action': 'register'},
                            status=status.HTTP_404_NOT_FOUND)

        # Verify the public key matches
        if device.public_key != public_key_pem:
            return Response({'error': 'Authentication failed'}, status=status.HTTP_403_FORBIDDEN)

        # Generate a new session key
        session_key = uuid.uuid4().hex + uuid.uuid4().hex  # 64 bytes

        # Update device - EXPLICITLY SET TO ACTIVE
        device.session_key = session_key
        device.is_active = True  # This line ensures the device is marked as active
        device.save()

        logger.info(f"Device reconnected and marked active: {device_id}")

        # Encrypt the response with the device's public key
        response_data = {
            'sessionKey': session_key,
            'message': 'Reconnection successful',
            'serverTime': timezone.now().isoformat()
        }

        encrypted_response = encrypt_with_public_key(response_data, device.public_key)

        return Response(encrypted_response, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Reconnection error: {str(e)}")
        return Response({'error': 'Reconnection failed'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def generate_token(request):
    """Generate a new authorization token for device registration"""
    try:
        data = json.loads(request.body)
        admin_key = data.get('adminKey')

        # In production, use a proper authentication mechanism
        # This is just a simple example
        if admin_key != 'your-admin-secret-key':
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)

        token_value = uuid.uuid4().hex
        expires_at = timezone.now() + timedelta(hours=24)

        token = AuthorizationToken.objects.create(
            token=token_value,
            expires_at=expires_at,
            created_by=request.META.get('REMOTE_ADDR')
        )

        return Response({
            'token': token_value,
            'expiresAt': expires_at.isoformat()
        })
    except Exception as e:
        logger.error(f"Token generation error: {str(e)}")
        return Response({'error': 'Error generating token'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def deregister_device(request, device_id):
    """Mark a device as inactive when it disconnects"""
    try:
        data = json.loads(request.body)

        # Validate the device
        try:
            device = Device.objects.get(device_id=device_id, is_active=True)
        except Device.DoesNotExist:
            return Response({'error': 'Device not found'}, status=status.HTTP_404_NOT_FOUND)

        # Optional: Verify encrypted data using session key
        if 'data' in data:
            try:
                encrypted_data = data.get('data')
                decrypted_data = decrypt_with_session_key(encrypted_data, device.session_key)
                # You could verify the decrypted data here if needed
            except Exception as e:
                logger.warning(f"Error decrypting deregistration data: {str(e)}")
                # Continue anyway - we still want to deregister

        # Mark the device as inactive
        device.is_active = False
        device.save()

        logger.info(f"Device deregistered: {device_id}")
        return Response({'status': 'Device deregistered'})
    except Exception as e:
        logger.error(f"Error deregistering device: {str(e)}")
        return Response({'error': 'Deregistration failed'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def view_tokens(request):
    try:
        tokens = AuthorizationToken.objects.all()  # Get all tokens
        token_data = []

        for token in tokens:
            token_data.append({
                'token': token.token,
                'expiresAt': token.expires_at.isoformat()
            })

        return Response(token_data)
    except Exception as e:
        logger.error(f"Error fetching tokens: {str(e)}")
        return Response({'error': 'Error fetching tokens'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_active_tokens(request):
    """
    Return a list of all active authorization tokens
    (tokens that have not expired and have not been used yet)
    """
    try:
        # Get all active tokens
        active_tokens = AuthorizationToken.objects.filter(
            is_used=False,
            expires_at__gt=timezone.now()
        ).order_by('-created_at')

        # Prepare data in JSON format without using a serializer
        tokens_data = []
        for token in active_tokens:
            tokens_data.append({
                'token': token.token,
                'createdAt': token.created_at.isoformat(),
                'expiresAt': token.expires_at.isoformat(),
                'isUsed': token.is_used,
                'isValid': token.is_valid,
                'createdBy': token.created_by
            })

        return Response({
            'count': len(tokens_data),
            'tokens': tokens_data
        })
    except Exception as e:
        logger.error(f"Error retrieving active tokens: {str(e)}")
        return Response(
            {'error': 'An error occurred while retrieving the list of active tokens'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])  # Allow anonymous access for device registration
def register_device(request):
    """Register a new device using an authorization token"""
    try:
        data = json.loads(request.body)
        encrypted_data = data.get('data')

        if not encrypted_data:
            return Response({'error': 'Missing encrypted data'}, status=status.HTTP_400_BAD_REQUEST)
        logger.info("encrypted data received")

        # Decrypt the registration data
        registration_data = decrypt_with_private_key(encrypted_data)

        # Extract device information
        device_info = registration_data.get('deviceInfo', {})
        auth_token = registration_data.get('authToken')

        # Validate token
        try:
            token = AuthorizationToken.objects.get(token=auth_token)
            if not token.is_valid:
                return Response({'error': 'Invalid or expired token'}, status=status.HTTP_403_FORBIDDEN)
        except AuthorizationToken.DoesNotExist:
            return Response({'error': 'Invalid token'}, status=status.HTTP_403_FORBIDDEN)
        logger.info("token valid")
        # Extract device information
        device_id = device_info.get('deviceId')
        public_key = device_info.get('publicKey')
        metadata = device_info.get('metadata', {})
        capabilities = device_info.get('operations', [])  # Note: this matches the client's field name

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
        logger.info("device created")
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
        return Response(encrypted_response, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return Response({'error': 'Registration failed'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
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

    return Response({'devices': device_list})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_device_capabilities(request, device_id):
    """Get capabilities for a specific device"""
    try:
        device = get_object_or_404(Device, device_id=device_id, is_active=True)

        return Response({
            'deviceId': device.device_id,
            'deviceType': device.device_type,
            'capabilities': device.capabilities,
            'lastSeen': device.last_seen.isoformat()
        })
    except Exception as e:
        logger.error(f"Error getting device capabilities: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_action_parameters(request, action_name):
    """Get required parameters for a specific action"""
    try:
        # Try to get from database
        action_param = ActionParameter.objects.filter(action_name=action_name).first()

        if action_param:
            return Response({
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
        elif action_name == "execute_code":
            default_params = [
                {"name": "code", "type": "string", "required": True}
            ]
        elif action_name == "execute_code_with_input":
            default_params = [
                {"name": "code", "type": "string", "required": True},
                {"name": "input_data", "type": "string", "required": True}
            ]

        return Response({
            'action': action_name,
            'parameters': default_params,
            'description': f"Execute {action_name} operation"
        })
    except Exception as e:
        logger.error(f"Error getting action parameters: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def execute_command(request):
    """Execute a command on a device"""
    try:
        data = json.loads(request.body)
        device_id = data.get('deviceId')
        command_name = data.get('command')
        params = data.get('params', {})

        # Validate required fields
        if not device_id or not command_name:
            return Response({'error': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)

        # Get the device
        try:
            device = Device.objects.get(device_id=device_id, is_active=True)
        except Device.DoesNotExist:
            return Response({'error': 'Device not found'}, status=status.HTTP_404_NOT_FOUND)

        # Validate the command is supported by the device
        if command_name not in device.capabilities:
            return Response({
                'error': f"Command '{command_name}' not supported by this device"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validate parameters for code execution commands
        if command_name == "execute_code":
            if "code" not in params:
                return Response({
                    'error': "Missing required parameter 'code'"
                }, status=status.HTTP_400_BAD_REQUEST)
        elif command_name == "execute_code_with_input":
            if "code" not in params or "input_data" not in params:
                return Response({
                    'error': "Missing required parameters for execute_code_with_input"
                }, status=status.HTTP_400_BAD_REQUEST)

        # Extra security measure: Log all code execution commands
        if command_name in ["execute_code", "execute_code_with_input"]:
            logger.debug(f"Code content: {params.get('code', '')[:100]}...")

        # Create the command
        command = Command.objects.create(
            device=device,
            name=command_name,
            params=params,
            status='pending'
        )

        logger.info(f"Command {command_name} created for device {device_id}")

        return Response({
            'status': 'Command queued',
            'commandId': str(command.id)
        })

    except Exception as e:
        logger.error(f"Execute command error: {str(e)}")
        return Response({'error': 'Error processing command'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_command_status(request, command_id):
    """Get the status of a command"""
    try:
        command = get_object_or_404(Command, id=command_id)

        return Response({
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
        return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([AllowAny])  # Devices might not have authentication
def update_command_status(request, command_id):
    """Update the status and result of a command (called by device)"""
    try:
        data = json.loads(request.body)
        device_id = data.get('deviceId')
        encrypted_data = data.get('data')

        # Validate required fields
        if not device_id or not encrypted_data:
            return Response({'error': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)

        # Get the device
        try:
            device = Device.objects.get(device_id=device_id, is_active=True)
        except Device.DoesNotExist:
            return Response({'error': 'Device not found'}, status=status.HTTP_404_NOT_FOUND)

        # Get the command
        try:
            command = Command.objects.get(id=command_id, device=device)
        except Command.DoesNotExist:
            return Response({'error': 'Command not found'}, status=status.HTTP_404_NOT_FOUND)

        # Decrypt the result data
        result_data = decrypt_with_session_key(encrypted_data, device.session_key)

        # Update the command
        command.status = result_data.get('status', 'completed')
        command.result = result_data
        command.save()

        # Update device's last_seen timestamp
        device.save()  # This will update the auto_now field

        logger.info(f"Command {command_id} updated to {command.status}")

        return Response({'status': 'Command updated'})
    except Exception as e:
        logger.error(f"Update command error: {str(e)}")
        return Response({'error': 'Error updating command'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
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

        return Response({'commands': command_list})
    except Exception as e:
        logger.error(f"Error getting device commands: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_server_public_key(request):
    """Return the server's public key"""
    try:
        return Response({
            'publicKey': get_server_public_key_pem()
        })
    except Exception as e:
        logger.error(f"Error getting server public key: {str(e)}")
        return Response({'error': 'Error retrieving public key'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])  # Devices may not have authentication
def get_pending_commands(request, device_id):
    """Get pending commands for a device (called by device)"""
    try:
        # Get the device
        device = get_object_or_404(Device, device_id=device_id, is_active=True)

        # Update last_seen timestamp
        device.save()  # This will update the auto_now field

        # Get pending commands
        pending_commands = Command.objects.filter(device=device, status='pending')

        command_list = []
        for command in pending_commands:
            # Mark as sent
            command.status = 'sent'
            command.save()

            # Add to response
            command_list.append({
                'id': str(command.id),
                'name': command.name,
                'params': command.params
            })

        # Encrypt the response if the device has a session key
        if device.session_key:
            command_data = {
                'commands': command_list,
                'timestamp': timezone.now().isoformat()
            }
            encrypted_data = encrypt_with_session_key(command_data, device.session_key)
            return Response({'data': encrypted_data}, status=status.HTTP_200_OK)
        else:
            # Fallback for devices without session key (shouldn't happen in normal operation)
            return Response({'commands': command_list}, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Error getting pending commands: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)