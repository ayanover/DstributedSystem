from django.db import models
import uuid


class AuthorizationToken(models.Model):
    """One-time tokens for device registration"""
    token = models.CharField(max_length=64, primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    created_by = models.CharField(max_length=255, null=True, blank=True)

    @property
    def is_valid(self):
        from django.utils import timezone
        return not self.is_used and self.expires_at > timezone.now()

    def __str__(self):
        return f"Token: {self.token[:10]}... ({'Valid' if self.is_valid else 'Invalid'})"


class Device(models.Model):
    """Connected device information"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    device_id = models.CharField(max_length=64, unique=True)
    device_type = models.CharField(max_length=50)
    public_key = models.TextField()
    session_key = models.CharField(max_length=128)
    capabilities = models.JSONField(default=list)
    metadata = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)
    registered_at = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.device_type} ({self.device_id})"


class ActionParameter(models.Model):
    """Parameters required for specific actions"""
    action_name = models.CharField(max_length=50, primary_key=True)
    parameters = models.JSONField(default=list)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Action: {self.action_name}"


class Command(models.Model):
    """Commands sent to devices"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='commands')
    name = models.CharField(max_length=50)
    params = models.JSONField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    result = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} on {self.device.device_type} ({self.status})"