# Notes API

RESTful API for managing notes with tags and authorization support.

## Tech Stack

- **FastAPI** — web framework
- **SQLAlchemy** — ORM
- **PostgreSQL** — database
- **Pydantic** — data validation
- **Pytest** — testing
- **Docker** — containerization

## Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/marathozin/notes-api.git
cd notes-api
```

### 2. Environment Configuration
```bash
cp .env.example .env
```

## Running with Docker
```bash
docker compose up --build
```
- API URL: http://localhost:8000
- Interactive Docs: http://localhost:8000/docs

## Local Development

### 1. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate
```

### 2. Install dependencies:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Start the development server:
```bash
uvicorn app.main:app --reload
```

## API Documentation

Interactive docs: `http://localhost:8000/docs`

## Testing

```bash
pytest
```