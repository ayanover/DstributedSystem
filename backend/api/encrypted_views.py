import json
import uuid
import logging
from datetime import timedelta
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Device, AuthorizationToken, Command, ActionParameter
from .crypto import (
    decrypt_with_private_key,
    encrypt_with_public_key,
    get_server_public_key_pem,
    encrypt_with_session_key,
    decrypt_with_session_key
)

logger = logging.getLogger(__name__)

# In-memory storage for frontend sessions (use Redis in production)
FRONTEND_SESSIONS = {}


# Helper function to clean up old sessions
def cleanup_old_sessions():
    """Clean up sessions older than 24 hours"""
    cutoff_time = timezone.now() - timedelta(hours=24)
    expired_sessions = []

    for frontend_id, session_data in FRONTEND_SESSIONS.items():
        if session_data['created_at'] < cutoff_time:
            expired_sessions.append(frontend_id)

    for frontend_id in expired_sessions:
        del FRONTEND_SESSIONS[frontend_id]
        logger.info(f"Cleaned up expired frontend session: {frontend_id}")

    return len(expired_sessions)


@api_view(['POST'])
@permission_classes([AllowAny])
def establish_frontend_session(request):
    """Establish encrypted session with frontend (similar to device registration)"""
    try:
        data = json.loads(request.body)
        frontend_id = data.get('frontendId')

        if not frontend_id:
            return Response({'error': 'Missing frontend ID'}, status=status.HTTP_400_BAD_REQUEST)

        # Clean up old sessions periodically
        cleanup_old_sessions()

        # Create session key (64 characters like device sessions)
        session_key = uuid.uuid4().hex + uuid.uuid4().hex

        # Store session
        FRONTEND_SESSIONS[frontend_id] = {
            'session_key': session_key,
            'created_at': timezone.now(),
            'last_used': timezone.now()
        }

        logger.info(f"Frontend session established: {frontend_id}")

        return Response({
            'sessionKey': session_key,
            'message': 'Frontend session established',
            'serverTime': timezone.now().isoformat()
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Frontend session establishment error: {str(e)}")
        return Response({'error': 'Session establishment failed'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def execute_command_encrypted(request):
    """Execute a command with frontend encryption support"""
    try:
        # Check if this is an encrypted frontend request
        frontend_id = request.META.get('HTTP_X_FRONTEND_ID')
        data = json.loads(request.body)

        if frontend_id and 'data' in data:
            # This is an encrypted frontend request
            encrypted_data = data.get('data')

            # Validate frontend session
            if frontend_id not in FRONTEND_SESSIONS:
                return Response({'error': 'Invalid or expired frontend session'}, status=status.HTTP_401_UNAUTHORIZED)

            session_key = FRONTEND_SESSIONS[frontend_id]['session_key']

            # Update last used time
            FRONTEND_SESSIONS[frontend_id]['last_used'] = timezone.now()

            try:
                # Decrypt the frontend request
                decrypted_data = decrypt_with_session_key(encrypted_data, session_key)

                device_id = decrypted_data.get('deviceId')
                command_name = decrypted_data.get('command')
                params = decrypted_data.get('params', {})

                logger.debug(f"Decrypted frontend command: {command_name} for device {device_id}")

            except Exception as e:
                logger.error(f"Failed to decrypt frontend request: {str(e)}")
                return Response({'error': 'Decryption failed'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            # This is a regular unencrypted request (backwards compatibility)
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
            logger.info(
                f"Frontend encrypted code execution - Frontend: {frontend_id}, Device: {device_id}, User: {request.user}")
            # Don't log the actual code content in production for security

        # Create the command
        command = Command.objects.create(
            device=device,
            name=command_name,
            params=params,
            status='pending'
        )

        logger.info(f"Encrypted command {command_name} created for device {device_id} from frontend {frontend_id}")

        # Prepare response
        response_data = {
            'status': 'Command queued',
            'commandId': str(command.id),
            'encrypted': True if frontend_id else False
        }

        # Encrypt response if this was an encrypted request
        if frontend_id and frontend_id in FRONTEND_SESSIONS:
            session_key = FRONTEND_SESSIONS[frontend_id]['session_key']
            encrypted_response = encrypt_with_session_key(response_data, session_key)
            return Response({'data': encrypted_response}, status=status.HTTP_200_OK)
        else:
            return Response(response_data, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Execute encrypted command error: {str(e)}")
        return Response({'error': 'Error processing command'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_command_status_encrypted(request, command_id):
    """Get command status with frontend encryption support"""
    try:
        # Check if this is an encrypted frontend request
        frontend_id = request.META.get('HTTP_X_FRONTEND_ID')

        if frontend_id and frontend_id in FRONTEND_SESSIONS:
            # This is an encrypted frontend request
            data = json.loads(request.body)
            encrypted_data = data.get('data')
            session_key = FRONTEND_SESSIONS[frontend_id]['session_key']

            # Update last used time
            FRONTEND_SESSIONS[frontend_id]['last_used'] = timezone.now()

            try:
                # Decrypt the request (though command_id is also in URL)
                decrypted_data = decrypt_with_session_key(encrypted_data, session_key)
                logger.debug(f"Decrypted status request for command {command_id}")
            except Exception as e:
                logger.error(f"Failed to decrypt frontend status request: {str(e)}")
                return Response({'error': 'Decryption failed'}, status=status.HTTP_400_BAD_REQUEST)

        # Get the command
        try:
            command = Command.objects.get(id=command_id)
        except Command.DoesNotExist:
            return Response({'error': 'Command not found'}, status=status.HTTP_404_NOT_FOUND)

        # Prepare response
        response_data = {
            'id': str(command.id),
            'deviceId': command.device.device_id,
            'name': command.name,
            'params': command.params,
            'status': command.status,
            'result': command.result,
            'createdAt': command.created_at.isoformat(),
            'updatedAt': command.updated_at.isoformat(),
            'encrypted': True if frontend_id else False
        }

        # Encrypt response if this was an encrypted request
        if frontend_id and frontend_id in FRONTEND_SESSIONS:
            session_key = FRONTEND_SESSIONS[frontend_id]['session_key']
            encrypted_response = encrypt_with_session_key(response_data, session_key)
            return Response({'data': encrypted_response}, status=status.HTTP_200_OK)
        else:
            return Response(response_data, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Get encrypted command status error: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_frontend_session_info(request):
    """Get information about active frontend sessions"""
    try:
        frontend_id = request.META.get('HTTP_X_FRONTEND_ID')

        if frontend_id and frontend_id in FRONTEND_SESSIONS:
            session = FRONTEND_SESSIONS[frontend_id]
            return Response({
                'frontendId': frontend_id,
                'sessionEstablished': True,
                'createdAt': session['created_at'].isoformat(),
                'lastUsed': session['last_used'].isoformat(),
                'totalSessions': len(FRONTEND_SESSIONS)
            })
        else:
            return Response({
                'sessionEstablished': False,
                'totalSessions': len(FRONTEND_SESSIONS)
            })
    except Exception as e:
        logger.error(f"Get frontend session info error: {str(e)}")
        return Response({'error': 'Error retrieving session info'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])  # Allow for maintenance scripts
def cleanup_frontend_sessions(request):
    """Clean up old frontend sessions (call this periodically or via cron)"""
    try:
        # Optional admin key check for security
        admin_key = request.data.get('adminKey')
        if admin_key != 'your-admin-secret-key':  # Change this in production
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)

        cleaned_count = cleanup_old_sessions()

        return Response({
            'message': 'Session cleanup completed',
            'cleaned_sessions': cleaned_count,
            'active_sessions': len(FRONTEND_SESSIONS)
        })

    except Exception as e:
        logger.error(f"Frontend session cleanup error: {str(e)}")
        return Response({'error': 'Cleanup failed'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def debug_frontend_sessions(request):
    """Debug endpoint to view active frontend sessions (admin only)"""
    try:
        if not request.user.is_staff:
            return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)

        sessions_info = []
        for frontend_id, session_data in FRONTEND_SESSIONS.items():
            sessions_info.append({
                'frontendId': frontend_id,
                'createdAt': session_data['created_at'].isoformat(),
                'lastUsed': session_data['last_used'].isoformat(),
                'sessionKey': session_data['session_key'][:8] + '...',  # Only show first 8 chars
                'age_minutes': (timezone.now() - session_data['created_at']).total_seconds() / 60
            })

        return Response({
            'active_sessions': len(FRONTEND_SESSIONS),
            'sessions': sessions_info
        })

    except Exception as e:
        logger.error(f"Debug frontend sessions error: {str(e)}")
        return Response({'error': 'Debug failed'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Import all the existing views for backwards compatibility
from .views import (
    get_all_commands,
    get_all_devices,
    device_heartbeat,
    reconnect_device,
    generate_token,
    deregister_device,
    view_tokens,
    get_active_tokens,
    register_device,
    get_devices,
    get_device_capabilities,
    get_action_parameters,
    execute_command,
    get_command_status,
    update_command_status,
    get_device_commands,
    get_server_public_key,
    get_pending_commands
)

# Re-export everything for convenience
__all__ = [
    # Encrypted endpoints
    'establish_frontend_session',
    'execute_command_encrypted',
    'get_command_status_encrypted',
    'get_frontend_session_info',
    'cleanup_frontend_sessions',
    'debug_frontend_sessions',

    # Original endpoints
    'get_all_commands',
    'get_all_devices',
    'device_heartbeat',
    'reconnect_device',
    'generate_token',
    'deregister_device',
    'view_tokens',
    'get_active_tokens',
    'register_device',
    'get_devices',
    'get_device_capabilities',
    'get_action_parameters',
    'execute_command',
    'get_command_status',
    'update_command_status',
    'get_device_commands',
    'get_server_public_key',
    'get_pending_commands'
]