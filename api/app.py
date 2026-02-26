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
# RUN SERVER
# =============================================================================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)
