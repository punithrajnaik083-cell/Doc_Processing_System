# Document Processing Agent

An AI system that reads business documents (PDF, JPG, PNG), extracts their data, validates it, flags what's wrong, and exports clean records, with a dashboard to watch it all.

---

## Getting Started

### Prerequisites
- Python 3.12+
- Node.js 20+ (LTS) & npm
- Tesseract OCR 5
- Git

---

### Backend Setup

#### Windows (PowerShell)
```powershell
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Install requirements
pip install -r requirements.txt

# Create .env file from template
copy .env.example .env

# Run unit tests
pytest

# Start FastAPI development server
uvicorn app.main:app --reload --port 8000
```

#### macOS / Linux (Bash)
```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Create .env file from template
cp .env.example .env

# Run unit tests
pytest

# Start FastAPI development server
uvicorn app.main:app --reload --port 8000
```

---

### Frontend Setup

#### Windows / macOS / Linux
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Create .env.local file from template
# Windows:
copy .env.example .env.local
# macOS/Linux:
cp .env.example .env.local

# Start Next.js development server
npm run dev
```

Visit [http://localhost:3000](http://localhost:3000) to view the application.

---

### Running Tests

```bash
# Backend pytest
cd backend
pytest
```
