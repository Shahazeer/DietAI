# 🧠 Dietician Agent - Complete Learning Guide

> A comprehensive guide to understanding how this AI-powered dietician application was built using Ollama, FastAPI, MongoDB, and React.

---

## 📚 Table of Contents

1. [Project Overview](#1-project-overview)
2. [Architecture](#2-architecture)
3. [Technology Stack](#3-technology-stack)
4. [Backend Deep Dive](#4-backend-deep-dive)
5. [Ollama Integration](#5-ollama-integration)
6. [Database Design](#6-database-design)
7. [API Endpoints](#7-api-endpoints)
8. [Frontend Overview](#8-frontend-overview)
9. [How to Explain This Project](#9-how-to-explain-this-project)

---

## 1. Project Overview

### What Does This Application Do?

The Dietician Agent is an **AI-powered health assistant** that:

1. **Analyzes lab reports** using computer vision (OCR)
2. **Identifies health issues** from extracted lab values
3. **Generates personalized 7-day meal plans** based on health conditions
4. **Tracks patient progress** over time to improve recommendations

### Key Innovation

This project runs **entirely on local hardware** using Ollama - no cloud APIs, no subscription costs, and complete data privacy.

---

## 2. Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER'S DEVICE                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────┐   │
│  │   Frontend   │───▶│   Backend    │───▶│   MongoDB        │   │
│  │   (React)    │    │   (FastAPI)  │    │   (Docker)       │   │
│  │   Port 5173  │    │   Port 8000  │    │   Port 27017     │   │
│  └──────────────┘    └──────────────┘    └──────────────────┘   │
│                             │                                    │
│                             ▼                                    │
│                    ┌──────────────────┐                         │
│                    │  Ollama Server   │◀── Windows Desktop      │
│                    │  (AI Models)     │    Port 11434           │
│                    │  - llava:7b      │                         │
│                    │  - mistral       │                         │
│                    └──────────────────┘                         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow

```
1. User uploads lab report (PDF/Image)
       ↓
2. Backend saves file, converts PDF to images
       ↓
3. Vision model (llava) extracts lab values via OCR
       ↓
4. Text model (mistral) analyzes health issues
       ↓
5. Text model generates 7-day personalized meal plan
       ↓
6. Results stored in MongoDB, displayed in React UI
```

---

## 3. Technology Stack

| Layer            | Technology         | Purpose                        |
| ---------------- | ------------------ | ------------------------------ |
| **Frontend**     | React + Vite       | User interface                 |
| **Backend**      | FastAPI (Python)   | REST API server                |
| **Database**     | MongoDB (Docker)   | Store patients, reports, plans |
| **AI Runtime**   | Ollama             | Run LLMs locally               |
| **Vision Model** | llava:7b           | Extract text from images       |
| **Text Model**   | mistral / llama3.2 | Generate analysis & plans      |

### Why These Technologies?

- **FastAPI**: Async Python framework, perfect for AI workloads
- **MongoDB**: Schema-less, handles varied lab report structures
- **Ollama**: Simple API for running open-source LLMs locally
- **React**: Modern, component-based UI

---

## 4. Backend Deep Dive

### Project Structure

```
backend/
├── app/
│   ├── config.py           # Environment variables
│   ├── main.py             # FastAPI app setup
│   ├── database/
│   │   └── mongodb.py      # Database connection
│   ├── models/
│   │   ├── patient.py      # Pydantic models for patients
│   │   ├── lab_report.py   # Models for lab data
│   │   └── diet_plan.py    # Models for meal plans
│   ├── routes/
│   │   ├── patients.py     # Patient CRUD endpoints
│   │   ├── reports.py      # Lab report upload/analysis
│   │   └── diet.py         # Diet plan generation
│   └── services/
│       ├── ollama_client.py    # Wrapper for Ollama API
│       ├── ocr_service.py      # Lab report extraction
│       ├── diet_planner.py     # Meal plan generation
│       └── progress_analyzer.py # Track improvements
├── .env                    # Configuration
└── requirement.txt         # Dependencies
```

### Key Files Explained

#### `config.py` - Configuration Management

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    mongodb_url: str          # MongoDB connection string
    ollama_url: str           # Ollama server address
    vision_model: str         # Model for OCR (llava:7b)
    text_model: str           # Model for text (mistral)
    ollama_timeout: int       # Request timeout

    class Config:
        env_file = ".env"     # Load from .env file

settings = Settings()
```

**Why Pydantic Settings?**

- Automatically reads from `.env` file
- Type validation at startup
- Easy to change models without code changes

---

#### `main.py` - Application Entry Point

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database.mongodb import mongodb
from app.routes import patients, reports, diet

app = FastAPI(title="Dietician Agent API")

# Allow frontend to connect
app.add_middleware(CORSMiddleware, allow_origins=["*"], ...)

# Connect to database on startup
@app.on_event("startup")
async def startup():
    await mongodb.connect()

# Register API routes
app.include_router(patients.router, prefix="/api/patients")
app.include_router(reports.router, prefix="/api/reports")
app.include_router(diet.router, prefix="/api/diet")
```

**Key Concepts:**

- **CORS Middleware**: Allows React (port 5173) to call API (port 8000)
- **Lifecycle Events**: `startup` connects to MongoDB
- **Router Pattern**: Organizes endpoints by feature

---

#### `mongodb.py` - Database Connection

```python
from motor.motor_asyncio import AsyncIOMotorClient

class MongoDB:
    client: AsyncIOMotorClient = None

    async def connect(self):
        self.client = AsyncIOMotorClient(settings.mongodb_url)
        db = self.client[settings.database_name]

        # Create indexes for fast lookups
        await db.patients.create_index("email", unique=True)
        await db.lab_reports.create_index("patient_id")

    def get_database(self):
        return self.client[settings.database_name]

mongodb = MongoDB()
```

**Why Motor?**

- Async MongoDB driver for Python
- Non-blocking database operations
- Perfect for FastAPI's async nature

---

## 5. Ollama Integration - DEEP DIVE

This is the **core innovation** of the project! Let's understand every aspect.

---

### 5.1 What is Ollama?

**Ollama** is a tool that lets you run Large Language Models (LLMs) locally on your own computer. Think of it as "Docker for AI models."

| Feature      | Cloud APIs (OpenAI)      | Ollama (Local)   |
| ------------ | ------------------------ | ---------------- |
| Cost         | $0.01-0.06 per 1K tokens | Free forever     |
| Privacy      | Data sent to cloud       | Data stays local |
| Speed        | Depends on internet      | Depends on GPU   |
| Availability | Requires internet        | Works offline    |

### 5.2 How Ollama Works

```
┌─────────────────────────────────────────────────────────────┐
│                    YOUR COMPUTER                            │
│                                                             │
│  ┌─────────────┐     HTTP Request      ┌───────────────┐   │
│  │  Your Code  │ ───────────────────▶  │ Ollama Server │   │
│  │  (Python)   │                        │  Port 11434   │   │
│  └─────────────┘     JSON Response     │               │   │
│         ▲         ◀─────────────────── │  ┌─────────┐  │   │
│         │                              │  │ Model   │  │   │
│         │                              │  │ (GPU)   │  │   │
│         │                              │  └─────────┘  │   │
│         │                              └───────────────┘   │
│         │                                                   │
│         └── Your code just makes HTTP calls!               │
└─────────────────────────────────────────────────────────────┘
```

**Key Insight:** Ollama is just an HTTP server. Your code doesn't need any special Ollama library - just make HTTP requests!

---

### 5.3 The Ollama Client Code - Line by Line

Here's the complete `ollama_client.py` with detailed explanations:

```python
# File: backend/app/services/ollama_client.py

import httpx                    # Async HTTP client (like requests, but async)
import base64                   # For encoding images to send to vision models
from typing import List         # Type hints for cleaner code
from app.config import settings # Our environment configuration

class OllamaClient:
    """
    A wrapper class for making requests to the Ollama API.
    Why a class? So we can reuse the same configuration across all calls.
    """

    def __init__(self):
        # The URL of your Ollama server (from .env file)
        # Example: "http://192.168.0.115:11434"
        self.base_url = settings.ollama_url

        # Timeout configuration - AI models can be slow!
        # This creates a timeout object with the same value for all timeout types
        self.timeout = httpx.Timeout(float(settings.ollama_timeout))
```

#### 5.3.1 The `generate()` Method - Text Generation

```python
    async def generate(self, model: str, prompt: str, num_predict: int = 8192) -> str:
        """
        Send a text prompt to a language model and get a response.

        Args:
            model: Name of the model (e.g., "mistral", "llama3.2")
            prompt: The text prompt to send
            num_predict: Maximum tokens to generate (default 8192)

        Returns:
            The generated text response as a string
        """

        # Create an async HTTP client
        # 'async with' ensures the client is properly closed after use
        async with httpx.AsyncClient(timeout=self.timeout) as client:

            # Make a POST request to Ollama's generate endpoint
            response = await client.post(
                f"{self.base_url}/api/generate",  # Full URL: http://192.168.0.115:11434/api/generate
                json={
                    "model": model,          # Which model to use
                    "prompt": prompt,        # What to ask the model
                    "stream": False,         # Wait for complete response (not streaming)
                    "options": {
                        "num_predict": num_predict,  # Max output tokens
                        "num_ctx": 8192,             # Context window (input + output)
                    }
                },
            )

            # Raise an error if the request failed
            response.raise_for_status()

            # Parse JSON response and return the "response" field
            # Ollama returns: {"response": "...", "done": true, ...}
            return response.json()["response"]
```

**Understanding the Parameters:**

| Parameter     | What it does                                                                   | Example                   |
| ------------- | ------------------------------------------------------------------------------ | ------------------------- |
| `model`       | Which AI model to use                                                          | `"mistral"`, `"llama3.2"` |
| `prompt`      | Your question/instruction                                                      | `"Create a diet plan..."` |
| `stream`      | If `true`, get response token by token. If `false`, wait for complete response | `False`                   |
| `num_predict` | Maximum tokens in the output                                                   | `8192` = ~6000 words      |
| `num_ctx`     | Total context window (prompt + response)                                       | `8192` tokens             |

---

#### 5.3.2 The `generate_with_image()` Method - Vision Analysis

```python
    async def generate_with_image(self, model: str, prompt: str, image_path: str) -> str:
        """
        Send an image to a vision model for analysis.
        Used for OCR - extracting text from lab report images.

        Args:
            model: Vision model name (e.g., "llava:7b", "bakllava")
            prompt: Instructions for what to extract from the image
            image_path: Path to the image file on disk

        Returns:
            The model's analysis/extraction as text
        """

        # Step 1: Read the image file as binary
        with open(image_path, "rb") as f:
            image_bytes = f.read()

        # Step 2: Encode to base64 string
        # Why base64? HTTP/JSON can't handle raw binary data
        # Base64 converts binary to text that can be sent in JSON
        image_b64 = base64.b64encode(image_bytes).decode()

        # Step 3: Send to Ollama with the image
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "images": [image_b64],  # ← THIS IS THE KEY! Array of base64 images
                    "options": {
                        "num_predict": 2048,
                        "num_ctx": 4096,
                    }
                },
            )
            response.raise_for_status()
            return response.json()["response"]
```

**How Vision Models Work:**

```
┌─────────────────┐     ┌─────────────────────────────────────┐
│   Lab Report    │     │         Vision Model (llava)         │
│   Image File    │ ──▶ │                                      │
│                 │     │  1. "See" the image                  │
│  glucose: 126   │     │  2. Recognize text/numbers           │
│  hdl: 45        │     │  3. Understand context               │
│                 │     │  4. Output structured data           │
└─────────────────┘     └─────────────────────────────────────┘
                                        │
                                        ▼
                        {"glucose": 126, "hdl": 45, ...}
```

---

### 5.4 How OCR Service Uses Ollama

The `ocr_service.py` orchestrates the extraction process:

```python
# File: backend/app/services/ocr_service.py

# The prompt we send to the vision model
EXTRACTION_PROMPT = """
Analyze this lab report image and extract ALL test results.

Return ONLY valid JSON in this exact format:
{
  "tests": {
    "hemoglobin": {"value": 14.5, "unit": "g/dL", "reference": "13-17"},
    "glucose_fasting": {"value": 95, "unit": "mg/dL", "reference": "70-100"}
  }
}
"""

class OCRService:
    async def process_report(self, file_path: str, preferences: dict):
        """Main entry point for processing lab reports"""

        # Step 1: If PDF, convert each page to an image
        images = self._prepare_images(file_path)

        # Step 2: Extract lab values from each image using vision model
        all_tests = {}
        for img_path in images:
            extracted = await self._extract_from_image(img_path)
            all_tests.update(extracted)

        # Step 3: Analyze the extracted values using text model
        analysis = await self._analyze_result(all_tests, preferences)

        return all_tests, analysis

    async def _extract_from_image(self, image_path: str):
        """Use vision model to 'read' the image"""

        # Call Ollama's vision model with the image
        response = await ollama.generate_with_image(
            model=settings.vision_model,  # "llava:7b"
            prompt=EXTRACTION_PROMPT,     # Tell it what to extract
            image_path=image_path         # The image to analyze
        )

        # Parse the JSON from the response
        # (with error handling for when the model doesn't output valid JSON)
        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return data.get('tests', {})
        except:
            pass
        return {}
```

---

### 5.5 How Diet Planner Uses Ollama

The `diet_planner.py` generates meal plans:

```python
# File: backend/app/services/diet_planner.py

DIET_PLAN_PROMPT = """
You are an expert dietician. Create a 7-day meal plan for these health issues:
{health_issues}

Diet: {diet_type} | Allergies: {allergies} | Cuisine: {cuisines}

Return ONLY valid JSON...
"""

class DietPlanner:
    async def generate_plan(self, health_analysis, preferences, progress=None):

        # Build the prompt with patient-specific data
        prompt = DIET_PLAN_PROMPT.format(
            health_issues=", ".join(health_analysis.issues),
            diet_type=preferences.get("type", "non-veg"),
            allergies=", ".join(preferences.get("allergies", [])),
            cuisines=", ".join(preferences.get("cuisines", ["Indian"])),
        )

        # Call the text model
        response = await ollama.generate(
            model=settings.text_model,  # "mistral"
            prompt=prompt,
            num_predict=8192  # Need lots of tokens for 7 days!
        )

        # Parse JSON from response
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
```

---

### 5.6 Ollama API Reference

#### Available Endpoints

| Endpoint          | Method | Purpose                                |
| ----------------- | ------ | -------------------------------------- |
| `/api/generate`   | POST   | Text generation (with optional images) |
| `/api/chat`       | POST   | Multi-turn conversations               |
| `/api/embeddings` | POST   | Generate vector embeddings             |
| `/api/tags`       | GET    | List available models                  |
| `/api/pull`       | POST   | Download a model                       |

#### Example API Calls

**List Models:**

```bash
curl http://192.168.0.115:11434/api/tags
```

**Simple Generation:**

```bash
curl http://192.168.0.115:11434/api/generate -d '{
  "model": "mistral",
  "prompt": "What is the capital of France?",
  "stream": false
}'
```

**Chat Conversation:**

```bash
curl http://192.168.0.115:11434/api/chat -d '{
  "model": "mistral",
  "messages": [
    {"role": "user", "content": "Hello!"},
    {"role": "assistant", "content": "Hi! How can I help?"},
    {"role": "user", "content": "What is 2+2?"}
  ]
}'
```

---

### 5.7 Common Ollama Issues & Solutions

| Issue                | Cause                 | Solution                          |
| -------------------- | --------------------- | --------------------------------- |
| "Connection refused" | Ollama not running    | Run `ollama serve` on desktop     |
| "Model not found"    | Model not downloaded  | Run `ollama pull model_name`      |
| Response cut off     | `num_predict` too low | Increase to 8192 or higher        |
| Timeout error        | Model too slow        | Increase `OLLAMA_TIMEOUT` in .env |
| Out of memory        | Model too big         | Use smaller model (7b vs 13b)     |

---

### 5.8 Key Takeaways for Ollama Integration

1. **Ollama is just HTTP** - No special libraries needed
2. **Base64 for images** - Vision models need base64-encoded images
3. **Prompt engineering matters** - Clear prompts = better outputs
4. **Handle failures** - AI doesn't always output valid JSON
5. **Token limits** - Increase `num_predict` for longer outputs
6. **Models load on-demand** - Only uses GPU when called

---

## 6. Database Design

### Collections

#### `patients`

```json
{
  "_id": "ObjectId",
  "name": "John Doe",
  "email": "john@example.com",
  "dietary_preference": {
    "type": "veg",
    "allergies": ["nuts", "dairy"],
    "cuisines": ["Indian", "Mediterranean"],
    "meal_frequency": 3
  },
  "created_at": "2024-01-17T12:00:00Z",
  "updated_at": "2024-01-17T12:00:00Z"
}
```

#### `lab_reports`

```json
{
  "_id": "ObjectId",
  "patient_id": "string",
  "report_date": "2024-01-17",
  "file_path": "../uploads/report.pdf",
  "extracted_data": {
    "hemoglobin": { "value": 14.5, "unit": "g/dL", "status": "normal" },
    "glucose": { "value": 126, "unit": "mg/dL", "status": "high" }
  },
  "health_analysis": {
    "issues": ["Elevated glucose indicates prediabetes"],
    "risk_factors": ["High cholesterol"],
    "recommendations": ["Reduce sugar intake"]
  }
}
```

#### `diet_plans`

```json
{
    "_id": "ObjectId",
    "patient_id": "string",
    "lab_report_id": "string",
    "days": [
        {
            "day": 1,
            "breakfast": {"name": "Oatmeal", "ingredients": [...], "calories": 300},
            "lunch": {...},
            "dinner": {...}
        }
    ],
    "rationale": "This plan focuses on lowering blood sugar...",
    "progress_report": {...}
}
```

---

## 7. API Endpoints

### Patients

| Method | Endpoint                         | Description               |
| ------ | -------------------------------- | ------------------------- |
| `POST` | `/api/patients/`                 | Register new patient      |
| `GET`  | `/api/patients/search?email=...` | Find patient by email     |
| `GET`  | `/api/patients/{id}`             | Get patient details       |
| `GET`  | `/api/patients/{id}/history`     | Get all reports and plans |

### Reports

| Method | Endpoint              | Description                   |
| ------ | --------------------- | ----------------------------- |
| `POST` | `/api/reports/upload` | Upload and analyze lab report |
| `GET`  | `/api/reports/{id}`   | Get report details            |

### Diet Plans

| Method | Endpoint                         | Description              |
| ------ | -------------------------------- | ------------------------ |
| `POST` | `/api/diet/generate/{report_id}` | Generate 7-day meal plan |
| `GET`  | `/api/diet/{id}`                 | Get diet plan details    |

---

## 8. Frontend Overview

### Component Structure

```
frontend/src/
├── components/
│   ├── PatientForm.jsx      # New patient registration
│   ├── LabReportUpload.jsx  # Drag & drop file upload
│   ├── HealthAnalysis.jsx   # Display extracted lab data
│   └── DietPlanView.jsx     # 7-day meal plan display
├── services/
│   └── api.js               # API client for backend
├── App.jsx                  # Main app with navigation
└── index.css                # Dark theme styling
```

### State Management

- `currentPatient` - Stored in localStorage for persistence
- `reportData` - Lab analysis results
- `dietPlan` - Generated meal plan

---

## 9. How to Explain This Project

### Elevator Pitch (30 seconds)

> "I built an AI-powered dietician that runs entirely on local hardware. It uses computer vision to read lab reports, identifies health issues like high cholesterol or diabetes risk, and generates personalized 7-day meal plans. The key innovation is using Ollama to run open-source models like Llava and Mistral locally, so there's no cloud dependency and complete data privacy."

### Technical Deep Dive (5 minutes)

**1. The Problem:**
"Traditional health apps require expensive APIs like OpenAI or cloud-based services. I wanted to build something that runs completely locally."

**2. The Solution:**
"I used Ollama, which lets you run LLMs on consumer hardware. On my RTX 3070 with 8GB VRAM, I can run vision models and text generation locally."

**3. How It Works:**

1. "User uploads a lab report PDF or image"
2. "I convert it to images and send to Llava (a vision model) for OCR"
3. "The extracted values are analyzed by Mistral for health assessment"
4. "Another Mistral call generates a 7-day meal plan tailored to the issues"
5. "Everything is stored in MongoDB for tracking progress over time"

**4. Key Challenges:**

- "Vision models sometimes hallucinate values - I added validation"
- "JSON parsing was tricky - LLMs don't always output valid JSON"
- "Response truncation - had to increase num_predict to 8192 tokens"

**5. What I Learned:**

- "How to integrate AI models into production applications"
- "The importance of prompt engineering for structured output"
- "Async programming patterns with FastAPI"
- "How to handle AI failures gracefully in UX"

---

## 📝 Key Takeaways

1. **Ollama makes local AI accessible** - No complex setup, just `ollama pull model`

2. **Prompt engineering is crucial** - Getting structured JSON output requires careful prompts

3. **Error handling is non-negotiable** - AI models can fail or produce garbage

4. **Environment variables are your friend** - Easy to swap models without code changes

5. **MongoDB is great for AI apps** - Schema-less design handles varied AI outputs

---

## 🚀 Next Steps to Improve

- [ ] Add streaming responses for real-time generation feedback
- [ ] Implement RAG with patient history for better recommendations
- [ ] Add food image recognition for meal logging
- [ ] Fine-tune a medical model for better accuracy

---

_Created for learning and portfolio purposes. Always consult healthcare professionals for medical advice._
