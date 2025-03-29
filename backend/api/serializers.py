from rest_framework import serializers
from .models import IoTDevice, Task, CalculationResult

class IoTDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = IoTDevice
        fields = '__all__'

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'

class CalculationResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = CalculationResult
        fields = '__all__'
