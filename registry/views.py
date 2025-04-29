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

from registry.models import Activity, Authorization, Contact, Operator, Aircraft, Pilot, Test, TestValidity, Person, Address, Manufacturer
from registry.serializers import (ContactSerializer, OperatorSerializer, PilotSerializer, 
                                  PrivilagedContactSerializer, PrivilagedPilotSerializer,
                                  PrivilagedOperatorSerializer, AircraftSerializer, AircraftESNSerializer,
                                  OperatorCreateSerializer, PilotCreateSerializer, 
                                  ContactCreateSerializer, AircraftCreateSerializer, ManufacturerSerializer)
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
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            print("Validation errors:", serializer.errors)
        return self.create(request, *args, **kwargs)


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
    """
    queryset = Aircraft.objects.all()
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AircraftCreateSerializer
        return AircraftSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
    
    @requires_auth
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


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
