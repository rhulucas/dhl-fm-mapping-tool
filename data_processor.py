#!/usr/bin/env python3
"""
Faster 99 - Facility Data Processor
====================================
This script demonstrates Python skills for data processing and validation.
Used for generating, validating, and analyzing facility data.

Skills demonstrated:
- JSON data handling
- Data validation
- Statistical analysis
- Report generation
- API data modeling
"""

import json
from datetime import datetime
from collections import defaultdict
import os

# Configuration
DATA_FILE = 'data.json'
REPORT_FILE = 'facility_report.txt'


def load_facility_data(filepath):
    """Load and parse GeoJSON facility data."""
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        print(f"✓ Loaded {len(data['features'])} facilities from {filepath}")
        return data
    except FileNotFoundError:
        print(f"✗ Error: {filepath} not found")
        return None
    except json.JSONDecodeError as e:
        print(f"✗ Error parsing JSON: {e}")
        return None


def validate_facility(facility):
    """Validate a single facility record."""
    errors = []
    props = facility.get('properties', {})
    
    # Required fields
    required_fields = ['id', 'name', 'type', 'address', 'size_sqft', 'employees', 'contacts']
    for field in required_fields:
        if field not in props:
            errors.append(f"Missing required field: {field}")
    
    # Validate contacts structure
    contacts = props.get('contacts', {})
    required_contacts = ['facility_manager', 'it_support', 'maintenance', 'security']
    for contact_type in required_contacts:
        if contact_type not in contacts:
            errors.append(f"Missing contact: {contact_type}")
        else:
            contact = contacts[contact_type]
            if 'name' not in contact or 'email' not in contact or 'phone' not in contact:
                errors.append(f"Incomplete contact info for: {contact_type}")
    
    # Validate geometry
    geometry = facility.get('geometry', {})
    if geometry.get('type') != 'Point':
        errors.append("Invalid geometry type (expected Point)")
    
    coords = geometry.get('coordinates', [])
    if len(coords) != 2:
        errors.append("Invalid coordinates")
    
    return errors


def analyze_facilities(data):
    """Perform statistical analysis on facility data."""
    features = data['features']
    
    stats = {
        'total_facilities': len(features),
        'total_sqft': 0,
        'total_employees': 0,
        'by_type': defaultdict(int),
        'largest_facility': None,
        'smallest_facility': None,
        'avg_sqft': 0,
        'avg_employees': 0
    }
    
    sqft_list = []
    employee_list = []
    
    for f in features:
        props = f['properties']
        sqft = props.get('size_sqft', 0)
        employees = props.get('employees', 0)
        
        stats['total_sqft'] += sqft
        stats['total_employees'] += employees
        stats['by_type'][props.get('type', 'unknown')] += 1
        
        sqft_list.append((props['name'], sqft))
        employee_list.append((props['name'], employees))
    
    # Find largest and smallest
    sqft_list.sort(key=lambda x: x[1], reverse=True)
    stats['largest_facility'] = sqft_list[0] if sqft_list else None
    stats['smallest_facility'] = sqft_list[-1] if sqft_list else None
    
    # Calculate averages
    if features:
        stats['avg_sqft'] = stats['total_sqft'] / len(features)
        stats['avg_employees'] = stats['total_employees'] / len(features)
    
    return stats


def generate_report(data, stats, validation_results):
    """Generate a human-readable facility report."""
    report_lines = [
        "=" * 60,
        "FASTER 99 - FACILITY MANAGEMENT REPORT",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "=" * 60,
        "",
        "SUMMARY STATISTICS",
        "-" * 40,
        f"Total Facilities: {stats['total_facilities']}",
        f"Total Square Footage: {stats['total_sqft']:,} sqft",
        f"Total Employees: {stats['total_employees']:,}",
        f"Average Facility Size: {stats['avg_sqft']:,.0f} sqft",
        f"Average Employees per Facility: {stats['avg_employees']:.0f}",
        "",
        "FACILITIES BY TYPE",
        "-" * 40,
    ]
    
    for ftype, count in sorted(stats['by_type'].items(), key=lambda x: -x[1]):
        percentage = (count / stats['total_facilities']) * 100
        report_lines.append(f"  {ftype.replace('_', ' ').title()}: {count} ({percentage:.1f}%)")
    
    report_lines.extend([
        "",
        "TOP FACILITIES BY SIZE",
        "-" * 40,
        f"  Largest: {stats['largest_facility'][0]} ({stats['largest_facility'][1]:,} sqft)",
        f"  Smallest: {stats['smallest_facility'][0]} ({stats['smallest_facility'][1]:,} sqft)",
        "",
        "DATA VALIDATION",
        "-" * 40,
    ])
    
    if all(len(errors) == 0 for errors in validation_results.values()):
        report_lines.append("  ✓ All facility records passed validation")
    else:
        for facility_id, errors in validation_results.items():
            if errors:
                report_lines.append(f"  ✗ {facility_id}:")
                for error in errors:
                    report_lines.append(f"      - {error}")
    
    report_lines.extend([
        "",
        "FACILITY DETAILS",
        "-" * 40,
    ])
    
    for f in data['features']:
        props = f['properties']
        report_lines.extend([
            f"\n  [{props['id']}] {props['name']}",
            f"    Type: {props['type'].replace('_', ' ').title()}",
            f"    Address: {props['address']}",
            f"    Size: {props['size_sqft']:,} sqft | Employees: {props['employees']}",
            f"    Manager: {props['contacts']['facility_manager']['name']}",
        ])
    
    report_lines.extend([
        "",
        "=" * 60,
        "END OF REPORT",
        "=" * 60,
    ])
    
    return "\n".join(report_lines)


def export_contacts_csv(data, filepath='contacts.csv'):
    """Export all facility contacts to CSV format."""
    lines = ['Facility ID,Facility Name,Role,Contact Name,Email,Phone']
    
    for f in data['features']:
        props = f['properties']
        facility_id = props['id']
        facility_name = props['name']
        
        for role, contact in props['contacts'].items():
            lines.append(
                f'"{facility_id}","{facility_name}","{role}","{contact["name"]}","{contact["email"]}","{contact["phone"]}"'
            )
    
    with open(filepath, 'w') as f:
        f.write("\n".join(lines))
    
    print(f"✓ Exported contacts to {filepath}")


def main():
    """Main entry point."""
    print("\n" + "=" * 50)
    print("FASTER 99 - DATA PROCESSOR")
    print("=" * 50 + "\n")
    
    # Load data
    data = load_facility_data(DATA_FILE)
    if not data:
        return
    
    # Validate all facilities
    print("\nValidating facility data...")
    validation_results = {}
    for f in data['features']:
        facility_id = f['properties'].get('id', 'unknown')
        errors = validate_facility(f)
        validation_results[facility_id] = errors
        if errors:
            print(f"  ✗ {facility_id}: {len(errors)} error(s)")
        else:
            print(f"  ✓ {facility_id}: Valid")
    
    # Analyze data
    print("\nAnalyzing facility data...")
    stats = analyze_facilities(data)
    print(f"  Total facilities: {stats['total_facilities']}")
    print(f"  Total square footage: {stats['total_sqft']:,}")
    print(f"  Total employees: {stats['total_employees']:,}")
    
    # Generate report
    print("\nGenerating report...")
    report = generate_report(data, stats, validation_results)
    
    with open(REPORT_FILE, 'w') as f:
        f.write(report)
    print(f"✓ Report saved to {REPORT_FILE}")
    
    # Export contacts
    export_contacts_csv(data)
    
    print("\n" + "=" * 50)
    print("PROCESSING COMPLETE")
    print("=" * 50 + "\n")


if __name__ == '__main__':
    main()
