# AI Social Content Generator

[![CI](https://github.com/adrianherediaportfolio/ai-social-content-generator/actions/workflows/ci.yml/badge.svg)](https://github.com/adrianherediaportfolio/ai-social-content-generator/actions)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg)](https://react.dev)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Un generador y programador de contenido para redes sociales potenciado por IA. Crea publicaciones optimizadas para **Twitter/X**, **LinkedIn** e **Instagram** a partir de un solo tema usando OpenAI. Incluye un dashboard en React para gestionar, editar y programar contenido.

## Caracteristicas

- **Generacion Multi-Plataforma** — Un tema genera publicaciones adaptadas para Twitter (280 chars), LinkedIn (profesional) e Instagram (rico en hashtags)
- **Potenciado por IA** — Usa OpenAI GPT-4o-mini para contenido optimizado por plataforma
- **Fallback con Templates** — Funciona sin clave de OpenAI usando plantillas integradas
- **Dashboard React** — Interfaz moderna para generar, ver, filtrar y gestionar publicaciones
- **Calendario de Contenido** — Vista de publicaciones programadas por mes
- **API CRUD Completa** — Crear, leer, actualizar, eliminar y programar publicaciones
- **Panel de Estadisticas** — Seguimiento de publicaciones totales, borradores, programadas y publicadas
- **Docker Compose** — Despliegue del stack completo con un solo comando

## Arquitectura

```
ai-social-content-generator/
├── backend/               # API REST en Python con FastAPI
│   ├── src/
│   │   ├── api/routes.py  # Endpoints de la API
│   │   ├── core/          # Configuracion y base de datos
│   │   ├── models/        # Esquemas Pydantic
│   │   └── services/      # Generacion de contenido con IA
│   └── tests/
├── frontend/              # React + Vite + TailwindCSS
│   └── src/
│       └── App.jsx        # Componente principal del dashboard
├── docker-compose.yml
└── .env.example
```

## Inicio Rapido

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install ".[dev]"

# Configurar (opcional — funciona sin clave de OpenAI)
cp ../.env.example ../.env
# Edita .env y anade tu OPENAI_API_KEY

uvicorn src.main:app --reload
```

Documentacion de la API: `http://localhost:8000/docs`

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Dashboard: `http://localhost:5173`

### Docker (Stack Completo)

```bash
cp .env.example .env
docker compose up -d
```

- Frontend: `http://localhost:3000`
- API del Backend: `http://localhost:8000/docs`

## Endpoints de la API

| Metodo | Endpoint | Descripcion |
|--------|----------|-------------|
| `POST` | `/api/v1/generate` | Generar contenido para multiples plataformas |
| `GET` | `/api/v1/posts` | Listar publicaciones (filtrar por plataforma/estado) |
| `GET` | `/api/v1/posts/{id}` | Obtener una publicacion especifica |
| `PATCH` | `/api/v1/posts/{id}` | Actualizar una publicacion |
| `DELETE` | `/api/v1/posts/{id}` | Eliminar una publicacion |
| `POST` | `/api/v1/posts/{id}/schedule` | Programar una publicacion |
| `GET` | `/api/v1/stats` | Estadisticas del dashboard |
| `GET` | `/api/v1/calendar` | Vista de calendario de contenido |
| `GET` | `/health` | Verificacion de salud |

### Generar Contenido

```bash
curl -X POST http://localhost:8000/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{"topic": "Tendencias de IA en 2026", "platforms": ["twitter", "linkedin", "instagram"]}'
```

## Ejecutar Tests

```bash
# Backend
cd backend
pytest tests/ -v

# Frontend
cd frontend
npm run build  # Verifica que la build se completa correctamente
```

## Stack Tecnologico

**Backend:**
- [FastAPI](https://fastapi.tiangolo.com) — Framework web asincrono para Python
- [OpenAI API](https://openai.com) — Generacion de contenido
- [SQLite](https://sqlite.org) + [aiosqlite](https://github.com/omnilib/aiosqlite) — Base de datos
- [Pydantic](https://pydantic.dev) — Validacion de datos

**Frontend:**
- [React 18](https://react.dev) — Framework de UI
- [Vite](https://vitejs.dev) — Herramienta de build
- [TailwindCSS](https://tailwindcss.com) — CSS utility-first

## Licencia

MIT — ver [LICENSE](LICENSE).
