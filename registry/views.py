import datetime
import json
import jwt

from datetime import datetime
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.template import loader
from django.utils import translation
from django.views.generic import TemplateView
from rest_framework import generics, mixins, status, viewsets
from rest_framework.authentication import (SessionAuthentication,
                                           TokenAuthentication)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.exceptions import ValidationError

from registry.models import Activity, Authorization, Contact, Operator, Aircraft, Pilot, Test, TestValidity, Person, Address, Manufacturer, RIDModule
from registry.serializers import (ContactSerializer, OperatorSerializer, PilotSerializer, 
                                  PrivilagedContactSerializer, PrivilagedPilotSerializer,
                                  PrivilagedOperatorSerializer, AircraftSerializer, AircraftESNSerializer,
                                  OperatorCreateSerializer, PilotCreateSerializer, 
                                  ContactCreateSerializer, AircraftCreateSerializer, ManufacturerSerializer,
                                  RIDModuleSerializer, RIDModuleCreateSerializer, RIDModuleRIDIDUpdateSerializer)
from django.http import JsonResponse
from rest_framework.decorators import api_view
from six.moves.urllib import request as req
from functools import wraps
from django.conf import settings
from registry.auth import requires_auth, requires_scope


class OperatorList(mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  generics.GenericAPIView):
    """
    List all operators, or create a new operator.
    """
    queryset = Operator.objects.all()
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return OperatorCreateSerializer
        return OperatorSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
    
    @requires_auth
    def post(self, request, *args, **kwargs):
        print("Received POST data:", request.data)
        # Create a mutable copy of request data
        # For JSON requests, request.data is already a dict
        # For form data, it might be a QueryDict
        import copy
        if hasattr(request.data, '_mutable'):
            # QueryDict - convert to regular dict
            data = {}
            for key, value in request.data.items():
                if isinstance(value, list) and len(value) == 1:
                    data[key] = value[0]
                else:
                    data[key] = value
            # Handle nested structures (like address)
            if 'address' in data and isinstance(data['address'], str):
                try:
                    import json
                    data['address'] = json.loads(data['address'])
                except (json.JSONDecodeError, TypeError):
                    pass
        else:
            # Already a dict, use deepcopy
            data = copy.deepcopy(dict(request.data))

        # Handle operator_type conversion
        if 'operator_type' in data:
            if isinstance(data['operator_type'], str):
                type_map = {'na': 0, 'luc': 1, 'non-luc': 2, 'auth': 3, 'dec': 4, 'private': 2}
                op_type = data['operator_type'].lower()
                if op_type in type_map:
                    data['operator_type'] = type_map[op_type]

        # Handle website format
        if 'website' in data and data['website']:
            original_website = data['website']
            if not data['website'].startswith(('http://', 'https://')):
                data['website'] = 'https://' + data['website']
            print(f"Website transformation: '{original_website}' -> '{data['website']}'", flush=True)
        
        # Handle phone number - normalize if it doesn't start with + or 1
        if 'phone_number' in data and data['phone_number']:
            phone = str(data['phone_number']).strip()
            # Remove any spaces or dashes
            phone = phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
            # If it doesn't start with + and is just digits, it should be valid
            # The regex allows: optional +, optional 1, then 9-15 digits
            # So numbers like '0585396050' should work, but let's ensure it's clean
            data['phone_number'] = phone

        # Handle address fields
        if 'address' in data:
            # Ensure address is a dict (not a QueryDict or other type)
            if not isinstance(data['address'], dict):
                addr_data = dict(data['address'])
            else:
                addr_data = data['address'].copy()
            
            # Convert line_1 to address_line_1 if needed
            if 'line_1' in addr_data and 'address_line_1' not in addr_data:
                addr_data['address_line_1'] = addr_data.pop('line_1')

            # Set default values for required address fields if missing
            if 'address_line_2' not in addr_data or not addr_data.get('address_line_2'):
                addr_data['address_line_2'] = '-'
            if 'address_line_3' not in addr_data or not addr_data.get('address_line_3'):
                addr_data['address_line_3'] = '-'
            
            # Ensure postcode has a default if missing
            if 'postcode' not in addr_data or not addr_data.get('postcode'):
                addr_data['postcode'] = '0'

            # Handle country code conversion
            if 'country' in addr_data:
                country_map = {
                    'uae': 'AE',
                    'united arab emirates': 'AE',
                    'usa': 'US',
                    'united states': 'US',
                    'uk': 'GB',
                    'united kingdom': 'GB'
                }
                country = str(addr_data['country']).lower()
                if country in country_map:
                    addr_data['country'] = country_map[country]
            
            # Update the address in data
            data['address'] = addr_data

        try:
            serializer = self.get_serializer(data=data)
            if not serializer.is_valid():
                error_details = dict(serializer.errors)
                print("DEBUG - Validation errors:", error_details, flush=True)
                print("Validation errors:", error_details)
                print("Processed data:", data, flush=True)
                
                # Format errors for better readability
                formatted_errors = {}
                for field, errors in error_details.items():
                    if isinstance(errors, list):
                        formatted_errors[field] = [str(e) for e in errors]
                    else:
                        formatted_errors[field] = [str(errors)]
                
                return Response({
                    'status': 'error',
                    'message': 'Validation failed',
                    'errors': formatted_errors,
                    'received_data': dict(request.data) if hasattr(request.data, 'dict') else request.data,
                    'processed_data': data,
                    'help': {
                        'operator_type': 'Must be one of: 0 (NA), 1 (LUC), 2 (Non-LUC/Private), 3 (AUTH), 4 (DEC)',
                        'website': 'Must include http:// or https://',
                        'phone_number': 'Must match format: +999999999 or 9999999999 (9-15 digits)',
                        'address': {
                            'required_fields': ['address_line_1', 'address_line_2', 'address_line_3', 'city', 'country', 'postcode'],
                            'country': 'Must be a valid ISO 3166 code (e.g., AE for UAE)'
                        }
                    }
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Create the operator using the validated serializer
            serializer.save()
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
            
        except ValidationError as e:
            # Handle DRF ValidationError
            print(f"ValidationError in operator creation: {str(e)}", flush=True)
            error_details = dict(e.detail) if hasattr(e, 'detail') else {'error': [str(e)]}
            formatted_errors = {}
            for field, errors in error_details.items():
                if isinstance(errors, list):
                    formatted_errors[field] = [str(e) for e in errors]
                else:
                    formatted_errors[field] = [str(errors)]
            
            return Response({
                'status': 'error',
                'message': 'Validation failed',
                'errors': formatted_errors,
                'processed_data': data
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"Exception in operator creation: {str(e)}", flush=True)
            import traceback
            print(traceback.format_exc(), flush=True)
            return Response({
                'status': 'error',
                'message': f'Server error: {str(e)}',
                'error_type': type(e).__name__
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class OperatorDetail(mixins.RetrieveModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.DestroyModelMixin,
                    generics.GenericAPIView):
    """
    Retrieve, update or delete a Operator instance.
    """
    queryset = Operator.objects.all()
    serializer_class = OperatorSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
    
    @requires_auth
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
    
    @requires_auth
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    @requires_auth
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class OperatorDetailPrivilaged(mixins.RetrieveModelMixin,
                    generics.GenericAPIView):
    """
    Retrieve operator with privileged details.
    """
    queryset = Operator.objects.all()
    serializer_class = PrivilagedOperatorSerializer

    @requires_scope('read:privileged')
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class OperatorAircraft(mixins.RetrieveModelMixin,
                    generics.GenericAPIView):
    """
    Retrieve aircraft for a specific operator.
    """
    queryset = Aircraft.objects.all()
    serializer_class = AircraftSerializer

    def get_Aircraft(self, pk):
        try:
            o = Operator.objects.get(id=pk)
        except Operator.DoesNotExist:
            raise Http404
        else: 
            return Aircraft.objects.filter(operator=o)

    def get(self, request, pk, format=None):
        aircraft = self.get_Aircraft(pk)
        serializer = AircraftSerializer(aircraft, many=True)
        return Response(serializer.data)


class AircraftList(mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  generics.GenericAPIView):
    """
    List all aircraft, or create a new aircraft.
    Supports filtering by operator via ?operator=<uuid> query parameter.
    """
    queryset = Aircraft.objects.all()
    
    def get_queryset(self):
        """
        Optionally filter aircraft by operator query parameter.
        Example: GET /api/v1/aircraft?operator=566d63bb-cb1c-42dc-9a51-baef0d0a8d04
        """
        queryset = Aircraft.objects.all()
        operator_id = self.request.query_params.get('operator', None)
        
        if operator_id:
            # Filter aircraft by operator UUID
            queryset = queryset.filter(operator_id=operator_id)
        
        return queryset
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AircraftCreateSerializer
        return AircraftSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
    
    @requires_auth
    def post(self, request, *args, **kwargs):
        print("Received POST data for aircraft:", request.data, flush=True)
        
        try:
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                error_details = dict(serializer.errors)
                print("DEBUG - Validation errors:", error_details, flush=True)
                print("Validation errors:", error_details)
                print("Received data:", dict(request.data) if hasattr(request.data, 'dict') else request.data, flush=True)
                
                # Format errors for better readability
                formatted_errors = {}
                for field, errors in error_details.items():
                    if isinstance(errors, list):
                        formatted_errors[field] = [str(e) for e in errors]
                    else:
                        formatted_errors[field] = [str(errors)]
                
                return Response({
                    'status': 'error',
                    'message': 'Validation failed',
                    'errors': formatted_errors,
                    'received_data': dict(request.data) if hasattr(request.data, 'dict') else request.data,
                    'help': {
                        'operator': 'Required. Must be a valid operator UUID.',
                        'mass': 'Required. Must be an integer (mass in kg).',
                        'manufacturer': 'Optional. If not provided, will use first available manufacturer or create a default one.',
                        'model': 'Optional. String (max 280 chars). Default: "GenericModel"',
                        'esn': 'Optional. String (max 48 chars). Auto-generated if not provided.',
                        'maci_number': 'Optional. String (max 280 chars). Auto-generated if not provided.',
                        'registration_mark': 'Optional. String (max 10 chars).',
                        'category': 'Optional. Integer: 0=Other, 1=AEROPLANE, 2=ROTORCRAFT, 3=Hybrid, 4=Ornithopter. Default: 0',
                        'sub_category': 'Optional. Integer: 0=Other, 1=AIRPLANE, 2=NONPOWERED GLIDER, 3=POWERED GLIDER, 4=HELICOPTER, 5=GYROPLANE, 6=BALLOON/AIRSHIP, 7=UAV. Default: 7',
                        'is_airworthy': 'Optional. Boolean. Default: False',
                        'icao_aircraft_type_designator': 'Optional. String (max 4 chars). Default: "0000"',
                        'max_certified_takeoff_weight': 'Optional. Decimal. Default: 0.00',
                        'status': 'Optional. Integer: 0=Inactive, 1=Active. Default: 1'
                    }
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Create the aircraft using the validated serializer
            serializer.save()
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
            
        except ValidationError as e:
            # Handle DRF ValidationError
            print(f"ValidationError in aircraft creation: {str(e)}", flush=True)
            error_details = dict(e.detail) if hasattr(e, 'detail') else {'error': [str(e)]}
            formatted_errors = {}
            for field, errors in error_details.items():
                if isinstance(errors, list):
                    formatted_errors[field] = [str(e) for e in errors]
                else:
                    formatted_errors[field] = [str(errors)]
            
            return Response({
                'status': 'error',
                'message': 'Validation failed',
                'errors': formatted_errors,
                'received_data': dict(request.data) if hasattr(request.data, 'dict') else request.data
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"Exception in aircraft creation: {str(e)}", flush=True)
            import traceback
            print(traceback.format_exc(), flush=True)
            return Response({
                'status': 'error',
                'message': f'Server error: {str(e)}',
                'error_type': type(e).__name__
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AircraftDetail(mixins.RetrieveModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.DestroyModelMixin,
                    generics.GenericAPIView):
    """
    Retrieve, update or delete an Aircraft instance.
    """
    queryset = Aircraft.objects.all()
    serializer_class = AircraftSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
    
    @requires_auth
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
    
    @requires_auth
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    @requires_auth
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class AircraftESNDetails(mixins.RetrieveModelMixin,
                    generics.GenericAPIView):
    """
    Retrieve aircraft by ESN.
    """
    queryset = Aircraft.objects.all()
    serializer_class = AircraftESNSerializer
    lookup_field = 'esn'

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class ContactList(mixins.ListModelMixin,
                mixins.CreateModelMixin,
                generics.GenericAPIView):
    """
    List all contacts or create a new contact.
    """
    queryset = Contact.objects.all()
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ContactCreateSerializer
        return ContactSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
    
    @requires_auth
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class ContactDetail(mixins.RetrieveModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.DestroyModelMixin,
                    generics.GenericAPIView):
    """
    Retrieve, update or delete a Contact instance.
    """
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
    
    @requires_auth
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
    
    @requires_auth
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    @requires_auth
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class ContactDetailPrivilaged(mixins.RetrieveModelMixin,
                    generics.GenericAPIView):
    """
    Retrieve contact with privileged details.
    """
    queryset = Contact.objects.all()
    serializer_class = PrivilagedContactSerializer

    @requires_scope('read:privileged')
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class PilotList(mixins.ListModelMixin,
                mixins.CreateModelMixin,
                generics.GenericAPIView):
    """
    List all pilots or create a new pilot.
    """
    queryset = Pilot.objects.all()
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PilotCreateSerializer
        return PilotSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
    
    @requires_auth
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class PilotDetail(mixins.RetrieveModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.DestroyModelMixin,
                    generics.GenericAPIView):
    """
    Retrieve, update or delete a Pilot instance.
    """
    queryset = Pilot.objects.all()
    serializer_class = PilotSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
    
    @requires_auth
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
    
    @requires_auth
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    @requires_auth
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class PilotDetailPrivilaged(mixins.RetrieveModelMixin,
                    generics.GenericAPIView):
    """
    Retrieve pilot with privileged details.
    """
    queryset = Pilot.objects.all()
    serializer_class = PrivilagedPilotSerializer

    @requires_scope('read:privileged')
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class ManufacturerList(mixins.ListModelMixin,
                   generics.GenericAPIView):
    """
    List all manufacturers.
    """
    queryset = Manufacturer.objects.all()
    serializer_class = ManufacturerSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class HomeView(TemplateView):
    template_name = 'registry/index.html'


class APIView(TemplateView):
    template_name = 'registry/api.html'


class RIDModuleList(mixins.ListModelMixin,
                    mixins.CreateModelMixin,
                    generics.GenericAPIView):
    """
    List all RID modules, or create a new RID module.
    Supports filtering by operator via ?operator=<uuid> query parameter.
    Supports filtering by aircraft via ?aircraft=<uuid> query parameter.
    """
    queryset = RIDModule.objects.all()
    
    def get_queryset(self):
        """
        Optionally filter RID modules by operator or aircraft query parameters.
        Example: GET /api/v1/rid-modules?operator=566d63bb-cb1c-42dc-9a51-baef0d0a8d04
        Example: GET /api/v1/rid-modules?aircraft=566d63bb-cb1c-42dc-9a51-baef0d0a8d04
        """
        queryset = RIDModule.objects.all()
        operator_id = self.request.query_params.get('operator', None)
        aircraft_id = self.request.query_params.get('aircraft', None)
        
        if operator_id:
            queryset = queryset.filter(operator_id=operator_id)
        if aircraft_id:
            queryset = queryset.filter(aircraft_id=aircraft_id)
        
        return queryset
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return RIDModuleCreateSerializer
        return RIDModuleSerializer
    
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
    
    @requires_auth
    def post(self, request, *args, **kwargs):
        print("Received POST data for RID module:", request.data, flush=True)
        
        try:
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                error_details = dict(serializer.errors)
                print("DEBUG - Validation errors:", error_details, flush=True)
                
                formatted_errors = {}
                for field, errors in error_details.items():
                    if isinstance(errors, list):
                        formatted_errors[field] = [str(e) for e in errors]
                    else:
                        formatted_errors[field] = [str(errors)]
                
                return Response({
                    'status': 'error',
                    'message': 'Validation failed',
                    'errors': formatted_errors,
                    'received_data': dict(request.data) if hasattr(request.data, 'dict') else request.data,
                }, status=status.HTTP_400_BAD_REQUEST)
            
            serializer.save()
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
            
        except ValidationError as e:
            print(f"ValidationError in RID module creation: {str(e)}", flush=True)
            error_details = dict(e.detail) if hasattr(e, 'detail') else {'error': [str(e)]}
            formatted_errors = {}
            for field, errors in error_details.items():
                if isinstance(errors, list):
                    formatted_errors[field] = [str(e) for e in errors]
                else:
                    formatted_errors[field] = [str(errors)]
            
            return Response({
                'status': 'error',
                'message': 'Validation failed',
                'errors': formatted_errors,
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"Exception in RID module creation: {str(e)}", flush=True)
            import traceback
            print(traceback.format_exc(), flush=True)
            return Response({
                'status': 'error',
                'message': f'Server error: {str(e)}',
                'error_type': type(e).__name__
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RIDModuleDetail(mixins.RetrieveModelMixin,
                     mixins.UpdateModelMixin,
                     mixins.DestroyModelMixin,
                     generics.GenericAPIView):
    """
    Retrieve, update or delete a RID Module instance.
    """
    queryset = RIDModule.objects.all()
    serializer_class = RIDModuleSerializer
    
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
    
    @requires_auth
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
    
    @requires_auth
    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        # Handle deactivation
        if 'status' in request.data and request.data['status'] in ['inactive', 'decommissioned', 'lost']:
            from django.utils import timezone
            if not instance.deactivated_at:
                request.data['deactivated_at'] = timezone.now()
        return self.partial_update(request, *args, **kwargs)
    
    @requires_auth
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        # Soft delete - set status to decommissioned instead of actually deleting
        from django.utils import timezone
        instance.status = 'decommissioned'
        instance.deactivated_at = timezone.now()
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RIDModuleByRIDID(mixins.RetrieveModelMixin,
                       generics.GenericAPIView):
    """
    Retrieve RID module by RID ID.
    """
    queryset = RIDModule.objects.all()
    serializer_class = RIDModuleSerializer
    lookup_field = 'rid_id'
    
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class RIDModuleByESN(mixins.RetrieveModelMixin,
                     generics.GenericAPIView):
    """
    Retrieve RID module by ESN (Electronic Serial Number).
    """
    queryset = RIDModule.objects.all()
    serializer_class = RIDModuleSerializer
    lookup_field = 'module_esn'
    
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class OperatorRIDModules(mixins.ListModelMixin,
                        generics.GenericAPIView):
    """
    Retrieve all RID modules for a specific operator.
    """
    queryset = RIDModule.objects.all()
    serializer_class = RIDModuleSerializer
    
    def get_queryset(self):
        operator_id = self.kwargs.get('pk')
        return RIDModule.objects.filter(operator_id=operator_id)
    
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class AircraftRIDModules(mixins.ListModelMixin,
                        generics.GenericAPIView):
    """
    Retrieve all RID modules for a specific aircraft.
    """
    queryset = RIDModule.objects.all()
    serializer_class = RIDModuleSerializer
    
    def get_queryset(self):
        aircraft_id = self.kwargs.get('pk')
        return RIDModule.objects.filter(aircraft_id=aircraft_id)
    
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class RIDModuleRIDIDUpdate(generics.GenericAPIView):
    """
    Update the RID ID of a RID Module.
    PATCH /api/v1/rid-modules/{module_id}/rid-id
    """
    queryset = RIDModule.objects.all()
    serializer_class = RIDModuleRIDIDUpdateSerializer
    lookup_field = 'pk'
    
    @requires_auth
    def patch(self, request, *args, **kwargs):
        """Update the RID ID of the module"""
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=False)
        
        if serializer.is_valid():
            serializer.save()
            # Return the full module object using the standard serializer
            response_serializer = RIDModuleSerializer(instance)
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
