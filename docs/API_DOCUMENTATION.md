# REST API Documentation - Syntax Error Detection System

## 🚀 Quick Start

### Start the API Server

```bash
python start_api.py
```

The API will be available at: `http://localhost:8000`  
**Note**: Use `http://localhost:8000` in your browser (not `0.0.0.0`)

### Interactive Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 📡 API Endpoints

### 1. Health Check
**GET** `/health`

Check API status and configuration.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "supported_languages": ["Python", "Java", "C", "C++"],
  "ml_model_loaded": true
}
```

---

### 2. Check Code for Errors
**POST** `/check`

Detect syntax errors in code.

**Request:**
```json
{
  "code": "def test():\n    print('Hello')",
  "filename": "test.py"
}
```

**Response:**
```json
{
  "language": "Python",
  "predicted_error": "NoError",
  "confidence": 1.0,
  "tutor": {
    "why": "The Python code follows correct syntax rules.",
    "fix": "No changes are required."
  },
  "rule_based_issues": [],
  "has_errors": false
}
```

---

### 3. Auto-Fix Code
**POST** `/fix`

Automatically fix detected syntax errors.

**Request:**
```json
{
  "code": "def test()\n    pass",
  "error_type": "MissingColon",
  "language": "Python",
  "line_num": 0
}
```

**Response:**
```json
{
  "success": true,
  "fixed_code": "def test():\n    pass",
  "changes": ["Added colon at line 1"],
  "error": null
}
```

---

### 4. Code Quality Analysis
**POST** `/quality`

Analyze code quality metrics.

**Request:**
```json
{
  "code": "def test():\n    pass",
  "language": "python"
}
```

**Response:**
```json
{
  "line_counts": {
    "total": 2,
    "code": 2,
    "comments": 0,
    "blank": 0
  },
  "complexity": 1,
  "comment_ratio": 0.0,
  "avg_line_length": 12.5,
  "quality_score": 85.0,
  "suggestions": []
}
```

---

### 5. Check and Fix (Combined)
**POST** `/check-and-fix`

Check for errors and automatically suggest fixes in one call.

**Request:**
```json
{
  "code": "def test()\n    pass",
  "filename": "test.py"
}
```

**Response:**
```json
{
  "error_detection": {
    "language": "Python",
    "predicted_error": "MissingColon",
    "confidence": 1.0,
    "tutor": {...},
    "rule_based_issues": [...]
  },
  "auto_fix": {
    "success": true,
    "fixed_code": "def test():\n    pass",
    "changes": ["Added colon at line 1"]
  },
  "has_errors": true,
  "fix_available": true
}
```

---

## 🔧 Usage Examples

### Python
```python
import requests

# Check code
response = requests.post(
    "http://localhost:8000/check",
    json={
        "code": "print('hello world')",
        "filename": "test.py"
    }
)
print(response.json())
```

### cURL
```bash
curl -X POST "http://localhost:8000/check" \
  -H "Content-Type: application/json" \
  -d '{"code": "print(\"hello\")", "filename": "test.py"}'
```

### JavaScript/Node.js
```javascript
fetch('http://localhost:8000/check', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    code: "print('hello world')",
    filename: "test.py"
  })
})
.then(res => res.json())
.then(data => console.log(data));
```

---

## 🌐 Supported Languages

- **Python** (.py)
- **Java** (.java)
- **C** (.c)
- **C++** (.cpp)

---

## 📊 Error Types Supported

### Python-Specific:
- IndentationError
- MissingColon
- ImportError
- NameError
- MutableDefault
- WildcardImport
- LineTooLong

### Java/C/C++-Specific:
- MissingDelimiter (semicolons)
- MissingInclude (C/C++)
- UndeclaredIdentifier

### Universal:
- UnmatchedBracket
- UnclosedString
- DivisionByZero
- TypeMismatch
- DuplicateDefinition
- InvalidAssignment
- UnusedVariable
- UnreachableCode
- InfiniteLoop

---

## 🔒 CORS Configuration

By default, CORS is enabled for all origins (`*`). For production, update the CORS settings in `api.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 🚢 Deployment

### Using Uvicorn
```bash
uvicorn api:app --host 0.0.0.0 --port 8000
```

### Using Gunicorn (Production)
```bash
gunicorn api:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Using Docker
```bash
docker build -t syntax-checker-api .
docker run -p 8000:8000 syntax-checker-api
```

---

## 📈 Rate Limiting

Consider adding rate limiting for production:

```bash
pip install slowapi
```

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/check")
@limiter.limit("100/minute")
async def check_code(request: Request, ...):
    ...
```

---

## 🔐 Authentication (Optional)

Add API key authentication:

```python
from fastapi import Header, HTTPException

async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != "your-secret-key":
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return x_api_key

@app.post("/check", dependencies=[Depends(verify_api_key)])
async def check_code(...):
    ...
```

---

## 📝 License

MIT License - See LICENSE file for details
