# NovaTech AI Solutions Website + Backend

Responsive company website for a tech solutions business offering AI services and a customer-support bot.

## Features

- Marketing landing page for services and AI value proposition
- Interactive support-bot demo connected to backend API
- Contact form that submits leads to backend API
- Data storage to JSON files for demo purposes

## Run locally

```bash
python3 backend/server.py
```

Visit `http://127.0.0.1:8000`.

## API endpoints

- `GET /api/health`
- `POST /api/contact`
- `POST /api/support-bot`
