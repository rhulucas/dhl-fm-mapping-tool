#!/usr/bin/env python3
"""
Faster 99 - Large Scale Facility Data Generator
================================================
Generates 100 realistic facility records across multiple US states.
Demonstrates data modeling and generation capabilities.
"""

import json
import random
from datetime import datetime

# Seed for reproducibility
random.seed(42)

# US Cities with coordinates (major logistics hubs)
# offset_dir: direction to offset (to avoid water bodies)
# "any" = any direction, "east" = only east, "inland" = away from coast, etc.
US_CITIES = [
    # Ohio
    {"city": "Columbus", "state": "OH", "lat": 39.9612, "lng": -82.9988, "offset_dir": "any"},
    {"city": "Cleveland", "state": "OH", "lat": 41.4500, "lng": -81.7000, "offset_dir": "south"},  # Lake Erie to north
    {"city": "Cincinnati", "state": "OH", "lat": 39.1031, "lng": -84.5120, "offset_dir": "any"},
    {"city": "Dayton", "state": "OH", "lat": 39.7589, "lng": -84.1916, "offset_dir": "any"},
    {"city": "Toledo", "state": "OH", "lat": 41.6200, "lng": -83.5500, "offset_dir": "south"},  # Lake Erie to north
    {"city": "Akron", "state": "OH", "lat": 41.0814, "lng": -81.5190, "offset_dir": "any"},
    # Indiana
    {"city": "Indianapolis", "state": "IN", "lat": 39.7684, "lng": -86.1581, "offset_dir": "any"},
    {"city": "Fort Wayne", "state": "IN", "lat": 41.0793, "lng": -85.1394, "offset_dir": "any"},
    {"city": "Evansville", "state": "IN", "lat": 37.9716, "lng": -87.5711, "offset_dir": "any"},
    # Illinois
    {"city": "Chicago", "state": "IL", "lat": 41.8500, "lng": -87.7500, "offset_dir": "west"},  # Lake Michigan to east
    {"city": "Aurora", "state": "IL", "lat": 41.7606, "lng": -88.3201, "offset_dir": "any"},
    {"city": "Rockford", "state": "IL", "lat": 42.2711, "lng": -89.0940, "offset_dir": "any"},
    {"city": "Joliet", "state": "IL", "lat": 41.5250, "lng": -88.0817, "offset_dir": "any"},
    # Michigan
    {"city": "Detroit", "state": "MI", "lat": 42.3500, "lng": -83.1000, "offset_dir": "north"},  # River to south
    {"city": "Grand Rapids", "state": "MI", "lat": 42.9634, "lng": -85.6681, "offset_dir": "any"},
    {"city": "Lansing", "state": "MI", "lat": 42.7325, "lng": -84.5555, "offset_dir": "any"},
    # Kentucky
    {"city": "Louisville", "state": "KY", "lat": 38.2527, "lng": -85.7585, "offset_dir": "any"},
    {"city": "Lexington", "state": "KY", "lat": 38.0406, "lng": -84.5037, "offset_dir": "any"},
    # Pennsylvania
    {"city": "Pittsburgh", "state": "PA", "lat": 40.4406, "lng": -79.9959, "offset_dir": "any"},
    {"city": "Philadelphia", "state": "PA", "lat": 39.9800, "lng": -75.1500, "offset_dir": "west"},  # River to east
    {"city": "Harrisburg", "state": "PA", "lat": 40.2732, "lng": -76.8867, "offset_dir": "any"},
    # Tennessee
    {"city": "Nashville", "state": "TN", "lat": 36.1627, "lng": -86.7816, "offset_dir": "any"},
    {"city": "Memphis", "state": "TN", "lat": 35.1495, "lng": -90.0000, "offset_dir": "east"},  # River to west
    {"city": "Knoxville", "state": "TN", "lat": 35.9606, "lng": -83.9207, "offset_dir": "any"},
    # Georgia
    {"city": "Atlanta", "state": "GA", "lat": 33.7490, "lng": -84.3880, "offset_dir": "any"},
    {"city": "Savannah", "state": "GA", "lat": 32.0500, "lng": -81.1500, "offset_dir": "west"},  # Coast to east
    # Texas
    {"city": "Dallas", "state": "TX", "lat": 32.7767, "lng": -96.7970, "offset_dir": "any"},
    {"city": "Houston", "state": "TX", "lat": 29.7800, "lng": -95.4000, "offset_dir": "north"},  # Coast to south
    {"city": "San Antonio", "state": "TX", "lat": 29.4241, "lng": -98.4936, "offset_dir": "any"},
    {"city": "Austin", "state": "TX", "lat": 30.2672, "lng": -97.7431, "offset_dir": "any"},
    # California
    {"city": "Los Angeles", "state": "CA", "lat": 34.0522, "lng": -118.2437, "offset_dir": "east"},  # Coast to west
    {"city": "San Francisco", "state": "CA", "lat": 37.7600, "lng": -122.3500, "offset_dir": "east"},  # Bay to west
    {"city": "San Diego", "state": "CA", "lat": 32.7400, "lng": -117.1000, "offset_dir": "east"},  # Coast to west
    {"city": "Sacramento", "state": "CA", "lat": 38.5816, "lng": -121.4944, "offset_dir": "any"},
    # New York
    {"city": "New York", "state": "NY", "lat": 40.7500, "lng": -73.9500, "offset_dir": "north"},  # Water to south/east
    {"city": "Buffalo", "state": "NY", "lat": 42.9000, "lng": -78.8000, "offset_dir": "east"},  # Lake Erie to west
    {"city": "Rochester", "state": "NY", "lat": 43.1300, "lng": -77.6500, "offset_dir": "south"},  # Lake Ontario to north
    # New Jersey
    {"city": "Newark", "state": "NJ", "lat": 40.7357, "lng": -74.1724, "offset_dir": "west"},  # Water to east
    {"city": "Jersey City", "state": "NJ", "lat": 40.7300, "lng": -74.1000, "offset_dir": "west"},  # Water to east
    # Florida
    {"city": "Miami", "state": "FL", "lat": 25.7800, "lng": -80.2500, "offset_dir": "west"},  # Coast to east
    {"city": "Orlando", "state": "FL", "lat": 28.5383, "lng": -81.3792, "offset_dir": "any"},
    {"city": "Tampa", "state": "FL", "lat": 27.9700, "lng": -82.5000, "offset_dir": "east"},  # Bay to west
    {"city": "Jacksonville", "state": "FL", "lat": 30.3500, "lng": -81.7000, "offset_dir": "west"},  # Coast to east
]

# Facility types with weights (more common types have higher weights)
FACILITY_TYPES = [
    ("distribution", 25),
    ("hub", 20),
    ("warehouse", 20),
    ("fulfillment", 15),
    ("sorting", 8),
    ("crossdock", 5),
    ("cold_storage", 4),
    ("returns", 2),
    ("service", 1),
]

# Street names for address generation
STREET_TYPES = ["Way", "Drive", "Road", "Boulevard", "Parkway", "Lane", "Avenue", "Street"]
STREET_NAMES = [
    "Industrial", "Commerce", "Logistics", "Distribution", "Enterprise", "Gateway",
    "Corporate", "Business", "Trade", "Freight", "Cargo", "Supply Chain",
    "Innovation", "Technology", "Warehouse", "Central", "Metro", "Regional"
]

# First and last names for contact generation
FIRST_NAMES = [
    "James", "Michael", "Robert", "David", "William", "Richard", "Joseph", "Thomas",
    "Christopher", "Daniel", "Matthew", "Anthony", "Mark", "Steven", "Paul", "Andrew",
    "Jennifer", "Elizabeth", "Linda", "Barbara", "Susan", "Jessica", "Sarah", "Karen",
    "Nancy", "Lisa", "Betty", "Margaret", "Sandra", "Ashley", "Dorothy", "Kimberly",
    "Emily", "Donna", "Michelle", "Carol", "Amanda", "Melissa", "Deborah", "Stephanie"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
    "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
    "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker",
    "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores"
]

# Equipment by facility type
EQUIPMENT_BY_TYPE = {
    "distribution": [
        "Automated Sorting System", "Conveyor Network", "Pallet Racking System",
        "Loading Dock Equipment", "Forklift Fleet", "Stretch Wrapper", "Label Printer Array"
    ],
    "hub": [
        "High-Speed Sorter", "Cross-Belt Conveyor", "Automated Guided Vehicles",
        "Package Scanner Array", "Dimensioning System", "Fleet Vehicles"
    ],
    "warehouse": [
        "Racking System", "Forklift Fleet", "Pallet Jacks", "Inventory Scanner Network",
        "Shelving Units", "Order Picking Carts", "Stretch Wrap Machine"
    ],
    "fulfillment": [
        "Pick-to-Light System", "Automated Storage/Retrieval", "Packing Stations",
        "Shipping Scale Array", "Robotic Arms", "Conveyor System"
    ],
    "sorting": [
        "High-Speed Sorter", "Conveyor Network", "Barcode Scanner Array",
        "Divert Systems", "Accumulation Tables", "Label Applicators"
    ],
    "crossdock": [
        "Dock Levelers", "Pallet Jacks", "Staging Area Equipment",
        "RF Scanner System", "Dock Lights", "Truck Restraints"
    ],
    "cold_storage": [
        "Refrigeration Units", "Freezer Compressors", "Temperature Monitoring System",
        "Cold Room Doors", "Pallet Racking (Cold)", "Defrost System"
    ],
    "returns": [
        "Inspection Stations", "Grading Equipment", "Repackaging Line",
        "Quality Control Scanners", "Refurbishment Tools", "Inventory System"
    ],
    "service": [
        "Vehicle Service Bays", "Diagnostic Equipment", "Parts Storage",
        "Fuel Station", "Wash Bay", "Tire Service Equipment"
    ]
}

# Emergency procedures by type
EMERGENCY_PROCEDURES = {
    "power_outage": [
        "Activate emergency lighting",
        "Check main circuit breakers",
        "Start backup generator if available",
        "Contact utility company",
        "Notify facility manager",
        "Secure temperature-sensitive inventory"
    ],
    "hvac_failure": [
        "Check thermostat settings",
        "Inspect air filters",
        "Verify outdoor unit operation",
        "Contact HVAC service provider",
        "Open dock doors for ventilation if needed",
        "Monitor temperature readings"
    ],
    "security_breach": [
        "Activate alarm system",
        "Lock down all entry points",
        "Contact security team",
        "Review surveillance footage",
        "Notify local authorities if needed",
        "Document incident details"
    ],
    "fire_alarm": [
        "Evacuate building immediately",
        "Call 911",
        "Account for all personnel",
        "Meet at designated assembly point",
        "Do not re-enter until cleared by fire department",
        "Contact facility manager"
    ],
    "water_leak": [
        "Locate and close main water valve",
        "Move inventory away from affected area",
        "Contact maintenance team",
        "Document damage for insurance",
        "Set up water extraction equipment",
        "Check for electrical hazards"
    ],
    "equipment_malfunction": [
        "Press emergency stop button",
        "Clear area around equipment",
        "Do not attempt repairs without training",
        "Contact maintenance department",
        "Document malfunction details",
        "Implement backup procedures"
    ]
}


def weighted_choice(choices):
    """Select from weighted choices."""
    total = sum(weight for _, weight in choices)
    r = random.uniform(0, total)
    upto = 0
    for choice, weight in choices:
        if upto + weight >= r:
            return choice
        upto += weight
    return choices[-1][0]


def generate_address(city_info):
    """Generate a realistic street address."""
    number = random.randint(100, 9999)
    street_name = random.choice(STREET_NAMES)
    street_type = random.choice(STREET_TYPES)
    return f"{number} {street_name} {street_type}, {city_info['city']}, {city_info['state']}"


def generate_contact():
    """Generate a random contact person."""
    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    email_first = first.lower()[0]
    email_last = last.lower()
    return {
        "name": f"{first} {last}",
        "email": f"{email_first}.{email_last}@faster99.com",
        "phone": f"{random.randint(200,999)}-555-{random.randint(1000,9999)}"
    }


def generate_coordinates(city_info):
    """Generate coordinates with directional offset to avoid water bodies."""
    offset_dir = city_info.get('offset_dir', 'any')
    
    # Base offset range (about 2-3 miles)
    offset_range = 0.04
    
    if offset_dir == 'any':
        lat_offset = random.uniform(-offset_range, offset_range)
        lng_offset = random.uniform(-offset_range, offset_range)
    elif offset_dir == 'north':
        lat_offset = random.uniform(0.01, offset_range)
        lng_offset = random.uniform(-offset_range/2, offset_range/2)
    elif offset_dir == 'south':
        lat_offset = random.uniform(-offset_range, -0.01)
        lng_offset = random.uniform(-offset_range/2, offset_range/2)
    elif offset_dir == 'east':
        lat_offset = random.uniform(-offset_range/2, offset_range/2)
        lng_offset = random.uniform(0.01, offset_range)
    elif offset_dir == 'west':
        lat_offset = random.uniform(-offset_range/2, offset_range/2)
        lng_offset = random.uniform(-offset_range, -0.01)
    else:
        lat_offset = random.uniform(-offset_range, offset_range)
        lng_offset = random.uniform(-offset_range, offset_range)
    
    return [
        round(city_info['lng'] + lng_offset, 4),
        round(city_info['lat'] + lat_offset, 4)
    ]


def generate_facility(index, city_info):
    """Generate a single facility record."""
    facility_type = weighted_choice(FACILITY_TYPES)
    
    # Size based on type
    size_ranges = {
        "distribution": (150000, 500000),
        "hub": (100000, 350000),
        "warehouse": (80000, 250000),
        "fulfillment": (120000, 400000),
        "sorting": (60000, 180000),
        "crossdock": (40000, 120000),
        "cold_storage": (50000, 200000),
        "returns": (30000, 100000),
        "service": (20000, 80000),
    }
    
    size_range = size_ranges.get(facility_type, (50000, 150000))
    size = random.randint(*size_range)
    
    # Employees based on size
    employees_per_sqft = random.uniform(0.0003, 0.0008)
    employees = int(size * employees_per_sqft)
    
    # Select random equipment for this facility type
    available_equipment = EQUIPMENT_BY_TYPE.get(facility_type, ["General Equipment"])
    equipment = random.sample(available_equipment, min(4, len(available_equipment)))
    equipment.extend(["HVAC System", "Fire Suppression System", "Security System"])
    
    # Select random emergency procedures
    procedure_keys = random.sample(list(EMERGENCY_PROCEDURES.keys()), 4)
    procedures = {key: EMERGENCY_PROCEDURES[key] for key in procedure_keys}
    
    # Generate facility ID
    type_prefix = {
        "distribution": "DC",
        "hub": "HB",
        "warehouse": "WH",
        "fulfillment": "FC",
        "sorting": "SF",
        "crossdock": "CD",
        "cold_storage": "CS",
        "returns": "RC",
        "service": "SC"
    }
    prefix = type_prefix.get(facility_type, "FL")
    facility_id = f"{prefix}-{str(index).zfill(3)}"
    
    # Generate facility name
    type_names = {
        "distribution": "Distribution Center",
        "hub": "Regional Hub",
        "warehouse": "Warehouse",
        "fulfillment": "Fulfillment Center",
        "sorting": "Sorting Facility",
        "crossdock": "Cross-Dock",
        "cold_storage": "Cold Storage",
        "returns": "Returns Center",
        "service": "Service Center"
    }
    type_name = type_names.get(facility_type, "Facility")
    facility_name = f"{city_info['city']} {type_name}"
    
    # Add suffix for duplicates
    suffix_options = ["", " East", " West", " North", " South", " Central", " Metro", " Gateway"]
    facility_name += random.choice(suffix_options)
    
    return {
        "type": "Feature",
        "properties": {
            "id": facility_id,
            "name": facility_name.strip(),
            "type": facility_type,
            "address": generate_address(city_info),
            "size_sqft": size,
            "employees": employees,
            "contacts": {
                "facility_manager": generate_contact(),
                "it_support": generate_contact(),
                "maintenance": generate_contact(),
                "security": generate_contact()
            },
            "equipment": equipment,
            "emergency_procedures": procedures,
            "floor_plan": f"{facility_id.lower()}_floorplan.svg"
        },
        "geometry": {
            "type": "Point",
            "coordinates": generate_coordinates(city_info)
        }
    }


def generate_all_facilities(count=100):
    """Generate specified number of facilities."""
    facilities = []
    
    for i in range(1, count + 1):
        city_info = random.choice(US_CITIES)
        facility = generate_facility(i, city_info)
        facilities.append(facility)
        
        if i % 10 == 0:
            print(f"Generated {i}/{count} facilities...")
    
    return {
        "type": "FeatureCollection",
        "features": facilities
    }


def generate_statistics(data):
    """Generate statistics summary."""
    features = data['features']
    
    total_sqft = sum(f['properties']['size_sqft'] for f in features)
    total_employees = sum(f['properties']['employees'] for f in features)
    
    by_type = {}
    by_state = {}
    
    for f in features:
        props = f['properties']
        ftype = props['type']
        by_type[ftype] = by_type.get(ftype, 0) + 1
        
        # Extract state from address
        address = props['address']
        state = address.split(',')[-1].strip()
        by_state[state] = by_state.get(state, 0) + 1
    
    return {
        "total_facilities": len(features),
        "total_sqft": total_sqft,
        "total_employees": total_employees,
        "by_type": by_type,
        "by_state": by_state
    }


def main():
    print("\n" + "=" * 60)
    print("FASTER 99 - LARGE SCALE FACILITY DATA GENERATOR")
    print("=" * 60)
    print(f"\nGenerating 100 facilities across {len(US_CITIES)} US cities...\n")
    
    # Generate facilities
    data = generate_all_facilities(100)
    
    # Save to file
    output_file = 'data.json'
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"\n✓ Saved {len(data['features'])} facilities to {output_file}")
    
    # Generate and display statistics
    stats = generate_statistics(data)
    
    print("\n" + "=" * 60)
    print("GENERATION SUMMARY")
    print("=" * 60)
    print(f"\nTotal Facilities: {stats['total_facilities']}")
    print(f"Total Square Footage: {stats['total_sqft']:,} sqft ({stats['total_sqft']/1000000:.1f}M)")
    print(f"Total Employees: {stats['total_employees']:,}")
    
    print("\nBy Facility Type:")
    for ftype, count in sorted(stats['by_type'].items(), key=lambda x: -x[1]):
        print(f"  {ftype.replace('_', ' ').title()}: {count}")
    
    print("\nBy State:")
    for state, count in sorted(stats['by_state'].items(), key=lambda x: -x[1])[:10]:
        print(f"  {state}: {count}")
    
    print("\n" + "=" * 60)
    print("GENERATION COMPLETE!")
    print("=" * 60 + "\n")


if __name__ == '__main__':
    main()
