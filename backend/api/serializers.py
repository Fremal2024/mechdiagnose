from django.contrib.auth.models import User
import bleach
from rest_framework import serializers
from .models import MachineType, Fault, Solution, SymptomKeyword, DiagnosisHistory


class SolutionSerializer(serializers.ModelSerializer):
    """Serializers solution data"""
    class Meta:
        model = Solution
        fields = '__all__'

class FaultSerializer(serializers.ModelSerializer):
    """Serializers fault data with nested solutions"""
    solutions = SolutionSerializer(many=True, read_only=True)
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)

    class Meta:
        model = Fault
        fields = '__all__'

class MachineTypeSerializer(serializers.ModelSerializer):
    """Serializes machine type with nested faults"""
    faults = FaultSerializer(many=True, read_only=True)

    class Meta:
        model = MachineType
        fields = '__all__'

class SymptomKeywordSerializer(serializers.ModelSerializer):
    """Serializers symptom keywords"""

    class Meta:
        model = SymptomKeyword
        fields = '__all__'

class DiagnosisRequestSerializer(serializers.Serializer):  
    symptoms = serializers.CharField(max_length=1000)
    machine_type = serializers.CharField(max_length=100, required=False, allow_blank=True)

    def validate_symptoms(self, value):
        return bleach.clean(value, tags=[], strip=True)

class DignosisHistorySerializer(serializers.ModelSerializer):
    """Serializes diagnosis history"""

    class Meta:
        model = DiagnosisHistory
        fields = '__all__'
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']