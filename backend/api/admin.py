from django.contrib import admin
from .models import MachineType, Fault, Solution, SymptomKeyword, DiagnosisHistory

# Register your models here.
@admin.register(MachineType)
class MachineTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name', 'description']


@admin.register(Fault)
class FaultAdmin(admin.ModelAdmin):
    list_display = ['name', 'machine_type', 'severity', 'created_at']
    list_filter = ['machine_type', 'severity']
    search_fields = ['name', 'description', 'symptoms']

@admin.register(Solution)
class SolutionAdmin(admin.ModelAdmin):
    list_display = ['title', 'fault', 'difficulty', 'estimated_time']
    list_filter = ['fault', 'difficulty']

@admin.register(SymptomKeyword)
class SymptomKeywordAdmin(admin.ModelAdmin):
    list_display = ['keyword', 'fault', 'weight']
    list_filter = ['fault']

@admin.register(DiagnosisHistory)
class DiagnosisHistoryAdmin(admin.ModelAdmin):
    list_display = ['created_at', 'user', 'suggested_fault', 'confidence_score']
    list_filter = ['created_at', 'suggested_fault']