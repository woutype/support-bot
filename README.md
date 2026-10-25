<div align="center">

# 🎫 SupportDesk Bot

<p align="center">
  <a href="https://github.com/woutype/support-bot">
    <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=600&size=20&duration=2500&pause=1000&color=2CA5E0&center=true&vCenter=true&width=550&lines=Async+Telegram+Ticketing+Bot;aiogram+3+%2B+PostgreSQL+%2B+asyncpg;Engineered+by+woutype+%E2%9A%A1" alt="Typing SVG" />
  </a>
</p>

[![Author](https://img.shields.io/badge/Author-woutype-8A2BE2?style=for-the-badge&logo=github&logoColor=white)](https://github.com/woutype)
[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![aiogram](https://img.shields.io/badge/aiogram-3.x-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)](https://docs.aiogram.dev/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15%2B-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![asyncpg](https://img.shields.io/badge/asyncpg-Connection_Pool-005C84?style=for-the-badge&logo=fastapi&logoColor=white)](https://magicstack.github.io/asyncpg/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

<p align="center">
  A high-performance, asynchronous two-way customer support bot built with <b>Python</b>, <b>aiogram 3</b>, and <b>PostgreSQL</b>.<br>
  Enables clients to file tickets directly in Telegram while support operators manage, inspect, and reply to issues in real time through an interactive inline UI.
</p>

[Key Features](#-key-features) • [Database Schema](#-database-schema) • [Quick Start](#-quick-start) • [Tech Stack](#-tech-stack)

</div>

---

## 🌟 Key Features

### 👤 Client (User) Experience
* **⚡ Frictionless Onboarding:** Automatic user registration upon `/start` with safe conflict resolution (`ON CONFLICT DO NOTHING`).
* **🎫 Interactive Ticket Submission:** Multi-step **FSM (Finite State Machine)** flow with input validation (minimum 6 characters) and instant cancellation.
* **📋 Dynamic Ticket History:** Browse tickets via auto-generated inline buttons complete with live status badges:
  * `🟡 OPEN` — Inquiry awaiting operator review.
  * `🟢 ANSWERED` — Solution provided by support team.
  * `🔴 CLOSED` — Ticket resolved or closed.
* **🔄 In-Place Navigation:** Seamlessly inspect ticket details and return to the list via Telegram's `edit_text` API without chat clutter.

### 🛡️ Operator (Admin) Dashboard
* **🔔 Real-Time Ticket Alerts:** Immediate dispatch of newly created tickets to support operators with user profile cards.
* **✍️ 1-Click Interactive Reply:** Operators click `[ ✍️ Reply ]`, enter their answer, and the bot routes the message directly into the customer's private chat.
* **❌ Instant Resolution:** Close invalid inquiries or spam with `[ ❌ Close Ticket ]` and notify the client automatically.
* **🔘 Native Menu Integration:** Custom Telegram `BotCommand` menu for quick navigation.

---

## 🗄️ Database Schema

The persistence layer uses a high-throughput **asyncpg connection pool** with foreign-key referential integrity:

### 1. `users` Table
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `SERIAL` | `PRIMARY KEY` | Internal database row ID |
| `tg_id` | `BIGINT` | `UNIQUE NOT NULL` | Unique Telegram User ID |
| `username` | `TEXT` | `NULLABLE` | Telegram username (`@username`) |
| `full_name` | `TEXT` | `NOT NULL` | User's full display name |
| `created_at` | `TIMESTAMP` | `DEFAULT CURRENT_TIMESTAMP` | Initial registration date |

### 2. `tickets` Table
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `SERIAL` | `PRIMARY KEY` | Unique ticket number (`#1, #2...`) |
| `user_tg_id` | `BIGINT` | `REFERENCES users(tg_id)` | Author's Telegram ID |
| `issue_text` | `TEXT` | `NOT NULL` | Description of the user's issue |
| `status` | `TEXT` | `DEFAULT 'OPEN'` | Status: `OPEN`, `ANSWERED`, `CLOSED` |
| `admin_tg_id` | `BIGINT` | `NULLABLE` | Telegram ID of the responding operator |
| `admin_reply` | `TEXT` | `NULLABLE` | Official support reply text |
| `created_at` | `TIMESTAMP` | `DEFAULT CURRENT_TIMESTAMP` | Timestamp of ticket submission |
| `updated_at` | `TIMESTAMP` | `DEFAULT CURRENT_TIMESTAMP` | Timestamp of latest reply or status change |

---

## 📁 Project Directory Structure

```text
support-bot/
├── .env.example              # Template for environment variables
├── .env                      # Production secrets & tokens (git-ignored)
├── .gitignore                # Exclusion list (venv, secrets, caches)
├── requirements.txt          # Pinned project dependencies
├── config.py                 # Fail-fast dataclass configuration parser
├── main.py                   # Application entrypoint & connection pool init
│
├── database/                 # Asynchronous persistence layer
│   ├── __init__.py
│   └── db.py                 # asyncpg connection pool & CRUD operations
│
├── handlers/                 # aiogram 3 event routers
│   ├── __init__.py           # Unified router aggregator (Open-Closed Principle)
│   ├── user.py               # Customer commands, tickets FSM & callbacks
│   └── admin.py              # Operator controls, reply FSM & resolution
│
├── keyboards/                # Keyboard factories
│   ├── __init__.py           # Public keyboards package exports
│   ├── user_kb.py            # Customer Reply keyboards & dynamic Inline lists
│   └── admin_kb.py           # Operator Inline actions under tickets
│
└── states/                   # Finite State Machine (FSM) state groups
    ├── __init__.py
    └── ticket_states.py      # Customer TicketState & Operator AdminState
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites
* **Python 3.11+** installed on your system.
* **PostgreSQL** running locally or on a cloud provider (Neon, Supabase, Render, Aiven).
* A **Telegram Bot Token** obtained from [@BotFather](https://t.me/BotFather).
* Your **Telegram User ID** obtained from [@userinfobot](https://t.me/userinfobot).

### 2. Clone Repository
```bash
git clone https://github.com/woutype/support-bot.git
cd support-bot
```

### 3. Setup Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy the sample file and fill in your real credentials:
```bash
cp .env.example .env
```
Edit `.env`:
```ini
# Telegram Bot Credentials
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
ADMIN_ID=5075170717

# PostgreSQL Connection Credentials
DB_HOST=localhost
DB_PORT=5432
DB_NAME=support_bot
DB_USER=postgres
DB_PASS=postgres
```

> [!TIP]
> Ensure a database named `support_bot` (or your chosen `DB_NAME`) exists in PostgreSQL before starting the bot. All tables and relations are created automatically on launch!

### 5. Run the Application
```bash
python main.py
```

You should see:
```text
INFO:root:🚀 Bot started successfully!
INFO:aiogram.dispatcher:Run polling for bot @YourBotName id=...
```

---

## 🛠️ Tech Stack & Design Highlights

* **[aiogram 3.x](https://docs.aiogram.dev/):** The cutting edge of async Telegram frameworks, featuring Router modularity, Magic Filters (`F`), and built-in Dependency Injection.
* **[asyncpg](https://github.com/MagicStack/asyncpg):** The fastest asynchronous PostgreSQL driver in the Python ecosystem with native connection pooling.
* **[Pydantic / Dataclasses](https://docs.python.org/3/library/dataclasses.html):** Strictly typed, fail-fast configuration with immediate startup validation.
* **Defensive Architecture:** Clean package boundaries via `__init__.py`, parameterized queries preventing SQL injections, and resilient state handling.

---

## 👨‍💻 Author

**woutype** — [@woutype](https://github.com/woutype)

---

## 📄 License

Distributed under the **MIT License**. See `LICENSE` for more information.

<div align="center">
  <sub>Developed with ❤️ and engineered for reliability by <a href="https://github.com/woutype"><b>woutype</b></a>.</sub>
</div>
