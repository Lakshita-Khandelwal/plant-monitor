# 🌱 AI Plant Monitor

A real-time plant monitoring system that uses IoT sensors and Claude AI to analyze plant health.

## Features
- 📸 Image capture from IoT device
- 💧 Soil moisture monitoring
- 🤖 AI-powered plant health analysis using Claude
- ⚡ Real-time dashboard updates
- 📊 Historical data tracking

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Edit `.env` file with your credentials:
```env
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_service_key
CLAUDE_API_KEY=your_anthropic_api_key
```

### 3. Configure Frontend
Edit `static/app.js` lines 4-5:
```javascript
const supabaseUrl = 'https://xxxxx.supabase.co'
const supabaseKey = 'your_supabase_anon_key'
```
**Note:** Use your Supabase **anon/public** key here (safe to expose)

### 4. Setup Supabase

Create a table named `plant_logs`:
```sql
CREATE TABLE plant_logs (
  id BIGSERIAL PRIMARY KEY,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  moisture TEXT NOT NULL,
  image_url TEXT NOT NULL,
  claude_advice TEXT NOT NULL
);

-- Enable Realtime
ALTER TABLE plant_logs REPLICA IDENTITY FULL;
```

Create a storage bucket named `plants`:
- Go to Storage in Supabase dashboard
- Create new bucket called `plants`
- Make it **public**

Enable Realtime:
- Go to Database → Replication
- Enable replication for `plant_logs` table

### 5. Run the Server
```bash
uvicorn main:app --reload
# or using the virtual environment:
.venv/bin/python -m uvicorn main:app --reload
```

### 6. View Dashboard
Open browser to: **http://localhost:8000**

## API Endpoints

### `POST /upload`
Upload plant data from IoT device
- **Form Data:**
  - `moisture` (string): Moisture percentage
  - `image` (file): Plant photo (JPEG)
- **Response:** Success status with log ID

### `GET /`
Serves the web dashboard

### `GET /health`
Health check endpoint

## Tech Stack
- **Backend:** FastAPI
- **AI:** Claude 3.7 Sonnet
- **Database:** Supabase (PostgreSQL + Realtime)
- **Storage:** Supabase Storage
- **Frontend:** Vanilla JS + Tailwind CSS
