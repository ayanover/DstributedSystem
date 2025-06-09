# urls.py - Merged configuration keeping your existing functionality + encryption
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views
from . import encrypted_views  # Import the new encrypted views

urlpatterns = [
    # Authentication endpoints (your existing JWT setup)
    path('me/', views.me, name='me'),
    path('register/', views.register, name='register'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Server public key (required for encryption)
    path('server-key/', views.get_server_public_key, name='server_key'),
    path('server-key', views.get_server_public_key, name='get_server_public_key_alt'),  # Your alt version

    # NEW: Frontend encryption endpoints
    path('establish-frontend-session/', encrypted_views.establish_frontend_session, name='establish_frontend_session'),
    path('execute-command-encrypted/', encrypted_views.execute_command_encrypted, name='execute_command_encrypted'),
    path('commands/<uuid:command_id>/status-encrypted/', encrypted_views.get_command_status_encrypted,
         name='command_status_encrypted'),
    path('frontend-session-info/', encrypted_views.get_frontend_session_info, name='frontend_session_info'),

    # NEW: Admin/Maintenance endpoints for encryption
    path('cleanup-frontend-sessions/', encrypted_views.cleanup_frontend_sessions, name='cleanup_frontend_sessions'),
    path('debug-frontend-sessions/', encrypted_views.debug_frontend_sessions, name='debug_frontend_sessions'),

    # Device registration and connection (your existing)
    path('register-device/', views.register_device, name='register_device'),
    path('reconnect-device/', views.reconnect_device, name='reconnect_device'),
    path('devices/<str:device_id>/deregister/', views.deregister_device, name='deregister_device'),
    path('devices/<str:device_id>/deregister', views.deregister_device, name='deregister_device_alt'),  # Your alt
    path('devices/<str:device_id>/heartbeat/', views.device_heartbeat, name='device_heartbeat'),

    # Device queries (your existing)
    path('devices/', views.get_devices, name='get_devices'),
    path('devices', views.get_devices, name='get_devices_alt'),  # Your alt version
    path('devices/all/', views.get_all_devices, name='get_all_devices'),
    path('devices/<str:device_id>/capabilities/', views.get_device_capabilities, name='get_device_capabilities'),
    path('devices/<str:device_id>/capabilities', views.get_device_capabilities, name='get_device_capabilities_alt'),
    # Your alt
    path('devices/<str:device_id>/commands/', views.get_device_commands, name='get_device_commands'),
    path('devices/<str:device_id>/commands', views.get_device_commands, name='get_device_commands_alt'),  # Your alt
    path('devices/<str:device_id>/pending-commands/', views.get_pending_commands, name='get_pending_commands'),
    path('devices/<str:device_id>/pending-commands', views.get_pending_commands, name='get_pending_commands_alt'),
    # Your alt

    # Command execution (your existing - non-encrypted)
    path('execute-command/', views.execute_command, name='execute_command'),
    path('execute-command', views.execute_command, name='execute_command_alt'),  # Your alt
    path('commands/<uuid:command_id>/status/', views.get_command_status, name='get_command_status'),
    path('commands/<uuid:command_id>', views.get_command_status, name='get_command_status_alt'),  # Your alt
    path('commands/<uuid:command_id>/update/', views.update_command_status, name='update_command_status'),
    path('commands/<uuid:command_id>/update', views.update_command_status, name='update_command_status_alt'),
    # Your alt
    path('commands/all/', views.get_all_commands, name='get_all_commands'),

    # Action parameters (your existing)
    path('actions/<str:action_name>/parameters/', views.get_action_parameters, name='get_action_parameters'),
    path('actions/<str:action_name>/parameters', views.get_action_parameters, name='get_action_parameters_alt'),
    # Your alt

    # Token management (your existing)
    path('tokens/generate/', views.generate_token, name='generate_token'),
    path('tokens/active/', views.get_active_tokens, name='get_active_tokens'),
    path('tokens/list/', views.view_tokens, name='view_tokens'),

    # Admin paths (your existing)
    path('admin/generate-token', views.generate_token, name='generate_token_alt'),
    path('admin/tokens', views.get_active_tokens, name='get_active_tokens_alt'),
]