<<<<<<< HEAD
from fastapi import FastAPI, File, UploadFile
=======
from fastapi import FastAPI
>>>>>>> 3f4ba639343ed8b71677c6902aba9146f9ea72ad
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import os
import anthropic
<<<<<<< HEAD
import base64

=======
>>>>>>> 3f4ba639343ed8b71677c6902aba9146f9ea72ad

app = FastAPI()

# -------------------------
# GLOBAL STATE (lightweight)
# -------------------------
current_temperature = None
threshold_value = 15.0
action = "LED"

client = anthropic.Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

# -------------------------
# DATA MODELS
# -------------------------
class SensorData(BaseModel):
    temperature: float

class Settings(BaseModel):
    threshold: float
    action: str

# -------------------------
# SENSOR ENDPOINT (ESP32)
# -------------------------
@app.post("/check")
def check_temperature(data: SensorData):
    global current_temperature
    current_temperature = data.temperature

    prompt = f"""
    Temperature is {data.temperature}°C.
    Threshold is {threshold_value}°C.
    If temperature >= threshold respond ONLY with:
    OVERHEAT
    Else respond ONLY with:
    NORMAL
    """

    msg = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=5,
        messages=[{"role": "user", "content": prompt}]
    )

    result = msg.content[0].text.strip()

    return {
        "temperature": data.temperature,
        "overheat": result == "OVERHEAT",
        "action": action
    }

# -------------------------
# SETTINGS FROM GUI
# -------------------------
@app.post("/settings")
def update_settings(data: Settings):
    global threshold_value, action
    threshold_value = data.threshold
    action = data.action
    return {"status": "updated"}

# -------------------------
# LIVE DATA FOR GUI
# -------------------------
@app.get("/status")
def get_status():
    return {
        "temperature": current_temperature,
        "threshold": threshold_value,
        "action": action
    }

# -------------------------
# SIMPLE GUI
# -------------------------
@app.get("/", response_class=HTMLResponse)
def gui():
    return """
<!DOCTYPE html>
<html>
<head>
  <title>ESP32 Temperature Monitor</title>
  <style>
    body { font-family: Arial; background:#111; color:#eee; text-align:center; }
    .box { background:#222; padding:20px; width:300px; margin:auto; border-radius:10px; }
    input, select, button { width:100%; padding:8px; margin:5px; }
  </style>
</head>
<body>
  <h2>🌡 ESP32 Temperature Monitor</h2>

  <div class="box">
    <h3>Current Temperature</h3>
    <h1 id="temp">-- °C</h1>

    <h3>Threshold (°C)</h3>
    <input type="number" id="threshold" />

    <h3>Action</h3>
    <select id="action">
      <option value="LED">LED</option>
      <option value="ALERT">Alert</option>
    </select>

    <button onclick="save()">Save Settings</button>
  </div>

<script>
async function fetchStatus() {
  const res = await fetch('/status');
  const data = await res.json();
  document.getElementById('temp').innerText =
    data.temperature !== null ? data.temperature + " °C" : "--";
  document.getElementById('threshold').value = data.threshold;
  document.getElementById('action').value = data.action;
}

async function save() {
  await fetch('/settings', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      threshold: parseFloat(document.getElementById('threshold').value),
      action: document.getElementById('action').value
    })
  });
  alert("Settings saved!");
}

setInterval(fetchStatus, 2000);
fetchStatus();
<<<<<<< HEAD

@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):

    image_bytes = await file.read()
    encoded_image = base64.b64encode(image_bytes).decode("utf-8")

    message = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=300,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": encoded_image
                        }
                    },
                    {
                        "type": "text",
                        "text": "Analyze this plant. Tell if it is healthy or diseased and suggest action."
                    }
                ]
            }
        ]
    )

    result = message.content[0].text

    return {"analysis": result}

=======
>>>>>>> 3f4ba639343ed8b71677c6902aba9146f9ea72ad
</script>
</body>
</html>
"""