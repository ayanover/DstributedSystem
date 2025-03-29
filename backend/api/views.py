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
    print(data)
    message = 'success'

    form = SignupForm({
        'email': data.get('email'),
        'name': data.get('name'),
        'password1': data.get('password1'),
        'password2': data.get('password2'),
    })

    if form.is_valid():
        form.save()

    else:
        print(form.errors)
        message = 'error'

    return JsonResponse({'message':message})