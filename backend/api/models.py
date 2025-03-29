from django.db import models
import uuid
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager
from django.utils import timezone

class IoTDevice(models.Model):
    name = models.CharField(max_length=100)
    device_id = models.CharField(max_length=50, unique=True)
    user = models.ForeignKey(User, related_name='devices', on_delete=models.CASCADE)
    status = models.CharField(max_length=50, default='inactive')

    def __str__(self):
        return self.name

class Task(models.Model):
    task_id = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    assigned_device = models.ForeignKey(IoTDevice, related_name='tasks', on_delete=models.CASCADE)
    status = models.CharField(max_length=50, choices=[('assigned', 'Assigned'), ('completed', 'Completed')], default='assigned')

    def __str__(self):
        return self.task_id

class CalculationResult(models.Model):
    task = models.OneToOneField(Task, related_name='result', on_delete=models.CASCADE)
    result = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class CustomUserManager(UserManager):
        def _create_user(self, name, email, password, extra_fields):
            if not email:
                raise ValueError("You have not provided a valid e-mail address")

            email = self.normalize_email(email)
            user = self.model(email=email, name=name, extra_fields)
            user.set_password(password)
            user.save(using=self._db)

            return user

        def create_user(self, name=None, email=None, password=None, extra_fields):
            extra_fields.setdefault('is_superuser', False)
            return self._create_user(name, email, password, extra_fields)

        def create_superuser(self, name=None, email=None, password=None, extra_fields):
            extra_fields.setdefault('is_superuser', True)
            return self._create_user(name, email, password, extra_fields)

    class User(AbstractBaseUser, PermissionsMixin):
        id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
        email = models.EmailField(unique=True)
        name = models.CharField(max_length=255, blank=True, null=True)
        is_active = models.BooleanField(default=True)
        is_superuser = models.BooleanField(default=False)
        date_joined = models.DateTimeField(default=timezone.now)
        last_login = models.DateTimeField(blank=True, null=True)

        objects = CustomUserManager()

        USERNAME_FIELD = 'email'
        EMAIL_FIELD = 'email'
        REQUIRED_FIELDS = []

    def __str__(self):
        return f"Result for {self.task.task_id}"
