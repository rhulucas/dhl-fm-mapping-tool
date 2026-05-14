"""
Faster 99 - Facility Management API
====================================
RESTful API backend for facility management system.
Designed for deployment on Azure App Service.
"""

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import json
import os
from urllib.parse import urlparse
import psycopg2
import psycopg2.extras

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend access

# Load facility data
DATA_FILE = os.path.join(os.path.dirname(__file__), 'data.json')

# =============================================================================
# POSTGRESQL DATABASE
# =============================================================================

def _get_first_env_with_prefix(prefix):
    for key, value in os.environ.items():
        if key.startswith(prefix) and value:
            return value
    return None

def _parse_semicolon_connection_string(value):
    aliases = {
        'server': 'host',
        'host': 'host',
        'database': 'database',
        'dbname': 'database',
        'port': 'port',
        'user id': 'user',
        'userid': 'user',
        'user': 'user',
        'username': 'user',
        'password': 'password',
        'pwd': 'password',
        'ssl mode': 'sslmode',
        'sslmode': 'sslmode',
    }
    result = {}
    for part in value.split(';'):
        if '=' not in part:
            continue
        key, raw = part.split('=', 1)
        normalized = aliases.get(key.strip().lower())
        if normalized:
            result[normalized] = raw.strip()
    if 'port' in result:
        result['port'] = int(result['port'])
    return result

def _parse_database_url(value):
    parsed = urlparse(value)
    return {
        'host': parsed.hostname,
        'database': parsed.path.lstrip('/'),
        'user': parsed.username,
        'password': parsed.password,
        'port': parsed.port or 5432,
        'sslmode': 'require'
    }

def get_db_config():
    connection_string = (
        os.environ.get('DATABASE_URL') or
        os.environ.get('AZURE_POSTGRESQL_CONNECTIONSTRING') or
        os.environ.get('POSTGRESQLCONNSTR_DefaultConnection') or
        os.environ.get('CUSTOMCONNSTR_DefaultConnection') or
        _get_first_env_with_prefix('POSTGRESQLCONNSTR_') or
        _get_first_env_with_prefix('CUSTOMCONNSTR_')
    )

    if connection_string:
        if connection_string.startswith(('postgres://', 'postgresql://')):
            return _parse_database_url(connection_string)
        if ';' in connection_string:
            config = _parse_semicolon_connection_string(connection_string)
            config.setdefault('sslmode', 'require')
            return config
        return connection_string

    return {
        'host': os.environ.get('DB_HOST', 'rohu-db.postgres.database.azure.com'),
        'database': os.environ.get('DB_NAME', 'faster99_fm_db'),
        'user': os.environ.get('DB_USER', 'rohuadmin'),
        'password': os.environ.get('DB_PASSWORD', ''),
        'port': int(os.environ.get('DB_PORT', 5432)),
        'sslmode': os.environ.get('DB_SSLMODE', 'require')
    }

def get_db_connection():
    config = get_db_config()
    if isinstance(config, str):
        return psycopg2.connect(config)
    return psycopg2.connect(**config)

def ensure_tickets_table(conn):
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS tickets (
            id SERIAL PRIMARY KEY,
            facility_id VARCHAR(50) NOT NULL,
            title VARCHAR(255) NOT NULL,
            description TEXT DEFAULT '',
            category VARCHAR(50) NOT NULL,
            priority VARCHAR(20) DEFAULT 'medium',
            status VARCHAR(20) DEFAULT 'open',
            user_email VARCHAR(255),
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        )
    ''')
    conn.commit()
    cur.close()

def init_db():
    conn = get_db_connection()
    ensure_tickets_table(conn)
    conn.close()

try:
    init_db()
except Exception as e:
    print(f"DB init warning: {e}")

def format_ticket(row):
    return {
        "id": f"TKT-{row['id']:04d}",
        "db_id": row['id'],
        "facility_id": row['facility_id'],
        "title": row['title'],
        "description": row['description'] or '',
        "category": row['category'],
        "priority": row['priority'],
        "status": row['status'],
        "user_email": row.get('user_email', ''),
        "created_at": row['created_at'].isoformat() if row['created_at'] else None,
        "updated_at": row['updated_at'].isoformat() if row['updated_at'] else None
    }

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

def get_safe_db_status():
    config = get_db_config()
    if isinstance(config, str):
        if config.startswith(('postgres://', 'postgresql://')):
            parsed = _parse_database_url(config)
            return {
                'host': parsed.get('host'),
                'database': parsed.get('database'),
                'user': parsed.get('user'),
                'source': 'connection_string'
            }
        return {'source': 'connection_string'}
    return {
        'host': config.get('host'),
        'database': config.get('database'),
        'user': config.get('user'),
        'source': 'environment'
    }


# =============================================================================
# API ENDPOINTS
# =============================================================================

@app.route('/')
def index():
    """Serve the frontend."""
    index_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'index.html')
    return send_file(index_path)

@app.route('/style.css')
def style():
    """Serve the stylesheet."""
    css_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'style.css')
    return send_file(css_path, mimetype='text/css')

@app.route('/admin/tickets')
def admin_tickets_page():
    """Serve the protected admin ticket table."""
    admin_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'admin_tickets.html')
    return send_file(admin_path)

@app.route('/api/health/db', methods=['GET'])
def db_health():
    """Check PostgreSQL connectivity without exposing secrets."""
    status = get_safe_db_status()
    try:
        conn = get_db_connection()
        ensure_tickets_table(conn)
        cur = conn.cursor()
        cur.execute('SELECT COUNT(*) FROM tickets')
        ticket_count = cur.fetchone()[0]
        cur.close()
        conn.close()
        return jsonify({**status, 'ok': True, 'ticket_count': ticket_count})
    except Exception as e:
        return jsonify({**status, 'ok': False, 'error': str(e)}), 500


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

def require_admin_passcode():
    expected = os.environ.get('ADMIN_PASSCODE', 'faster99admin')
    provided = request.headers.get('X-Admin-Passcode', '')
    return bool(expected) and provided == expected

@app.route('/api/admin/tickets', methods=['GET'])
def admin_get_tickets():
    """Admin-only ticket table data."""
    if not require_admin_passcode():
        return jsonify({"error": "Admin passcode required"}), 401
    return get_tickets()

@app.route('/api/tickets', methods=['GET'])
def get_tickets():
    """Get all tickets with optional filtering."""
    facility_id = request.args.get('facility_id')
    status = request.args.get('status')

    try:
        conn = get_db_connection()
        ensure_tickets_table(conn)
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        query = "SELECT * FROM tickets WHERE 1=1"
        params = []
        if facility_id:
            query += " AND facility_id = %s"
            params.append(facility_id)
        if status:
            query += " AND status = %s"
            params.append(status)
        query += " ORDER BY created_at DESC"
        cur.execute(query, params)
        rows = cur.fetchall()
        cur.close()
        conn.close()
        result = [format_ticket(r) for r in rows]
        return jsonify({"count": len(result), "tickets": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/tickets', methods=['POST'])
def create_ticket():
    """Create a new maintenance ticket."""
    if not request.json:
        return jsonify({"error": "JSON data required"}), 400

    required = ['facility_id', 'title', 'category']
    missing = [f for f in required if f not in request.json]
    if missing:
        return jsonify({"error": f"Missing required fields: {missing}"}), 400

    try:
        conn = get_db_connection()
        ensure_tickets_table(conn)
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(
            '''INSERT INTO tickets (facility_id, title, description, category, priority, status, user_email)
               VALUES (%s, %s, %s, %s, %s, 'open', %s) RETURNING *''',
            (
                request.json['facility_id'],
                request.json['title'],
                request.json.get('description', ''),
                request.json['category'],
                request.json.get('priority', 'medium'),
                request.json.get('user_email', '')
            )
        )
        row = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        ticket = format_ticket(row)
        return jsonify({"message": "Ticket created successfully", "ticket": ticket}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/tickets/<ticket_id>', methods=['GET'])
def get_ticket(ticket_id):
    """Get a single ticket by ID."""
    try:
        db_id = int(ticket_id.split('-')[1])
        conn = get_db_connection()
        ensure_tickets_table(conn)
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT * FROM tickets WHERE id = %s", (db_id,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if not row:
            return jsonify({"error": "Ticket not found"}), 404
        return jsonify(format_ticket(row))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/tickets/<ticket_id>', methods=['PUT'])
def update_ticket(ticket_id):
    """Update a ticket status or details."""
    try:
        db_id = int(ticket_id.split('-')[1])
        conn = get_db_connection()
        ensure_tickets_table(conn)
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        updates = []
        params = []
        if request.json.get('status'):
            updates.append("status = %s")
            params.append(request.json['status'])
        if request.json.get('priority'):
            updates.append("priority = %s")
            params.append(request.json['priority'])
        if request.json.get('description'):
            updates.append("description = %s")
            params.append(request.json['description'])
        updates.append("updated_at = NOW()")
        params.append(db_id)
        cur.execute(f"UPDATE tickets SET {', '.join(updates)} WHERE id = %s RETURNING *", params)
        row = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        if not row:
            return jsonify({"error": "Ticket not found"}), 404
        return jsonify({"message": "Ticket updated", "ticket": format_ticket(row)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/tickets/<ticket_id>', methods=['DELETE'])
def delete_ticket(ticket_id):
    """Delete a ticket by ID."""
    try:
        db_id = int(ticket_id.split('-')[1])
        conn = get_db_connection()
        ensure_tickets_table(conn)
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("DELETE FROM tickets WHERE id = %s RETURNING *", (db_id,))
        row = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        if not row:
            return jsonify({"error": "Ticket not found"}), 404
        return jsonify({"message": "Ticket deleted", "ticket": format_ticket(row)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =============================================================================
# AI ENDPOINTS  (uses urllib — no external SDK required)
# =============================================================================

import urllib.request
import urllib.error

def get_openai_key():
    return (os.environ.get('OPENAI_API_KEY') or
            os.environ.get('openai_api_key') or
            os.environ.get('faster99_openai_api'))


def call_openai(prompt, max_tokens=400, json_mode=True):
    """Call OpenAI chat completions via urllib (no SDK needed)."""
    api_key = get_openai_key()
    if not api_key:
        raise ValueError("API key not configured")

    payload = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.3
    }
    if json_mode:
        payload["response_format"] = {"type": "json_object"}

    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        'https://api.openai.com/v1/chat/completions',
        data=data,
        headers={
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        result = json.loads(resp.read().decode('utf-8'))
        return result['choices'][0]['message']['content']

def fallback_equipment_diagnosis(equipment_name, status):
    """Provide a deterministic diagnosis when OpenAI is not configured."""
    name = (equipment_name or '').lower()
    if 'conveyor' in name:
        return {
            "likely_causes": [
                "Motor overload, jammed belt, or misaligned rollers",
                "Photo eye or limit switch blocked by debris",
                "Emergency stop, VFD fault, or power interruption"
            ],
            "immediate_actions": [
                "Lock out the conveyor and inspect the belt path for jams",
                "Check sensors, guards, and emergency stop status",
                "Review controller/VFD fault codes before restarting"
            ],
            "estimated_downtime": "1-3 hours",
            "severity": "high" if status == "fault" else "medium",
            "source": "local fallback"
        }
    if 'forklift' in name or 'charger' in name:
        return {
            "likely_causes": [
                "Loose charging connector or damaged cable",
                "Battery temperature, voltage, or cell imbalance fault",
                "Charger breaker, fuse, or input power issue"
            ],
            "immediate_actions": [
                "Inspect connector pins, cable jacket, and charger display",
                "Confirm input breaker is on and no fault code is active",
                "Move the forklift to a backup charger if available"
            ],
            "estimated_downtime": "30 minutes-2 hours",
            "severity": "medium",
            "source": "local fallback"
        }
    return {
        "likely_causes": [
            "Power supply, control signal, or sensor fault",
            "Mechanical wear, blockage, or loose connection",
            "Recent maintenance or configuration change"
        ],
        "immediate_actions": [
            "Secure the area and confirm the equipment is safe to inspect",
            "Check power, indicators, alarms, and recent ticket history",
            "Escalate to maintenance if the issue cannot be cleared safely"
        ],
        "estimated_downtime": "1-4 hours",
        "severity": "high" if status == "fault" else "medium",
        "source": "local fallback"
    }


@app.route('/api/ai/debug', methods=['GET'])
def ai_debug():
    """Debug: check if AI key is configured."""
    key = get_openai_key()
    return jsonify({
        "key_set": bool(key),
        "key_prefix": key[:10] + "..." if key else None
    })


@app.route('/api/ai/ticket-suggest', methods=['POST'])
def ai_ticket_suggest():
    """AI suggests ticket category, priority, and repair steps from description."""
    if not get_openai_key():
        return jsonify({"error": "AI service not configured"}), 503

    body = request.get_json() or {}
    description = body.get('description', '').strip()
    facility_id = body.get('facility_id', 'unknown')

    if not description:
        return jsonify({"error": "description is required"}), 400

    prompt = f"""You are a facility management expert. A technician at facility {facility_id} reported:
"{description}"

Respond in JSON with these fields:
- category: one of [hvac, electrical, plumbing, structural, safety, equipment, it, cleaning, other]
- priority: one of [low, medium, high, critical]
- title: a concise ticket title (max 8 words)
- steps: list of 3-5 recommended repair/inspection steps

Return only valid JSON, no extra text."""

    try:
        result = call_openai(prompt, max_tokens=400, json_mode=True)
        return jsonify(json.loads(result))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/ai/dashboard-summary', methods=['POST'])
def ai_dashboard_summary():
    """AI generates a plain-English summary of current facility & ticket stats."""
    if not get_openai_key():
        return jsonify({"error": "AI service not configured"}), 503

    body = request.get_json() or {}
    stats = body.get('stats', {})

    prompt = f"""You are a facility operations analyst. Here are today's stats:
{stats}

Write a concise 2-3 sentence operations summary for a facility manager.
Highlight anything that needs attention. Be direct and professional.
Return only the summary text, no JSON."""

    try:
        summary = call_openai(prompt, max_tokens=200, json_mode=False)
        return jsonify({"summary": summary.strip()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/ai/equipment-diagnosis', methods=['POST'])
def ai_equipment_diagnosis():
    """AI diagnoses equipment issues and suggests repair actions."""
    body = request.get_json() or {}
    equipment_name = body.get('name', 'Unknown Equipment')
    status = body.get('status', 'fault')
    facility_id = body.get('facility_id', 'unknown')

    if not get_openai_key():
        result = fallback_equipment_diagnosis(equipment_name, status)
        result["note"] = "OpenAI key is not configured, so this is a local rules-based diagnosis."
        return jsonify(result)

    prompt = f"""You are a facility maintenance expert. Equipment report:
- Facility: {facility_id}
- Equipment: {equipment_name}
- Status: {status}

Respond in JSON with:
- likely_causes: list of 2-3 most probable causes
- immediate_actions: list of 2-3 actions to take now
- estimated_downtime: estimated repair time (e.g. "2-4 hours", "1-2 days")
- severity: one of [low, medium, high, critical]

Return only valid JSON, no extra text."""

    try:
        result = call_openai(prompt, max_tokens=400, json_mode=True)
        return jsonify(json.loads(result))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/tickets/stats', methods=['GET'])
def ticket_stats():
    """Get ticket statistics."""
    try:
        conn = get_db_connection()
        ensure_tickets_table(conn)
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT COUNT(*) as total FROM tickets")
        total = cur.fetchone()['total']
        cur.execute("SELECT status, COUNT(*) as count FROM tickets GROUP BY status")
        by_status = {r['status']: r['count'] for r in cur.fetchall()}
        cur.execute("SELECT priority, COUNT(*) as count FROM tickets GROUP BY priority")
        by_priority = {r['priority']: r['count'] for r in cur.fetchall()}
        cur.execute("SELECT category, COUNT(*) as count FROM tickets GROUP BY category")
        by_category = {r['category']: r['count'] for r in cur.fetchall()}
        cur.close()
        conn.close()
        return jsonify({"total": total, "by_status": by_status, "by_priority": by_priority, "by_category": by_category})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =============================================================================
# RUN SERVER
# =============================================================================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)
