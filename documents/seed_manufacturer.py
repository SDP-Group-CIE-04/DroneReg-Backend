#!/usr/bin/env python
"""
Script to seed a manufacturer in the database

This script adds a sample manufacturer to the database to allow proper
testing of the aircraft registration functionality.

Usage:
    python seed_manufacturer.py
"""

import os
import sys
import django

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ohio.settings")
django.setup()

from registry.models import Manufacturer, Address
import uuid

def create_manufacturer():
    """Create a sample manufacturer if none exists"""
    
    # Check if any manufacturers exist
    if Manufacturer.objects.count() > 0:
        print("Manufacturers already exist in database")
        return
    
    # Create an address for the manufacturer
    address = Address.objects.create(
        address_line_1="1 Drone Avenue",
        address_line_2="Industrial Park",
        address_line_3="",
        postcode="DR1 2MF",
        city="San Francisco",
        country="US"
    )
    
    # Create the manufacturer
    manufacturer = Manufacturer.objects.create(
        full_name="DJI Technology Co., Ltd.",
        common_name="DJI",
        address=address,
        acronym="DJI",
        role="Drone Manufacturer",
        country="CN"
    )
    
    print(f"Created manufacturer: {manufacturer.common_name}")
    print(f"Manufacturer ID: {manufacturer.id}")
    
if __name__ == "__main__":
    create_manufacturer() 