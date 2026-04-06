# Workspace

## Overview

pnpm workspace monorepo using TypeScript. Each package manages its own dependencies.

## Stack

- **Monorepo tool**: pnpm workspaces
- **Node.js version**: 24
- **Package manager**: pnpm
- **TypeScript version**: 5.9
- **API framework**: Express 5
- **Database**: PostgreSQL + Drizzle ORM
- **Validation**: Zod (`zod/v4`), `drizzle-zod`
- **API codegen**: Orval (from OpenAPI spec)
- **Build**: esbuild (CJS bundle)

## Key Commands

- `pnpm run typecheck` — full typecheck across all packages
- `pnpm run build` — typecheck + build all packages
- `pnpm --filter @workspace/api-spec run codegen` — regenerate API hooks and Zod schemas from OpenAPI spec
- `pnpm --filter @workspace/db run push` — push DB schema changes (dev only)
- `pnpm --filter @workspace/api-server run dev` — run API server locally

See the `pnpm-workspace` skill for workspace structure, TypeScript setup, and package details.

## Django Project — NoteNest

A personal diary/notes app built with Django.

- **Location**: `django_project/NoteNest/`
- **Django version**: 6.0.3
- **Database**: SQLite (`db.sqlite3`)
- **Running on**: port 8000 (workflow: "NoteNest Django")
- **Start command**: `cd django_project/NoteNest && python manage.py runserver 0.0.0.0:8000`

### Django Stack
- `Django 6.0.3` — web framework
- `gunicorn` — production WSGI server
- `whitenoise` — static file serving

### Key Django Commands
- `python manage.py migrate` — run migrations
- `python manage.py makemigrations` — create new migrations
- `python manage.py collectstatic` — collect static files
- `python manage.py createsuperuser` — create admin user

### Apps
- `diary` — main app with Entry model (title, description, user, created_at)
