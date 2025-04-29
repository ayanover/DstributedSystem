import uuid
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone

class CustomUserManager(BaseUserManager):
    def _create_user(self, name, email, password, **extra_fields):
        if not email:
            raise ValueError("You have not provided a valid e-mail address")

        email = self.normalize_email(email)
        user = self.model(email=email, name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_user(self, name=None, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(name, email, password, **extra_fields)

    def create_superuser(self, name=None, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(name, email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(blank=True, null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

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

    @classmethod
    def create_defaults(cls):
        """Create default parameters for known actions"""
        defaults = {
            'execute_code': {
                'parameters': [
                    {"name": "code", "type": "string", "required": True}
                ],
                'description': "Execute Python code on the device"
            },
            'execute_code_with_input': {
                'parameters': [
                    {"name": "code", "type": "string", "required": True},
                    {"name": "input_data", "type": "string", "required": True}
                ],
                'description': "Execute Python code with input data on the device"
            },
            'factorial': {
                'parameters': [
                    {"name": "num1", "type": "number", "required": True}
                ],
                'description': "Calculate factorial of a number"
            },
            'add': {
                'parameters': [
                    {"name": "num1", "type": "number", "required": True},
                    {"name": "num2", "type": "number", "required": True}
                ],
                'description': "Add two numbers"
            },
            'subtract': {
                'parameters': [
                    {"name": "num1", "type": "number", "required": True},
                    {"name": "num2", "type": "number", "required": True}
                ],
                'description': "Subtract the second number from the first"
            },
            'multiply': {
                'parameters': [
                    {"name": "num1", "type": "number", "required": True},
                    {"name": "num2", "type": "number", "required": True}
                ],
                'description': "Multiply two numbers"
            },
            'divide': {
                'parameters': [
                    {"name": "num1", "type": "number", "required": True},
                    {"name": "num2", "type": "number", "required": True}
                ],
                'description': "Divide the first number by the second"
            },
            'power': {
                'parameters': [
                    {"name": "num1", "type": "number", "required": True},
                    {"name": "num2", "type": "number", "required": True}
                ],
                'description': "Raise the first number to the power of the second"
            },
            'modulo': {
                'parameters': [
                    {"name": "num1", "type": "number", "required": True},
                    {"name": "num2", "type": "number", "required": True}
                ],
                'description': "Calculate the remainder of dividing the first number by the second"
            }
        }

        for action_name, data in defaults.items():
            cls.objects.get_or_create(
                action_name=action_name,
                defaults={
                    'parameters': data['parameters'],
                    'description': data['description']
                }
            )


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