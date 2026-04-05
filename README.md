## Стек

- **FastAPI** — веб-фреймворк
- **SQLAlchemy** — ORM
- **PostgreSQL** — база данных
- **Pydantic** — проверка данных
- **Pytest** — тестирование
- **Docker** — контейнеризация

## Быстрый старт

### 1. Клонируйте репозиторий
```bash
git clone https://github.com/marathozin/notes-api.git
cd notes-api
```

### 2. Настройте окружение
```bash
cp .env.example .env
```

## Запуск через Docker Compose
```bash
docker compose up --build
```
- API URL: http://localhost:8000
- Interactive Docs: http://localhost:8000/docs

## Локальный заауск

### 1. Создайте и активируйте виртуальную среду:
```bash
python -m venv venv
source venv/bin/activate
```

### 2. Установите зависимости:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Запустите сервер:
```bash
uvicorn app.main:app --reload
```

## Документация API

Interactive docs: `http://localhost:8000/docs`

## Тестирование

```bash
pytest
```
