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
    path('devices/<str:device_id>/deregister/', views.deregister_device, name='deregister_device'),
    path('devices/<str:device_id>/pending-commands/', views.get_pending_commands, name='get_pending_commands'),
    path('commands/<uuid:command_id>/update/', views.update_command_status, name='update_command_status'),

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
    path('devices', views.get_devices, name='get_devices'),
    path('devices/<str:device_id>/capabilities', views.get_device_capabilities, name='get_device_capabilities'),
    path('devices/<str:device_id>/commands', views.get_device_commands, name='get_device_commands'),

    path('actions/<str:action_name>/parameters', views.get_action_parameters, name='get_action_parameters'),

    path('execute-command', views.execute_command, name='execute_command'),
    path('commands/<uuid:command_id>', views.get_command_status, name='get_command_status'),

    path('register-device/', views.register_device, name='register_device'),
    path('devices/<str:device_id>/pending-commands', views.get_pending_commands, name='get_pending_commands'),
    path('commands/<uuid:command_id>/update', views.update_command_status, name='update_command_status'),

    path('admin/generate-token', views.generate_token, name='generate_token'),
    path('admin/tokens', views.get_active_tokens, name='get_active_tokens'),
    path('server-key', views.get_server_public_key, name='get_server_public_key'),

    path('devices/<str:device_id>/deregister', views.deregister_device, name='deregister_device'),
]
