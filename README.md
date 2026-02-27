# Faster 99 - Facility Management Mapping Tool

An interactive facility management mapping tool built with Mapbox GL JS and Three.js, demonstrating full-stack development with Azure cloud deployment.

## Live Demo

- **Frontend**: https://zealous-beach-008e8110f.2.azurestaticapps.net

> Note: Demo works fully offline - facility data loads from local backup if API is unavailable.

## Features

### 🗺️ Interactive Mapping
- Interactive map with 100 facility locations across the US
- Search and filter by facility type
- Click-to-zoom facility navigation

### 🏢 3D Facility Visualization  
- Three.js powered 3D floor plans
- Interactive equipment inspection
- Real-time equipment status display
- One-click issue reporting from 3D view

### 🎫 Work Order Management
- Create and track maintenance tickets
- Status workflow: Open → In Progress → Resolved
- Filter tickets by status
- Direct navigation from ticket to facility on map

### 📊 Dashboard & Analytics
- Facility statistics overview
- Equipment inventory tracking
- Maintenance calendar with scheduled tasks
- Data import/export (CSV)

### 🔧 Technical Features
- RESTful API backend
- Offline support with localStorage fallback
- Role-based demo login
- Full-stack Azure deployment

## Tech Stack

- **Frontend**: HTML, CSS, JavaScript, Mapbox GL JS, Three.js
- **Backend**: Python, Flask, Gunicorn
- **Cloud**: Azure Static Web Apps, Azure App Service
- **CI/CD**: GitHub Actions
- **Data**: GeoJSON, localStorage (offline support)

## Local Development

### Prerequisites

- Python 3.11+
- A Mapbox account (free tier available)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/rhulucas/dhl-fm-mapping-tool.git
   cd dhl-fm-mapping-tool
   ```

2. Get a Mapbox token from https://mapbox.com and replace it in `index.html`:
   ```javascript
   mapboxgl.accessToken = 'YOUR_MAPBOX_TOKEN';
   ```

3. For local development, modify `index.html` to use local data:
   ```javascript
   // Change this line:
   fetch(API_URL + '/api/facilities')
   // To:
   fetch('./data.json')
   ```

4. Start a local server:
   ```bash
   python3 -m http.server 8080
   ```

5. Open http://localhost:8080

### Running the API locally

```bash
cd api
pip install -r requirements.txt
python app.py
```

API will be available at http://localhost:5000

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| GET | `/api/facilities` | List all facilities |
| GET | `/api/facilities/<id>` | Get single facility |
| GET | `/api/facilities/stats` | Get statistics |
| GET | `/api/facilities/search?q=<query>` | Search facilities |
| POST | `/api/facilities` | Create facility |
| PUT | `/api/facilities/<id>` | Update facility |
| DELETE | `/api/facilities/<id>` | Delete facility |

## Project Structure

```
├── api/                    # Backend API
│   ├── app.py              # Flask application
│   ├── data.json           # Facility data
│   └── requirements.txt    # Python dependencies
├── .github/workflows/      # CI/CD pipelines
├── index.html              # Frontend application
├── style.css               # Styles
├── data.json               # Local data backup
└── generate_facilities.py  # Data generation script
```

## Skills Demonstrated

- **Frontend Development**: JavaScript, HTML5, CSS3, responsive design
- **3D Graphics**: Three.js scene creation, interactive objects, raycasting
- **Mapping**: Mapbox GL JS, GeoJSON data handling, custom markers
- **Backend Development**: Python Flask, RESTful API design
- **Cloud Deployment**: Azure Static Web Apps, Azure App Service
- **DevOps**: CI/CD with GitHub Actions, automated deployments
- **UX Design**: Intuitive navigation, status workflows, data visualization
- **Offline Support**: localStorage fallback, graceful degradation

## License

MIT
