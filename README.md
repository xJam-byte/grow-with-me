# 🌱 Grow With Me — Your Personal Growth Operating System

> **Grow With Me — Become someone you are proud of.**

Grow With Me — это персональная операционная система развития, объединяющая трекер привычек, ежедневное обучение, духовную практику (99 имён Аллаха), вечернюю рефлексию, заметки, аналитику и честного AI-коуча в единую экосистему на базе Telegram Bot и Telegram Mini App.

---

## 🛠️ Стек технологий

- **Backend:** Python 3.11, FastAPI, aiogram 3, SQLAlchemy 2.0 (async), asyncpg, Alembic, Pydantic v2
- **Frontend (Mini App):** React 19, TypeScript, Vite, Tailwind CSS v4, Zustand, Lucide React
- **База данных:** PostgreSQL 16
- **AI:** OpenAI GPT-4o-mini (интеграция с лимитами и экономией токенов)
- **Деплой:** Railway (Backend + PostgreSQL) + Vercel (Frontend Mini App)

---

## 🚀 Быстрый старт (Локальная разработка)

### 1. Клонирование и настройка окружения

Скопируйте пример файла конфигурации:
```bash
cp .env.example .env
```
Заполните в `.env`:
- `TELEGRAM_BOT_TOKEN` — токен от @BotFather
- `DATABASE_URL` — строка подключения к PostgreSQL
- `OPENAI_API_KEY` — ключ OpenAI API

### 2. Запуск базы данных (Docker)

```bash
docker compose up -d
```
Запустится контейнер PostgreSQL 16 на порту `5432`.

### 3. Запуск Backend

```bash
cd backend
# Активация виртуального окружения
.venv\Scripts\activate   # Windows
# source .venv/bin/activate # Linux/macOS

# Запуск сервера разработки
uvicorn app.main:app --reload --port 8000
```
Swagger-документация API будет доступна по адресу: [http://localhost:8000/docs](http://localhost:8000/docs)

### 4. Запуск Frontend (Mini App)

```bash
cd frontend
npm run dev
```
Интерфейс Mini App будет доступен по адресу: [http://localhost:5173](http://localhost:5173)

---

## 🧪 Тестирование

Запуск тестов backend:
```bash
cd backend
.venv\Scripts\pytest
```

Сборка frontend (проверка типов TypeScript):
```bash
cd frontend
npm run build
```

---

## 📂 Структура проекта

```
grow-with-me/
├── backend/
│   ├── app/
│   │   ├── api/             # FastAPI маршруты и зависимости
│   │   ├── auth/            # Валидация Telegram initData
│   │   ├── bot/             # aiogram 3 бот и хэндлеры
│   │   ├── models/          # SQLAlchemy async модели
│   │   ├── repositories/    # Слой доступа к БД
│   │   ├── schemas/         # Pydantic схемы
│   │   ├── config.py        # Настройки приложения
│   │   ├── database.py      # Подключение к PostgreSQL
│   │   └── main.py          # Точка входа FastAPI
│   ├── migrations/          # Alembic миграции
│   ├── tests/               # Pytest тесты
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/             # HTTP клиент с авторизацией
│   │   ├── components/      # UI компоненты и Layout
│   │   ├── hooks/           # useTelegram, haptic feedback
│   │   ├── pages/           # Экраны (Home, Habits, Growth, Journal, AI, Settings)
│   │   ├── stores/          # Zustand хранилища
│   │   ├── styles/          # Tailwind стили и переменные
│   │   └── types/           # TypeScript типы
│   ├── package.json
│   └── vite.config.ts
├── docker-compose.yml       # Локальный PostgreSQL
├── idea.md                  # Исходный концепт и требования
└── README.md
```
