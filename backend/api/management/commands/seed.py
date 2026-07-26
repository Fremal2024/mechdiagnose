from django.core.management.base import BaseCommand
from api.models import MachineType, Fault, Solution, SymptomKeyword


class Command(BaseCommand):
    help = 'Seed the database with initial mechanical fault data'


    def handle(self, *args, **options):
        self.stdout.write('Seeding database....')

        #1. Engine Faults

        engine, created = MachineType.objects.get_or_create(
            name='Engine',
            defaults={'description': 'Internal combustion engines, diesel engines, and their components'}
        )

        #Faults: Engine Knocking

        knocking = Fault.objects.create(
            machine_type = engine,
            name='Engine knocking',
            description='A knocking or pinging sound from the engine during operation',
            symptoms='A knocking sound, loss of power, rough idle, engine vibration',
            severity='HIGH'
        )

        Solution.objects.create(
            fault=knocking,
            title='Check and adjust ignition timing',
            description='Incorrect ignition timing can cause kocking',
            steps='1. Connect timing light\n2. Check timing marks on cranckshaft pulley\n3. Adjust distributor as needed/n4. Recheck timing aafteradjustment',
            tools_required='Timing light, wrench set',
            estimated_time='1 hour',
            difficulty='MEDIUM'
        )

        Solution.objects.create(
            fault=knocking,
            title='Fuel Quality Check',
            description='Low octane fuel can cause kocking',
            steps='1. Check fuel type and quality\n2. Drain and replace with higher octane fuel\n3. Test drive',
            tools_required='Fuel container, fuel pump',
            estimated_time='30 minutes',
            difficulty='EASY'
        )

        #Keywords for engine knocking

        for kw in ['knock', 'knocking', 'ping', 'detonation', 'pre-ignition']:
            SymptomKeyword.objects.create(keyword=kw, fault=knocking, weight=2)

        #Fault: Overheating

        overheating = Fault.objects.create(
            machine_type=engine,
            name='Engine overheating',
            description='Engine temperature exceeds normal operating range',
            symptoms='Temperature gauge high, steam from hood, coolant warning light',
            severity='Critical'
        )

        Solution.objects.create(
            fault=overheating,
            title='Coolant System Check',
            description='Check coolant level and condition',
            steps='1. Wait for engine to cool\n2. Check coolant level in reservior\n3. Inspect for leaks\n4. Chec coolant mixture ratio',
            tools_required='Coolant teaser, funnel',
            estimated_time='30 minutes',
            difficulty='EASY'
        )
        for kw in ['overheat', 'steem', 'overheating', 'hot', 'temperature', 'coolant']:
            SymptomKeyword.objects.create(keyword=kw, fault=overheating, weight=2)

        #2. Pump Faults
        
        pump = MachineType.objects.create(
            name='Pump',
            description='Centrifugal, reciprocating, and other types of pumps'
        )

        #Fault: Pump Cavitation

        cavitation = Fault.objects.create(
            machine_type=pump,
            name='Pump Cavitation',
            description='Formation of vapor bubbles in the pump due to low pressure',
            symptoms='Noise from pump, reduced flow, vibration, pump damage',
            severity='HIGH'
        )

        Solution.objects.create(
            fault=cavitation,
            title='Check Suction Conditions',
            description='Ensure proper NPSH (Net Positive Suction Head)',
            steps='1. Check suction pressure\n2. Inspect suction pipe size\n3. Check for blockages\n4. Verify fluid temperature',
            tools_required='Pressure gauge',
            estimated_time='1 hour',
            difficulty='HARD'
        )

        for kw in ['cavitation', 'noise', 'vibration', 'flow reduction']:
            SymptomKeyword.objects.create(keyword=kw, fault=cavitation)

        self.stdout.write(self.style.SUCCESS('Database seeded successfully!'))