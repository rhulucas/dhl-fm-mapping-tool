"""
Excel/CSV Import Module for Facility Management
================================================
Converts Excel or CSV data to GeoJSON format for the mapping tool.
"""

import pandas as pd
import json
import os

def csv_to_geojson(csv_file_path):
    """
    Convert a CSV file to GeoJSON format.
    
    Expected columns:
    - id, name, type, address, latitude, longitude
    - size_sqft, employees
    - manager_name, manager_email, manager_phone
    - it_name, it_email, it_phone (optional)
    """
    df = pd.read_csv(csv_file_path)
    
    features = []
    
    for _, row in df.iterrows():
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [float(row['longitude']), float(row['latitude'])]
            },
            "properties": {
                "id": str(row['id']),
                "name": str(row['name']),
                "type": str(row['type']),
                "address": str(row['address']),
                "size_sqft": int(row.get('size_sqft', 10000)),
                "employees": int(row.get('employees', 50)),
                "contacts": {
                    "facility_manager": {
                        "name": str(row.get('manager_name', 'TBD')),
                        "email": str(row.get('manager_email', 'manager@company.com')),
                        "phone": str(row.get('manager_phone', '555-0000'))
                    },
                    "it_support": {
                        "name": str(row.get('it_name', 'IT Support')),
                        "email": str(row.get('it_email', 'it@company.com')),
                        "phone": str(row.get('it_phone', '555-0001'))
                    },
                    "maintenance": {
                        "name": "Maintenance Team",
                        "email": "maintenance@company.com",
                        "phone": "555-0002"
                    },
                    "security": {
                        "name": "Security Team",
                        "email": "security@company.com",
                        "phone": "555-0003"
                    }
                },
                "equipment": [
                    "HVAC System",
                    "Fire Suppression System",
                    "Security System"
                ],
                "emergency_procedures": {
                    "power_outage": [
                        "Check main breaker panel",
                        "Contact facility manager",
                        "Activate backup generators if available"
                    ],
                    "fire_alarm": [
                        "Evacuate immediately",
                        "Call 911",
                        "Meet at designated assembly point"
                    ]
                }
            }
        }
        features.append(feature)
    
    geojson = {
        "type": "FeatureCollection",
        "features": features
    }
    
    return geojson


def excel_to_geojson(excel_file_path):
    """
    Convert an Excel file to GeoJSON format.
    Reads the first sheet of the Excel file.
    """
    df = pd.read_excel(excel_file_path, sheet_name=0)
    
    # Save as temp CSV and use csv_to_geojson
    temp_csv = excel_file_path.replace('.xlsx', '_temp.csv').replace('.xls', '_temp.csv')
    df.to_csv(temp_csv, index=False)
    
    geojson = csv_to_geojson(temp_csv)
    
    # Clean up temp file
    os.remove(temp_csv)
    
    return geojson


def save_geojson(geojson_data, output_path):
    """Save GeoJSON data to a file."""
    with open(output_path, 'w') as f:
        json.dump(geojson_data, f, indent=2)
    print(f"Saved {len(geojson_data['features'])} facilities to {output_path}")


# Example usage
if __name__ == "__main__":
    # Test with the template
    template_path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'facility_template.csv')
    
    if os.path.exists(template_path):
        geojson = csv_to_geojson(template_path)
        print(json.dumps(geojson, indent=2))
    else:
        print("Template file not found. Please create templates/facility_template.csv")
