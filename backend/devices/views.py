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
from dotenv import load_dotenv

from .models import Device, AuthorizationToken, Command, ActionParameter
from .crypto import (
    decrypt_with_private_key,
    encrypt_with_public_key,
    get_server_public_key_pem, encrypt_with_session_key, decrypt_with_session_key
)

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([AllowAny])
def generate_token(request):
    """Generate a new authorization token for device registration"""
    try:
        data = json.loads(request.body)
        admin_key = data.get('adminKey')
        load_dotenv()
        # In production, use a proper authentication mechanism
        # This is just a simple example
        if admin_key != os.environ.get('ADMIN_SECRET_KEY'):
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
    Zwraca listę wszystkich aktywnych tokenów autoryzacyjnych
    (tokeny, które nie wygasły i nie zostały jeszcze użyte)
    """
    try:
        # Pobierz wszystkie tokeny, które są aktywne
        active_tokens = AuthorizationToken.objects.filter(
            is_used=False,
            expires_at__gt=timezone.now()
        ).order_by('-created_at')

        # Przygotuj dane w formacie JSON bez używania serializera
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
        logger.error(f"Błąd podczas pobierania aktywnych tokenów: {str(e)}")
        return Response(
            {'error': 'Wystąpił błąd podczas pobierania listy aktywnych tokenów'},
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
        logger.info( "encrypted data received")

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
            'capabilities': device.capabilities
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