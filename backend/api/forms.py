from django.contrib.auth.forms import UserCreationForm

from .models import User


class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = {'email', 'name', 'position', 'birth_date', 'password1', 'password2'}