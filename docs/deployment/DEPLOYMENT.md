# Production Deployment Specification

**Document ID:** DOC-DEP-001  
**Project:** College Attendance Management System  
**Target Environment:** Hostinger VPS / Standard Linux (Ubuntu 22.04 / 24.04 LTS)  
**Date:** October 2026  

---

## 1. Production Architecture Overview

```
[Internet / Campus Network]
            │
            ▼ (Port 80/443)
┌──────────────────────────────────────────────────────────┐
│                   HOSTINGER LINUX VPS                    │
│                                                          │
│  ┌────────────────────────────────────────────────────┐  │
│  │                     NGINX                          │  │
│  │  - SSL / TLS Termination (Let's Encrypt Certbot)   │  │
│  │  - Static Asset Delivery (Vite PWA Build & Media)  │  │
│  │  - Reverse Proxy /api/v1/ -> Gunicorn Socket       │  │
│  └─────────────────────────┬──────────────────────────┘  │
│                            │ Unix Domain Socket          │
│                            ▼                             │
│  ┌────────────────────────────────────────────────────┐  │
│  │               GUNICORN WSGI SERVICE                │  │
│  │  - Python 3.11/3.12 Virtualenv                     │  │
│  │  - 3-4 Worker Processes (systemd managed)          │  │
│  │  - Django Core Application                         │  │
│  └─────────────────────────┬──────────────────────────┘  │
│                            │ TCP 5432                    │
│                            ▼                             │
│  ┌────────────────────────────────────────────────────┐  │
│  │               POSTGRESQL 15+ DATABASE              │  │
│  │  - UTF-8 Encoding                                  │  │
│  │  - Daily Cron pg_dump Backups                      │  │
│  └────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────┘
```

---

## 2. Environment Configuration (`.env`)

Production parameters are strictly managed via environment variables. See [`.env.example`](file:///.env.example):
- `DEBUG=False`
- `SECRET_KEY=<cryptographically-random-50-character-string>`
- `ALLOWED_HOSTS=ams.college.edu,127.0.0.1`
- `DATABASE_URL=postgres://ams_user:password@localhost:5432/ams_db`
- `EMAIL_BACKEND=apps.notifications.services.smtp.SMTPProvider`
- `EMAIL_HOST=smtp.college.edu`
- `EMAIL_PORT=587`
- `EMAIL_USE_TLS=True`
- `EMAIL_HOST_USER=ams-alerts@college.edu`
- `EMAIL_HOST_PASSWORD=<secret>`

---

## 3. Deployment Steps

1. **System Provisioning:** Install Python, PostgreSQL, Nginx, Git, Certbot.
2. **Repository Clone:** Clone repository to `/var/www/ams/`.
3. **Virtualenv Setup:** `python3 -m venv /var/www/ams/venv && source /var/www/ams/venv/bin/activate && pip install -r requirements.txt`.
4. **Database Migration:** `python manage.py migrate --noinput`.
5. **Static Assets:** `python manage.py collectstatic --noinput`.
6. **Systemd Services:** Enable and start `ams-backend.service`.
7. **Nginx Configuration:** Deploy `/etc/nginx/sites-available/ams.conf` and obtain SSL certificate via `certbot --nginx`.
8. **Cron Scheduling:** Schedule background email queue processing and daily database backups.
