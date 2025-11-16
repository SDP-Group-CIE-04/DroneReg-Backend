from rest_framework import serializers
from registry.models import Activity, Authorization, Operator, Contact, Aircraft, Pilot, Address, Person, Test, TypeCertificate, Manufacturer, RIDModule


class AddressSerializer(serializers.ModelSerializer):
    address_line_2 = serializers.CharField(required=False, allow_blank=True, default='-')
    address_line_3 = serializers.CharField(required=False, allow_blank=True, default='-')
    postcode = serializers.CharField(required=False, allow_blank=True, default='0')

    class Meta:
        model = Address
        fields = ('id', 'address_line_1','address_line_2', 'address_line_3', 'postcode','city', 'country','created_at','updated_at')
    
    def validate(self, attrs):
        # Convert empty strings to defaults
        if 'address_line_2' in attrs and not attrs['address_line_2']:
            attrs['address_line_2'] = '-'
        if 'address_line_3' in attrs and not attrs['address_line_3']:
            attrs['address_line_3'] = '-'
        if 'postcode' in attrs and not attrs['postcode']:
            attrs['postcode'] = '0'
        return attrs

class TypeCertificateSerializer(serializers.ModelSerializer):

    class Meta:
        model = TypeCertificate
        fields = ('id', 'type_certificate_id','type_certificate_issuing_country', 'type_certificate_holder','type_certificate_holder_country', )

class PersonSerializer(serializers.ModelSerializer):

    class Meta:
        model = Person
        fields = ('id', 'first_name','middle_name', 'last_name', 'email', 'phone_number', 'date_of_birth', 'created_at','updated_at')

class PersonCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = ('first_name', 'middle_name', 'last_name', 'email', 'phone_number', 'date_of_birth')

class TestsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Test
        fields = ('id', 'test_type','taken_at', 'name','created_at','updated_at')

class OperatorSerializer(serializers.ModelSerializer):
    ''' This is the default serializer for Operator '''
    class Meta:
        model = Operator
        fields = ('id', 'company_name', 'website', 'email', 'phone_number')

class OperatorCreateSerializer(serializers.ModelSerializer):
    ''' Serializer for creating a new operator '''
    address = AddressSerializer()
    phone_number = serializers.CharField(required=False, allow_blank=True, max_length=17)
    
    class Meta:
        model = Operator
        fields = ('company_name', 'website', 'email', 'phone_number', 
                  'operator_type', 'address', 'vat_number', 
                  'insurance_number', 'company_number', 'country')
    
    def validate_phone_number(self, value):
        """Validate phone number format if provided"""
        if value:
            import re
            phone_regex = r'^\+?1?\d{9,15}$'
            if not re.match(phone_regex, value):
                raise serializers.ValidationError(
                    "Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
                )
        return value
    
    def create(self, validated_data):
        address_data = validated_data.pop('address')
        address = Address.objects.create(**address_data)
        operator = Operator.objects.create(address=address, **validated_data)
        return operator


class PrivilagedOperatorSerializer(serializers.ModelSerializer):
    ''' This is the privilaged serializer for Operator specially for law enforcement and other privilaged operators '''
    authorized_activities = serializers.SerializerMethodField()
    operational_authorizations = serializers.SerializerMethodField()
    address = AddressSerializer(read_only=True)
   
    def get_authorized_activities(self, response):
        activities = []
        o = Operator.objects.get(id=response.id)
        oa = o.authorized_activities.all()
        for activity in oa: 
            activities.append(activity.name)
        return activities

    def get_operational_authorizations(self, response):
        authorizations = []
        o = Operator.objects.get(id=response.id)
        oa = o.operational_authorizations.all()
        for authorization in oa: 
            authorizations.append(authorization.title)
        return authorizations


    class Meta:
        model = Operator
        fields = ('id', 'company_name', 'website', 'email', 'operator_type', 'address', 'operational_authorizations', 'authorized_activities', 'created_at', 'updated_at')


class ContactSerializer(serializers.ModelSerializer):
    person = PersonSerializer(read_only=True)
    operator = OperatorSerializer(read_only=True)
    class Meta:
        model = Contact
        fields = ('id', 'operator','person','role_type', 'updated_at')

class ContactCreateSerializer(serializers.ModelSerializer):
    ''' Serializer for creating a new contact '''
    person = PersonCreateSerializer()
    address = AddressSerializer()
    
    class Meta:
        model = Contact
        fields = ('operator', 'role_type', 'person', 'address')
    
    def create(self, validated_data):
        person_data = validated_data.pop('person')
        address_data = validated_data.pop('address')
        
        person = Person.objects.create(**person_data)
        address = Address.objects.create(**address_data)
        
        contact = Contact.objects.create(
            person=person,
            address=address,
            **validated_data
        )
        return contact

class PilotSerializer(serializers.ModelSerializer):
    person = PersonSerializer(read_only=True)
    operator = OperatorSerializer(read_only=True)
    tests = TestsSerializer(read_only=True)
    class Meta:
        model = Pilot
        fields = ('id', 'operator','is_active','tests', 'person','updated_at')

class PilotCreateSerializer(serializers.ModelSerializer):
    ''' Serializer for creating a new pilot '''
    person = PersonCreateSerializer()
    address = AddressSerializer()
    
    class Meta:
        model = Pilot
        fields = ('operator', 'is_active', 'person', 'address')
    
    def create(self, validated_data):
        person_data = validated_data.pop('person')
        address_data = validated_data.pop('address')
        
        person = Person.objects.create(**person_data)
        address = Address.objects.create(**address_data)
        
        pilot = Pilot.objects.create(
            person=person,
            address=address,
            **validated_data
        )
        return pilot

class AircraftSerializer(serializers.ModelSerializer):
    type_certificate = TypeCertificateSerializer(read_only= True)
    class Meta:
        model = Aircraft
        fields = ('id', 'mass', 'manufacturer', 'model','esn','maci_number','status','registration_mark', 'sub_category','type_certificate', 'created_at','master_series', 'series','popular_name','manufacturer','registration_mark','sub_category', 'icao_aircraft_type_designator', 'max_certified_takeoff_weight','updated_at')
        
        

class AircraftCreateSerializer(serializers.ModelSerializer):
    ''' Serializer for creating a new aircraft '''
    type_certificate = TypeCertificateSerializer(required=False, allow_null=True)
    registration_mark = serializers.CharField(required=False, allow_blank=True, max_length=10)
    icao_aircraft_type_designator = serializers.CharField(required=False, allow_blank=True, max_length=4, default='0000')
    manufacturer = serializers.PrimaryKeyRelatedField(queryset=Manufacturer.objects.all(), required=False, allow_null=True)
    
    class Meta:
        model = Aircraft
        fields = ('operator', 'mass', 'manufacturer', 'model', 'esn', 'maci_number',
                 'registration_mark', 'category', 'sub_category', 'is_airworthy',
                 'icao_aircraft_type_designator', 'max_certified_takeoff_weight', 'status',
                 'type_certificate', 'master_series', 'series', 'popular_name')
    
    def validate_registration_mark(self, value):
        """Validate registration_mark length"""
        if value and len(value) > 10:
            raise serializers.ValidationError(f"Registration mark must be 10 characters or less. Received {len(value)} characters: '{value}'")
        return value
    
    def validate_icao_aircraft_type_designator(self, value):
        """Validate icao_aircraft_type_designator length"""
        if value and len(value) > 4:
            raise serializers.ValidationError(f"ICAO aircraft type designator must be 4 characters or less. Received {len(value)} characters: '{value}'")
        return value
    
    def create(self, validated_data):
        # Handle nested type_certificate
        type_certificate_data = validated_data.pop('type_certificate', None)
        type_certificate = None
        if type_certificate_data:
            type_certificate = TypeCertificate.objects.create(**type_certificate_data)
        
        # Handle missing or empty manufacturer
        if 'manufacturer' not in validated_data or not validated_data['manufacturer']:
            # Get the first manufacturer or create a default one if none exists
            manufacturers = Manufacturer.objects.all()
            if manufacturers.exists():
                validated_data['manufacturer'] = manufacturers.first()
            else:
                # Create a default address
                address = Address.objects.create(
                    address_line_1="Default Address",
                    address_line_2="",
                    address_line_3="",
                    postcode="00000",
                    city="Default City",
                    country="US"
                )
                # Create a default manufacturer
                validated_data['manufacturer'] = Manufacturer.objects.create(
                    full_name="Default Manufacturer",
                    common_name="Default",
                    address=address,
                    acronym="DEF",
                    role="Manufacturer",
                    country="US"
                )
        
        # Create the aircraft
        aircraft = Aircraft.objects.create(**validated_data)
        
        # Set type_certificate if it was created
        if type_certificate:
            aircraft.type_certificate = type_certificate
            aircraft.save()
        
        return aircraft

class AircraftESNSerializer(serializers.ModelSerializer):

    class Meta:
        model = Aircraft
        fields = ('id', 'mass', 'manufacturer', 'model','esn','maci_number','status','created_at','updated_at')
        lookup_field = 'esn'
        
        
class PrivilagedPilotSerializer(serializers.ModelSerializer):
    ''' This is the privilaged serializer for Pilot specially for law enforcement and other privilaged interested parties '''
    tests = serializers.SerializerMethodField()
    operator_id = serializers.SerializerMethodField()
	
    def get_tests(self, response):
        tests = []
        p = Pilot.objects.get(id=response.id)
        all_tests = p.tests.all()
        for test in all_tests: 
            tests.append(test.name)
        return tests

    class Meta:
        model = Pilot
        fields = ('id',  'operator', 'first_name','is_active', 'last_name', 'email','phone_number','tests', 'updated_at')


class PrivilagedContactSerializer(serializers.ModelSerializer):
    ''' This is the privilaged serializer for Contact model specially for law enforcement and other privilaged interested parties '''

    authorized_activities = serializers.SerializerMethodField()
    operational_authorizations = serializers.SerializerMethodField()

    def get_authorized_activities(self, response):
        activities = []
        c = Contact.objects.get(id =response.id)
        o = c.operator
        oa = o.authorized_activities.all()
        for activity in oa: 
            activities.append(activity.name)
        return activities

    def get_operational_authorizations(self, response):
        authorizations = []
        c = Contact.objects.get(id =response.id)
        o = c.operator
        oa = o.operational_authorizations.all()
        for authorization in oa: 
            authorizations.append(authorization.title)
        return authorizations

    class Meta:
        model = Contact
        fields = ('id', 'company_name', 'operator','website', 'email', 'operator_type', 'phone_number', 'address',
                  'postcode', 'city', 'operational_authorizations', 'authorized_activities', 'created_at', 'updated_at')

class ManufacturerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manufacturer
        fields = ('id', 'full_name', 'common_name', 'acronym', 'role', 'country')


class RIDModuleSerializer(serializers.ModelSerializer):
    """Serializer for RID Module list and detail views"""
    operator = OperatorSerializer(read_only=True)
    aircraft = AircraftSerializer(read_only=True)
    
    class Meta:
        model = RIDModule
        fields = (
            'id', 'rid_id', 'operator', 'aircraft', 'module_esn', 'module_port', 
            'module_type', 'status', 'activation_status', 'activated_at', 
            'last_seen_at', 'deactivated_at', 'created_at', 'updated_at', 
            'notes', 'firmware_version'
        )
        read_only_fields = ('id', 'rid_id', 'created_at', 'updated_at')


class RIDModuleCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new RID Module"""
    rid_id = serializers.UUIDField(required=False, help_text="RID ID (UUID v4). If not provided, will be generated.")
    module_port = serializers.CharField(required=False, allow_blank=True, max_length=50)
    notes = serializers.CharField(required=False, allow_blank=True)
    firmware_version = serializers.CharField(required=False, allow_blank=True, max_length=20)
    
    class Meta:
        model = RIDModule
        fields = (
            'rid_id', 'operator', 'aircraft', 'module_esn', 'module_port', 
            'module_type', 'status', 'activation_status', 'notes', 'firmware_version'
        )
    
    def validate_module_esn(self, value):
        """Validate module ESN is not empty"""
        if not value or not value.strip():
            raise serializers.ValidationError("Module ESN cannot be empty")
        return value.strip().upper()
    
    def create(self, validated_data):
        """Create RID module, generating RID ID if not provided"""
        import uuid as uuid_lib
        
        # Generate RID ID if not provided
        if 'rid_id' not in validated_data or not validated_data.get('rid_id'):
            validated_data['rid_id'] = uuid_lib.uuid4()
        
        # Set activated_at to now if not set
        if 'activated_at' not in validated_data:
            from django.utils import timezone
            validated_data['activated_at'] = timezone.now()
        
        return super().create(validated_data)
