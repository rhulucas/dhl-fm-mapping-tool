# Faster 99 - Facility Management Mapping Tool

An interactive facility management mapping tool built with Mapbox GL JS, demonstrating full-stack development with Azure cloud deployment.

## Live Demo

- **Frontend**: https://zealous-beach-008e8110f.2.azurestaticapps.net
- **API**: https://faster99-api-eafbb2bah6hnguc4.eastus2-01.azurewebsites.net

## Features

- Interactive map with 100 facility locations across the US
- Facility details: contacts, equipment, emergency procedures
- Search and filter functionality
- Collapsible information panels
- RESTful API backend
- Full-stack Azure deployment (Static Web Apps + App Service)

## Tech Stack

- **Frontend**: HTML, CSS, JavaScript, Mapbox GL JS
- **Backend**: Python, Flask, Gunicorn
- **Cloud**: Azure Static Web Apps, Azure App Service
- **CI/CD**: GitHub Actions

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

- JavaScript & Python development
- API integration and data modeling
- Mapbox mapping tools
- Cloud deployment (Azure)
- CI/CD with GitHub Actions
- RESTful API design

## License

MIT
