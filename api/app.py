"""
Faster 99 - Facility Management API
====================================
RESTful API backend for facility management system.
Designed for deployment on Azure App Service.
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend access

# Load facility data
DATA_FILE = os.path.join(os.path.dirname(__file__), 'data.json')

def load_data():
    """Load facility data from JSON file."""
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"type": "FeatureCollection", "features": []}

def save_data(data):
    """Save facility data to JSON file."""
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)


# =============================================================================
# API ENDPOINTS
# =============================================================================

@app.route('/')
def index():
    """API root - health check."""
    return jsonify({
        "service": "Faster 99 Facility Management API",
        "version": "1.0.0",
        "status": "healthy",
        "endpoints": {
            "GET /api/facilities": "List all facilities",
            "GET /api/facilities/<id>": "Get single facility",
            "GET /api/facilities/stats": "Get statistics",
            "GET /api/facilities/search?q=<query>": "Search facilities",
            "GET /api/facilities/filter?type=<type>&state=<state>": "Filter facilities",
            "POST /api/facilities": "Create new facility",
            "PUT /api/facilities/<id>": "Update facility",
            "DELETE /api/facilities/<id>": "Delete facility"
        }
    })


@app.route('/api/facilities', methods=['GET'])
def get_facilities():
    """Get all facilities with optional filtering."""
    data = load_data()
    features = data.get('features', [])
    
    # Optional query parameters
    facility_type = request.args.get('type')
    state = request.args.get('state')
    limit = request.args.get('limit', type=int)
    
    # Filter by type
    if facility_type:
        features = [f for f in features if f['properties'].get('type') == facility_type]
    
    # Filter by state
    if state:
        features = [f for f in features if state.upper() in f['properties'].get('address', '').upper()]
    
    # Limit results
    if limit:
        features = features[:limit]
    
    return jsonify({
        "type": "FeatureCollection",
        "count": len(features),
        "features": features
    })


@app.route('/api/facilities/<facility_id>', methods=['GET'])
def get_facility(facility_id):
    """Get a single facility by ID."""
    data = load_data()
    
    for feature in data.get('features', []):
        if feature['properties'].get('id') == facility_id:
            return jsonify(feature)
    
    return jsonify({"error": "Facility not found"}), 404


@app.route('/api/facilities/stats', methods=['GET'])
def get_stats():
    """Get facility statistics."""
    data = load_data()
    features = data.get('features', [])
    
    # Calculate statistics
    total_facilities = len(features)
    total_sqft = sum(f['properties'].get('size_sqft', 0) for f in features)
    total_employees = sum(f['properties'].get('employees', 0) for f in features)
    
    # Count by type
    by_type = {}
    for f in features:
        ftype = f['properties'].get('type', 'unknown')
        by_type[ftype] = by_type.get(ftype, 0) + 1
    
    # Count by state
    by_state = {}
    for f in features:
        address = f['properties'].get('address', '')
        parts = address.split(',')
        if len(parts) >= 2:
            state = parts[-1].strip()
            by_state[state] = by_state.get(state, 0) + 1
    
    return jsonify({
        "total_facilities": total_facilities,
        "total_sqft": total_sqft,
        "total_employees": total_employees,
        "avg_sqft": total_sqft // total_facilities if total_facilities > 0 else 0,
        "avg_employees": total_employees // total_facilities if total_facilities > 0 else 0,
        "by_type": by_type,
        "by_state": by_state
    })


@app.route('/api/facilities/search', methods=['GET'])
def search_facilities():
    """Search facilities by name, ID, or address."""
    query = request.args.get('q', '').lower()
    
    if not query:
        return jsonify({"error": "Search query required"}), 400
    
    data = load_data()
    results = []
    
    for feature in data.get('features', []):
        props = feature['properties']
        # Search in name, ID, and address
        if (query in props.get('name', '').lower() or
            query in props.get('id', '').lower() or
            query in props.get('address', '').lower()):
            results.append(feature)
    
    return jsonify({
        "type": "FeatureCollection",
        "query": query,
        "count": len(results),
        "features": results
    })


@app.route('/api/facilities', methods=['POST'])
def create_facility():
    """Create a new facility."""
    if not request.json:
        return jsonify({"error": "JSON data required"}), 400
    
    data = load_data()
    new_feature = request.json
    
    # Validate required fields
    required = ['id', 'name', 'type', 'address']
    props = new_feature.get('properties', {})
    missing = [f for f in required if f not in props]
    
    if missing:
        return jsonify({"error": f"Missing required fields: {missing}"}), 400
    
    # Check for duplicate ID
    for feature in data.get('features', []):
        if feature['properties'].get('id') == props.get('id'):
            return jsonify({"error": "Facility ID already exists"}), 409
    
    data['features'].append(new_feature)
    save_data(data)
    
    return jsonify({
        "message": "Facility created successfully",
        "facility": new_feature
    }), 201


@app.route('/api/facilities/<facility_id>', methods=['PUT'])
def update_facility(facility_id):
    """Update an existing facility."""
    if not request.json:
        return jsonify({"error": "JSON data required"}), 400
    
    data = load_data()
    
    for i, feature in enumerate(data.get('features', [])):
        if feature['properties'].get('id') == facility_id:
            # Update properties
            data['features'][i] = request.json
            save_data(data)
            return jsonify({
                "message": "Facility updated successfully",
                "facility": data['features'][i]
            })
    
    return jsonify({"error": "Facility not found"}), 404


@app.route('/api/facilities/<facility_id>', methods=['DELETE'])
def delete_facility(facility_id):
    """Delete a facility."""
    data = load_data()
    
    for i, feature in enumerate(data.get('features', [])):
        if feature['properties'].get('id') == facility_id:
            deleted = data['features'].pop(i)
            save_data(data)
            return jsonify({
                "message": "Facility deleted successfully",
                "facility": deleted
            })
    
    return jsonify({"error": "Facility not found"}), 404


@app.route('/api/contacts/<facility_id>', methods=['GET'])
def get_contacts(facility_id):
    """Get contacts for a specific facility."""
    data = load_data()
    
    for feature in data.get('features', []):
        if feature['properties'].get('id') == facility_id:
            contacts = feature['properties'].get('contacts', {})
            return jsonify({
                "facility_id": facility_id,
                "contacts": contacts
            })
    
    return jsonify({"error": "Facility not found"}), 404


@app.route('/api/emergency/<facility_id>', methods=['GET'])
def get_emergency_procedures(facility_id):
    """Get emergency procedures for a specific facility."""
    data = load_data()
    
    for feature in data.get('features', []):
        if feature['properties'].get('id') == facility_id:
            procedures = feature['properties'].get('emergency_procedures', {})
            return jsonify({
                "facility_id": facility_id,
                "emergency_procedures": procedures
            })
    
    return jsonify({"error": "Facility not found"}), 404


# =============================================================================
# FILE UPLOAD ENDPOINTS
# =============================================================================

@app.route('/api/upload/csv', methods=['POST'])
def upload_csv():
    """Upload CSV file and convert to GeoJSON."""
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    if not file.filename.endswith('.csv'):
        return jsonify({"error": "Only CSV files are supported"}), 400
    
    try:
        import pandas as pd
        from io import StringIO
        
        # Read CSV content
        content = file.read().decode('utf-8')
        df = pd.read_csv(StringIO(content))
        
        # Convert to GeoJSON
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
                    "type": str(row.get('type', 'warehouse')),
                    "address": str(row['address']),
                    "size_sqft": int(row.get('size_sqft', 10000)),
                    "employees": int(row.get('employees', 50)),
                    "contacts": {
                        "facility_manager": {
                            "name": str(row.get('manager_name', 'Manager')),
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
                    "equipment": ["HVAC System", "Fire Suppression System", "Security System"],
                    "emergency_procedures": {
                        "power_outage": ["Check main breaker", "Contact facility manager", "Activate backup power"],
                        "fire_alarm": ["Evacuate immediately", "Call 911", "Meet at assembly point"]
                    }
                }
            }
            features.append(feature)
        
        geojson = {"type": "FeatureCollection", "features": features}
        
        return jsonify({
            "message": f"Successfully imported {len(features)} facilities",
            "count": len(features),
            "data": geojson
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/template', methods=['GET'])
def get_template():
    """Return CSV template format."""
    template = {
        "columns": [
            {"name": "id", "required": True, "example": "FAC-001"},
            {"name": "name", "required": True, "example": "Main Warehouse"},
            {"name": "type", "required": True, "example": "warehouse"},
            {"name": "address", "required": True, "example": "123 Main St Chicago IL"},
            {"name": "latitude", "required": True, "example": "41.8781"},
            {"name": "longitude", "required": True, "example": "-87.6298"},
            {"name": "size_sqft", "required": False, "example": "50000"},
            {"name": "employees", "required": False, "example": "120"},
            {"name": "manager_name", "required": False, "example": "John Smith"},
            {"name": "manager_email", "required": False, "example": "j.smith@company.com"},
            {"name": "manager_phone", "required": False, "example": "312-555-1234"}
        ],
        "sample_csv": "id,name,type,address,latitude,longitude,size_sqft,employees,manager_name,manager_email,manager_phone\\nFAC-001,Main Warehouse,warehouse,123 Main St Chicago IL,41.8781,-87.6298,50000,120,John Smith,j.smith@company.com,312-555-1234"
    }
    return jsonify(template)


# =============================================================================
# DATA EXPORT ENDPOINTS
# =============================================================================

@app.route('/api/export/csv', methods=['GET'])
def export_csv():
    """Export all facilities as CSV."""
    data = load_data()
    features = data.get('features', [])
    
    # Build CSV content
    headers = ['id', 'name', 'type', 'address', 'latitude', 'longitude', 'size_sqft', 'employees', 
               'manager_name', 'manager_email', 'manager_phone', 'it_name', 'it_email', 'it_phone']
    
    rows = [','.join(headers)]
    
    for f in features:
        p = f['properties']
        coords = f['geometry']['coordinates']
        contacts = p.get('contacts', {})
        manager = contacts.get('facility_manager', {})
        it = contacts.get('it_support', {})
        
        row = [
            str(p.get('id', '')),
            str(p.get('name', '')).replace(',', ';'),
            str(p.get('type', '')),
            str(p.get('address', '')).replace(',', ';'),
            str(coords[1]),  # latitude
            str(coords[0]),  # longitude
            str(p.get('size_sqft', '')),
            str(p.get('employees', '')),
            str(manager.get('name', '')),
            str(manager.get('email', '')),
            str(manager.get('phone', '')),
            str(it.get('name', '')),
            str(it.get('email', '')),
            str(it.get('phone', ''))
        ]
        rows.append(','.join(row))
    
    csv_content = '\n'.join(rows)
    
    from flask import Response
    return Response(
        csv_content,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=facilities_export.csv'}
    )


@app.route('/api/export/contacts', methods=['GET'])
def export_contacts():
    """Export all contacts as CSV."""
    data = load_data()
    features = data.get('features', [])
    
    headers = ['facility_id', 'facility_name', 'role', 'name', 'email', 'phone']
    rows = [','.join(headers)]
    
    for f in features:
        p = f['properties']
        contacts = p.get('contacts', {})
        
        for role, contact in contacts.items():
            row = [
                str(p.get('id', '')),
                str(p.get('name', '')).replace(',', ';'),
                role.replace('_', ' ').title(),
                str(contact.get('name', '')),
                str(contact.get('email', '')),
                str(contact.get('phone', ''))
            ]
            rows.append(','.join(row))
    
    csv_content = '\n'.join(rows)
    
    from flask import Response
    return Response(
        csv_content,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=contacts_export.csv'}
    )


# =============================================================================
# TICKET SYSTEM ENDPOINTS
# =============================================================================

# In-memory ticket storage (in production, use a database)
tickets = []
ticket_counter = 1

@app.route('/api/tickets', methods=['GET'])
def get_tickets():
    """Get all tickets with optional filtering."""
    facility_id = request.args.get('facility_id')
    status = request.args.get('status')
    
    result = tickets.copy()
    
    if facility_id:
        result = [t for t in result if t['facility_id'] == facility_id]
    if status:
        result = [t for t in result if t['status'] == status]
    
    return jsonify({
        "count": len(result),
        "tickets": result
    })


@app.route('/api/tickets', methods=['POST'])
def create_ticket():
    """Create a new maintenance ticket."""
    global ticket_counter
    
    if not request.json:
        return jsonify({"error": "JSON data required"}), 400
    
    required = ['facility_id', 'title', 'category']
    missing = [f for f in required if f not in request.json]
    if missing:
        return jsonify({"error": f"Missing required fields: {missing}"}), 400
    
    from datetime import datetime
    
    ticket = {
        "id": f"TKT-{ticket_counter:04d}",
        "facility_id": request.json['facility_id'],
        "title": request.json['title'],
        "description": request.json.get('description', ''),
        "category": request.json['category'],
        "priority": request.json.get('priority', 'medium'),
        "status": "open",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    
    tickets.append(ticket)
    ticket_counter += 1
    
    return jsonify({
        "message": "Ticket created successfully",
        "ticket": ticket
    }), 201


@app.route('/api/tickets/<ticket_id>', methods=['GET'])
def get_ticket(ticket_id):
    """Get a single ticket by ID."""
    for ticket in tickets:
        if ticket['id'] == ticket_id:
            return jsonify(ticket)
    return jsonify({"error": "Ticket not found"}), 404


@app.route('/api/tickets/<ticket_id>', methods=['PUT'])
def update_ticket(ticket_id):
    """Update a ticket status or details."""
    from datetime import datetime
    
    for ticket in tickets:
        if ticket['id'] == ticket_id:
            if request.json.get('status'):
                ticket['status'] = request.json['status']
            if request.json.get('priority'):
                ticket['priority'] = request.json['priority']
            if request.json.get('description'):
                ticket['description'] = request.json['description']
            ticket['updated_at'] = datetime.now().isoformat()
            
            return jsonify({
                "message": "Ticket updated",
                "ticket": ticket
            })
    
    return jsonify({"error": "Ticket not found"}), 404


@app.route('/api/tickets/stats', methods=['GET'])
def ticket_stats():
    """Get ticket statistics."""
    stats = {
        "total": len(tickets),
        "by_status": {},
        "by_priority": {},
        "by_category": {}
    }
    
    for t in tickets:
        status = t.get('status', 'unknown')
        priority = t.get('priority', 'unknown')
        category = t.get('category', 'unknown')
        
        stats['by_status'][status] = stats['by_status'].get(status, 0) + 1
        stats['by_priority'][priority] = stats['by_priority'].get(priority, 0) + 1
        stats['by_category'][category] = stats['by_category'].get(category, 0) + 1
    
    return jsonify(stats)


# =============================================================================
# RUN SERVER
# =============================================================================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)
