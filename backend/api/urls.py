from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

urlpatterns = [
    path('me/', views.me, name='me'),
    path('register/', views.register, name='register'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('server-key/', views.get_server_public_key, name='server_key'),
    path('register-device/', views.register_device, name='register_device'),
    path('reconnect-device/', views.reconnect_device, name='reconnect_device'),  # For reconnecting devices
    path('devices/<str:device_id>/deregister/', views.deregister_device, name='deregister_device'),
    path('devices/<str:device_id>/pending-commands/', views.get_pending_commands, name='get_pending_commands'),
    path('commands/<uuid:command_id>/update/', views.update_command_status, name='update_command_status'),

    # New endpoint for all commands history
    path('commands/all/', views.get_all_commands, name='get_all_commands'),

    # Protected endpoints (for web UI)
    path('tokens/generate/', views.generate_token, name='generate_token'),
    path('tokens/active/', views.get_active_tokens, name='get_active_tokens'),
    path('tokens/list/', views.view_tokens, name='view_tokens'),
    path('devices/', views.get_devices, name='get_devices'),
    path('devices/<str:device_id>/capabilities/', views.get_device_capabilities, name='get_device_capabilities'),
    path('devices/<str:device_id>/commands/', views.get_device_commands, name='get_device_commands'),
    path('actions/<str:action_name>/parameters/', views.get_action_parameters, name='get_action_parameters'),
    path('execute-command/', views.execute_command, name='execute_command'),
    path('commands/<uuid:command_id>/status/', views.get_command_status, name='get_command_status'),

    # Alternative paths (looks like your URLs have some duplicates)
    path('devices', views.get_devices, name='get_devices_alt'),
    path('devices/<str:device_id>/capabilities', views.get_device_capabilities, name='get_device_capabilities_alt'),
    path('devices/<str:device_id>/commands', views.get_device_commands, name='get_device_commands_alt'),
    path('actions/<str:action_name>/parameters', views.get_action_parameters, name='get_action_parameters_alt'),
    path('execute-command', views.execute_command, name='execute_command_alt'),
    path('commands/<uuid:command_id>', views.get_command_status, name='get_command_status_alt'),
    path('devices/<str:device_id>/pending-commands', views.get_pending_commands, name='get_pending_commands_alt'),
    path('commands/<uuid:command_id>/update', views.update_command_status, name='update_command_status_alt'),
    path('devices/<str:device_id>/deregister', views.deregister_device, name='deregister_device_alt'),

    # Admin paths
    path('admin/generate-token', views.generate_token, name='generate_token_alt'),
    path('admin/tokens', views.get_active_tokens, name='get_active_tokens_alt'),
    path('server-key', views.get_server_public_key, name='get_server_public_key_alt'),
path('devices/<str:device_id>/heartbeat/', views.device_heartbeat, name='device_heartbeat'),
# Add to your urlpatterns in urls.py
path('devices/all/', views.get_all_devices, name='get_all_devices'),
]