# Campus Market Place For College

*Empowering your campus with a secure, scalable, and modern marketplace API*

---

## 🏫 About

**Campus Market Place For College** is a feature-rich, API-centric backend for facilitating student-driven e-commerce within college communities. Built with FastAPI and async SQLAlchemy, this project is designed for extensibility, robustness, and integration with both web and mobile clients.

---

## 💡 Key Highlights

- **Modern Python stack:** FastAPI (async), SQLAlchemy, and fully typed Pydantic schemas
- **Production-grade authentication:** OAuth2, JWT access/refresh, secure cookies, role-based access, and token refresh
- **Robust item system:** Sell, buy, bid, search, track, and manage listings seamlessly
- **Bidding engine:** Place, update, and withdraw bids on marketplace items, all with strict user-level permissions
- **Fully containerized:** Out-of-the-box Docker, Docker Compose, and Alembic migrations—deploy on any cloud or on-premises
- **Structured for growth:** Versioned API, modular codebase (endpoints, services, models), ready for custom features or new portals

---

## ⚙️ Technical Architecture

```
├── app/
│   ├── api/           # API routes (v1, endpoints: auth, item, bid, etc.)
│   ├── core/          # App config, exception management
│   ├── db/            # Async DB access, session dep.
│   ├── models/        # SQLAlchemy models (User, Item, Bid, Enums...)
│   ├── schemas/       # Pydantic models for requests/responses
│   ├── services/      # Business logic layers
│   └── main.py        # FastAPI entrypoint
├── alembic/           # DB migration scripts
├── Dockerfile         # For containerized deployments
├── docker-compose.yml # Local and multi-service orchestration
├── pyproject.toml     # Build, dependency, and tool config
└── README.md
```

**Entry Point:**  
`app/main.py`  
Initializes the FastAPI app, includes CORS, static file serving, error handlers, and API router mounting.

---

## 🚦 API Overview

> Build your own frontend—web, mobile, or even CLI—on top of this robust backend!

### Authentication (`/api/v1/auth`)
- `POST /auth/register` — Create student accounts
- `POST /auth/login` — Issue access & refresh tokens via secure cookies
- `POST /auth/refresh` — Refresh access tokens using an httpOnly cookie
- `POST /auth/logout` — Invalidate tokens & clear cookies
- `GET /auth/me` — Retrieve current authenticated user

### Item Management (`/api/v1/item`)
- `GET /item/feed` — Browse items/feed, paginated
- `GET /item/search?query` — Search by keyword/categories
- `POST /item/create` — List a new item for sale (authenticated)
- `GET /item/selled_items` — See items you've posted
- `GET /item/bided_items` — See items you've bid on
- `GET /item/{item_id}` — View item detail
- `PATCH /item/{item_id}` — Edit your own listing
- `DELETE /item/{item_id}` — Remove your own listing

### Bid Management (`/api/v1/bid`)
- `POST /bid/{item_id}` — Place a bid on an item
- `PATCH /bid/{bid_id}` — Update your bid
- `DELETE /bid/{bid_id}` — Delete your bid

#### ... and endpoints for Item Images, Notifications, Ratings, and Transactions (see source for details)

**Swagger/OpenAPI available at:**  
`/docs` (when running locally)

---

## 🚀 Quickstart: Local Development

### 1. Clone & Configure

```bash
git clone https://github.com/viswajith275/Campus-Market-Place-For-College.git
cd Campus-Market-Place-For-College
```

Customize environment variables as needed in `.env` or `pyproject.toml` (DB URLs, secrets, etc).

### 2. Install (Dev Mode)

Requirements: Python 3.10+, Docker  
Install with poetry or pip as preferred.

```bash
docker-compose up --build      # recommended for isolation & reproducibility
# or directly:
cd app && uvicorn main:app --reload
```

### 3. Run Migrations

```bash
alembic upgrade head
```

### 4. Explore API

Visit `http://127.0.0.1:8000/docs` for full interactive documentation and try endpoints right in your browser.

---

## 🧩 Integration & Customization

- **Frontend-Ready:** Frontend devs can use any stack (React/Vue/Flutter...)—all endpoints are REST, strongly typed, and documented
- **Extendable:** Add new endpoints, schemas, or business rules in `app/api/v1/endpoints` and `app/services`
- **Multi-tenant:** Adapt for multiple colleges or permission models via the User/Item model structure
- **Asynchronous:** Out-of-the-box scalable, async database operations

---

## 🛡️ Security Best Practices

- All sensitive operations require JWT/cookie authentication
- CORS configuration is strict by default—review and adapt to your deployment target
- Secrets/tokens must be managed via Docker secrets, env files, or cloud vaults in production
- OAuth2 password grant flow and refresh token rotation are implemented out-of-box

---

## 👨‍💻 For Developers

- Modular, readable codebase following FastAPI community patterns
- Fully typed with Pydantic and Python 3.10+
- Easily add new features (e.g., payment integration, campus social feed)
- Contributions are welcome—please open a PR!

---

## 📄 License & Attribution

This project is released without a specified license—contact [@viswajith275](https://github.com/viswajith275) for commercial or institutional adoption.

---

## ☎️ Support & Community

- Open issues for bug reports or feature requests
- Collaborators and contributors invited!
- [Project Repository](https://github.com/viswajith275/Campus-Market-Place-For-College)

---

*Transform your campus experience with a secure, extensible, and developer-friendly marketplace engine.*
