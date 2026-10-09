# Satori Spa - Massage Spa Management System

A full-featured Django web application for managing a massage/spa business. Customers can browse services, learn about the team, and book appointments online. Staff have access to an admin dashboard for managing bookings, services, employees, and tracking revenue.

## Features

- **Public Website** — Homepage, services listing, about/team page, contact page
- **Online Booking System** — Customers select a service, choose a therapist, pick a date/time, and receive email confirmations
- **Admin Dashboard** — Full CRUD for services, employees, and bookings with real-time notification polling
- **Email Notifications** — Gmail SMTP integration notifies admins of new bookings and customers of status changes
- **Revenue Tracking** — Monthly revenue aggregated from completed bookings
- **Daily Booking Stats** — Automatic tracking of daily booking volume
- **Polling-Based Live Updates** — Version files enable the admin dashboard to detect new bookings without page refresh
- **Django Admin Integration** — All models registered for the built-in admin interface
- **ngrok Support** — Scripts included for exposing the local server publicly during development

## Tech Stack

| Component  | Technology |
|---|---|
| Framework  | Django 5.2 |
| Language   | Python 3 |
| Database   | MySQL |
| Frontend   | HTML, CSS, JavaScript, Font Awesome |
| Email      | Gmail SMTP with custom SSL backend |

## Models

- **Service** — Spa services (name, description, price, duration, image)
- **Booking** — Customer appointments linked to a Service (customer info, therapist, date/time, status)
- **Customer** — Registered customer profiles (name, email, phone)
- **Employee** — Spa therapists/staff (name, title, bio, photo, status)
- **DailyBookingStat** — Aggregated booking counts per day
- **MonthlyRevenue** — Aggregated revenue per month

## Setup

### Prerequisites

- Python 3.x
- MySQL running on `localhost:3306`
- Virtual environment (`.venv` included)

### Installation

```bash
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Create the database in MySQL
# Name: massage_spa_db, User: spa_user

# Run migrations
python manage.py migrate

# Create a superuser
python manage.py createsuperuser

# Start the development server
python manage.py runserver
```

### Access Points

| URL | Purpose |
|---|---|
| `http://127.0.0.1:8000/` | Public site (login page) |
| `http://127.0.0.1:8000/admin-dashboard/` | Admin dashboard |
| `http://127.0.0.1:8000/admin/` | Django admin interface |

### Utility Commands

```bash
python manage.py rebuild_daily_stats --days 30
```

## License

Private project.
