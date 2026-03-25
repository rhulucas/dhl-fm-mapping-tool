# Faster 99 - Facility Management Mapping Tool

An AI-powered facility management tool built with Mapbox GL JS, Three.js, and OpenAI — demonstrating full-stack development with Azure cloud deployment.

## Live Demo

- **Frontend**: https://zealous-beach-008e8110f.2.azurestaticapps.net

> Demo login: `demo@faster99.com` / `faster99demo` (or register with any email)

**Scan to open on mobile:**

![QR Code](https://api.qrserver.com/v1/create-qr-code/?size=160x160&data=https://zealous-beach-008e8110f.2.azurestaticapps.net)

## Features

### 🤖 AI-Powered Features (OpenAI GPT-4o)
- **Smart Ticket Auto-Fill** — describe a problem in plain English, AI suggests category, priority, title, and step-by-step repair instructions
- **Operations Summary** — one-click AI summary of current facility and ticket status for daily briefings
- **Equipment Fault Diagnosis** — click any faulty 3D equipment, AI identifies likely causes, immediate actions, and estimated downtime

### 🗺️ Interactive Mapping
- Interactive map with 100 facility locations across the US
- Search and filter by facility type
- Click-to-zoom facility navigation

### 🏢 3D Facility Visualization
- Three.js powered 3D floor plans
- Interactive equipment inspection with status indicators
- Real-time equipment status display (Operational / Maintenance / Fault)
- One-click issue reporting from 3D view

### 🎫 Work Order Management
- Create and track maintenance tickets
- Status workflow: Open → In Progress → Resolved
- Filter and search tickets by status, title, facility, category
- Direct navigation from ticket to facility on map

### 📊 Dashboard & Analytics
- Facility statistics overview (total facilities, sqft, employees, tickets)
- Chart.js donut and bar charts (facility types, ticket status, top states)
- Equipment inventory tracking across all facilities
- Maintenance calendar with scheduled tasks
- Data import/export (CSV)

### 📱 Mobile Responsive
- Optimized layout for iPhone and Android
- Map on top, sidebar below for easy one-hand navigation
- Scrollable tabs and touch-friendly buttons
- Tested on iPhone 11

### 🌙 Dark / Light Mode
- One-click toggle between dark and light theme
- Preference saved automatically (persists after refresh)

### 🔔 Browser Notifications
- Enable alerts with one click
- Desktop notification when a ticket is created
- Notifies when another user creates a ticket (via real-time sync)

### 🔐 Authentication & Database
- Real user authentication via Supabase Auth (email/password)
- Persistent ticket storage in Supabase PostgreSQL database
- Tickets shared across all users in real-time
- Role-based access (Administrator, Manager, Technician, Viewer)

### 🔧 Technical Features
- RESTful API backend with AI endpoints
- Full-stack Azure + Supabase deployment
- CI/CD with GitHub Actions

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | HTML5, CSS3, JavaScript |
| **Mapping** | Mapbox GL JS, GeoJSON |
| **3D Graphics** | Three.js, OrbitControls |
| **AI** | OpenAI GPT-4o-mini (ticket suggestions, diagnosis, summaries) |
| **Charts** | Chart.js (donut & bar charts) |
| **Backend** | Python, Flask, Gunicorn |
| **Database** | Supabase (PostgreSQL, Auth, Realtime) |
| **Cloud** | Azure Static Web Apps, Azure App Service |
| **CI/CD** | GitHub Actions |

## AI Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/ai/ticket-suggest` | Auto-fill ticket from description |
| POST | `/api/ai/dashboard-summary` | Generate operations summary |
| POST | `/api/ai/equipment-diagnosis` | Diagnose equipment fault |

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

## Local Development

### Prerequisites

- Python 3.11+
- A Mapbox account (free tier available)
- An OpenAI API key (for AI features)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/rhulucas/dhl-fm-mapping-tool.git
   cd dhl-fm-mapping-tool
   ```

2. Install API dependencies:
   ```bash
   cd api
   pip install -r requirements.txt
   ```

3. Start the API with your OpenAI key:
   ```bash
   OPENAI_API_KEY=your_key_here python app.py
   ```
   API will be available at http://localhost:5000

4. In a separate terminal, start the frontend:
   ```bash
   python3 -m http.server 8080
   ```

5. Open http://localhost:8080

> **Note:** The OpenAI API key is never stored in any file. It is passed as an environment variable only. For Azure deployment, set `OPENAI_API_KEY` under App Service → Environment Variables.

## Project Structure

```
├── api/                    # Backend API
│   ├── app.py              # Flask application (facilities + AI endpoints)
│   ├── data.json           # Facility data
│   └── requirements.txt    # Python dependencies
├── .github/workflows/      # CI/CD pipelines
├── index.html              # Frontend application
├── style.css               # Styles
├── data.json               # Local data backup
└── generate_facilities.py  # Data generation script
```

## Skills Demonstrated

- **AI Integration**: OpenAI GPT-4o API, prompt engineering, structured JSON responses
- **Frontend Development**: JavaScript, HTML5, CSS3, responsive design
- **3D Graphics**: Three.js scene creation, interactive objects, raycasting
- **Mapping**: Mapbox GL JS, GeoJSON data handling, custom markers
- **Backend Development**: Python Flask, RESTful API design
- **Cloud Deployment**: Azure Static Web Apps, Azure App Service
- **Database Integration**: Supabase Auth, PostgreSQL, real-time subscriptions
- **Notifications**: Browser Notification API for real-time ticket alerts
- **DevOps**: CI/CD with GitHub Actions, automated deployments
- **UX Design**: Intuitive navigation, status workflows, data visualization

## License

MIT
