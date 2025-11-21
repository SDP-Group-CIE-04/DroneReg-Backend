import os
import json
import jwt
from django.http import JsonResponse
from functools import wraps
from six.moves.urllib import request as req
from rest_framework import status
from rest_framework.response import Response

def get_token_auth_header(request):
    """Obtains the Access Token from the Authorization Header"""
    auth = request.META.get("HTTP_AUTHORIZATION", "")
    parts = auth.split()
    
    if not parts or parts[0].lower() != "bearer":
        return None
    
    token = parts[1] if len(parts) == 2 else None
    return token

def requires_auth(view_func):
    """Determines if the Access Token is valid"""
    @wraps(view_func)
    def decorated(self, request, *args, **kwargs):
        # Check if authentication bypass is enabled
        bypass_auth = os.environ.get('BYPASS_AUTHENTICATION', 'False') == 'True'
        if bypass_auth:
            return view_func(self, request, *args, **kwargs)
        
        token = get_token_auth_header(request)
        if not token:
            return Response({"message": "Authorization header is required"}, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            # This would validate with Auth0 in a real implementation
            # For now we're just checking the token exists
            payload = jwt.decode(token, verify=False)
        except jwt.PyJWTError:
            return Response({"message": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)
            
        return view_func(self, request, *args, **kwargs)
    return decorated

def requires_scope(required_scope):
    """Determines if the required scope is present in the Access Token"""
    def require_scope(view_func):
        @wraps(view_func)
        def decorated(self, request, *args, **kwargs):
            # Check if authentication bypass is enabled
            bypass_auth = os.environ.get('BYPASS_AUTHENTICATION', 'False') == 'True'
            if bypass_auth:
                return view_func(self, request, *args, **kwargs)
            
            token = get_token_auth_header(request)
            if not token:
                return Response({"message": "Authorization header is required"}, status=status.HTTP_401_UNAUTHORIZED)
            
            try:
                # For demo purposes, we're not verifying the token
                decoded = jwt.decode(token, verify=False)
            except jwt.PyJWTError:
                return Response({"message": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)
                
            if decoded.get("scope"):
                token_scopes = decoded["scope"].split()
                for token_scope in token_scopes:
                    if token_scope == required_scope:
                        return view_func(self, request, *args, **kwargs)
            
            return Response({"message": "You don't have access to this resource"}, status=status.HTTP_403_FORBIDDEN)
        return decorated
    return require_scope
