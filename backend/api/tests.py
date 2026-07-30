from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from .models import MachineType, Fault, Solution, SymptomKeyword
from .services import FaultMatcher

# Create your tests here.
class MachineTypeTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.machine = MachineType.objects.create(
            name='Test Engine',
            description='Test description'
        )

    def test_machine_type_creation(self):
        self.assertEqual(self.machine.name, 'Test Engine')
        self.assertEqual(str(self.machine), 'Test Engine')

    def test_api_machines_list(self):
        response = self.client.get('/api/machines/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


class FaultTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.machine = MachineType.objects.create(
            name='Test Engine',
            description='Test description'
        )
        self.fault = Fault.objects.create(
            machine_type=self.machine,
            name='Test Fault',
            description='Test description',
            symptoms='Test symptoms',
            severity='HIGH'
        )

    def test_fault_creation(self):
        self.assertEqual(self.fault.name, 'Test Fault')
        self.assertEqual(str(self.fault), 'Test Fault (Test Engine)')

    def test_api_faults_list(self):
        response = self.client.get('/api/faults/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


class SolutionTests(TestCase):
    def setUp(self):
        self.machine = MachineType.objects.create(
            name='Test Engine',
            description='Test description'
        )
        self.fault = Fault.objects.create(
            machine_type=self.machine,
            name='Test Fault',
            description='Test description',
            symptoms='Test symptoms',
            severity='HIGH'
        )
        self.solution = Solution.objects.create(
            fault=self.fault,
            title='Test Solution',
            description='Test description',
            steps='Step 1\nStep 2',
            tools_required='Wrench',
            estimated_time='1 hour',
            difficulty='MEDIUM'
        )

    def test_solution_creation(self):
        self.assertEqual(self.solution.title, 'Test Solution')
        self.assertEqual(str(self.solution), 'Solution: Test Solution')


class FaultMatcherTests(TestCase):
    def setUp(self):
        self.machine = MachineType.objects.create(
            name='Engine',
            description='Test description'
        )
        self.fault = Fault.objects.create(
            machine_type=self.machine,
            name='Engine Knocking',
            description='Knocking sound from engine',
            symptoms='Knocking sound, loss of power',
            severity='HIGH'
        )
        SymptomKeyword.objects.create(keyword='knock', fault=self.fault, weight=2)
        SymptomKeyword.objects.create(keyword='knocking', fault=self.fault, weight=2)

    def test_exact_match(self):
        matcher = FaultMatcher('engine knocking')
        results = matcher.match()
        self.assertTrue(len(results) > 0)
        self.assertEqual(results[0]['fault'].name, 'Engine Knocking')
        self.assertGreater(results[0]['confidence'], 0)

    def test_partial_match(self):
        matcher = FaultMatcher('knock')
        results = matcher.match()
        self.assertTrue(len(results) > 0)
        self.assertEqual(results[0]['fault'].name, 'Engine Knocking')

    def test_no_match(self):
        matcher = FaultMatcher('nothing related')
        results = matcher.match()
        self.assertEqual(len(results), 0)


class DiagnosisAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.machine = MachineType.objects.create(
            name='Engine',
            description='Test description'
        )
        self.fault = Fault.objects.create(
            machine_type=self.machine,
            name='Engine Knocking',
            description='Knocking sound from engine',
            symptoms='Knocking sound, loss of power',
            severity='HIGH'
        )
        SymptomKeyword.objects.create(keyword='knock', fault=self.fault, weight=2)

    def test_diagnosis_endpoint(self):
        response = self.client.post(
            '/api/diagnose/diagnose/',
            {'symptoms': 'engine knocking'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data['results'])