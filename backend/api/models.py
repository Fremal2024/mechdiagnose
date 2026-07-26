from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class MachineType(models.Model):
    """Categories of machines (Engine, Pump Compressot, etc.)"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    image = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Fault(models.Model):
    """Mechanical faults with severity levels"""
    SEVERITY_CHOICES =[
        ('LOW', 'Low - Regular Maintenance'),
        ('MEDIUM', 'Medium - Plan Repair'),
        ('HIGH', 'High - Immediate Attention'),
        ('CRITICAL', 'Critical - Stop Machine'),
    ]

    machine_type = models.ForeignKey(
        MachineType,
        on_delete=models.CASCADE,
        related_name='faults'
    )
    name = models.CharField(max_length=200)
    description = models.TextField()
    symptoms = models.TextField(help_text="Common symptoms for this fault")
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, default='MEDIUM')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.machine_type.name})"

    class Meta:
        ordering = ['-severity', 'name']

class Solution(models.Model):
    """Repair/maintenance solutions for each fault"""
    DIFFICULTY_CHOICES = [
        ('EASY', 'Easy'),
        ('MEDIUM', 'Medium'),
        ('HARD', 'Hard'),
        ('EXPERT', 'Expert'),
    ]

    fault = models.ForeignKey(
        Fault,
        on_delete=models.CASCADE,
        related_name='solutions'
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    steps = models.TextField(help_text="Step-by-step instructions")
    tools_required = models.TextField(blank=True)
    estimated_time = models.CharField(max_length=50) # For example, 2 hours
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='MEDIUM')
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"Solution: {self.title}"


class SymptomKeyword(models.Model):
    """Keywords that help match user input to faults"""
    keyword = models.CharField(max_length=100, unique=True)
    fault = models.ForeignKey(
        Fault,
        on_delete=models.CASCADE,
        related_name='keywords'
    )
    weight = models.IntegerField(default=1) # The higher the weight the more import it is


    def __str__(self):
        return self.keyword


class DiagnosisHistory(models.Model):
    """Track user diagnosis attempts for analytics and improvement"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    symptoms = models.TextField()
    suggested_fault = models.ForeignKey(Fault, on_delete=models.SET_NULL, null=True)
    confidence_score = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)


    def __str__(self):
        return f"Diagnosis at {self.created_at}"
    