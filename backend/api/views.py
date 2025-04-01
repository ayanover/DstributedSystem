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