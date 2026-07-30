from django_ratelimit.decorators import ratelimit
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.permissions import AllowAny
from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.http import JsonResponse
from django.utils import timezone
from django.db import connections
from django.db.utils import OperationalError
from .models import MachineType, Fault, Solution, SymptomKeyword, DiagnosisHistory
from.serializers import (
    MachineTypeSerializer, FaultSerializer, SolutionSerializer, DiagnosisRequestSerializer, DignosisHistorySerializer
)
from .services import FaultMatcher

# Create your views here.
class MachineTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """View for listing machine types"""
    queryset = MachineType.objects.all()
    serializer_class = MachineTypeSerializer
    permission_classes = [AllowAny]

class FaultViewSet(viewsets.ReadOnlyModelViewSet):
    """View for listing faults with optional filtering"""
    queryset = Fault.objects.all()
    serializer_class = FaultSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        """Filter faults by machine type id provided"""
        queryset = super().get_queryset()
        machine_type = self.request.query_params.get('machine_type')
        if machine_type:
            queryset = queryset.filter(machine_type__name__iexact=machine_type)
        return queryset

class SolutionViewSet(viewsets.ReadOnlyModelViewSet):
    """View for listing solutions"""
    queryset = Solution.objects.all()
    serializer_class = SolutionSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        """Filter solutions by fault if provided"""
        queryset = super().get_queryset()
        fault_id = self.request.query_params.get('fault')
        if fault_id:
            queryset = queryset.filter(fault_id=fault_id)
        return queryset

class DiagnosisViewSet(viewsets.GenericViewSet):
    permission_classes = [AllowAny]
    
    @method_decorator(csrf_exempt)
    @action(detail=False, methods=['post'])
    @ratelimit(key='ip', rate='10/m', method='POST', block=True)  # ← Add this
    def diagnose(self, request):
        """
        Diagnose a mechanical fault based on symptom description.
        """
        # Validate input
        serializer = DiagnosisRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'error': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        symptoms = serializer.validated_data['symptoms']
        machine_type = serializer.validated_data.get('machine_type')

        # Find Matching faults
        matcher = FaultMatcher(symptoms, machine_type)
        results = matcher.match()

        if not results:
            return Response({
                'message': 'No matching faults found. Try different keywords.', 'results': []
            })

        # Store diagnosis for analytics
        if request.user.is_authenticated:
            DiagnosisHistory.objects.create(
                user=request.user,
                symptoms=symptoms,
                suggested_fault=results[0]['fault'],
                confidence_score=results[0]['confidence'],
                ip_address=request.META.get('REMOTE_ADDR')
            )

        # Format response
        response_data = {
            'results': [
                {
                    'fault': FaultSerializer(result['fault']).data,
                    'confidence': f"{result['confidence'] * 100:.1f}%",
                    'matched_keywords': result['matches']
                }
                for result in results[:5]  #Return top 5 matches
            ]
        }

        return Response(response_data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def health(self, request):
        """Health check endpoint for monitoring"""
        db_status = 'ok'
        try:
            connections['default'].cursor()
        except OperationalError:
            db_status = 'error' 

        return JsonResponse({
            'status': 'healthy' if db_status == 'ok' else 'unhealthy',
            'database': db_status,
            'timestamp': timezone.now().isoformat(),
        })   

    @action(detail=False, methods=['get'])
    def history(self, request):
        """Get diagnosis history for the current user"""
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        history = DiagnosisHistory.objects.filter(
            user=request.user
        ).order_by('-created_at')[:20]
        
        data = []
        for entry in history:
            data.append({
                'id': entry.id,
                'symptoms': entry.symptoms,
                'fault': entry.suggested_fault.name if entry.suggested_fault else 'Unknown',
                'confidence': entry.confidence_score,
                'created_at': entry.created_at.isoformat(),
            })
        
        return Response(data)
    def rate_limit_exceeded(request, exception):
        """Custom response when rate limit is exceeded"""
        from django.http import JsonResponse
        return JsonResponse({
            'error': 'Too many requests. Please wait before trying again.'
        }, status=429)