# Reforme — Pilates Studio Management Platform

Reforme is a fullstack mini SaaS MVP platform designed for Pilates studios and fitness instructors.  
It provides class scheduling, recurring classes, client bookings, Stripe payments, instructor profiles, and automated email workflows.

Reforme is built with:

- Django + Django REST Framework (API)
- Next.js / React (frontend)
- MySQL 8 (database)
- Redis + RQ (background jobs)
- SendGrid (email)
- Stripe (payments)
- Docker for local development


## 🚀 Features

### Admin Dashboard
- Create, update, delete classes and recurring classes
- Manage instructors, class size, and clients
- View bookings and attendance lists

### Client
- Create account  
- Browse & Book classes  
- Manage passes & subscriptions  
- Receive confirmation/cancellation emails  


---

# 📦 Local Development Setup

This project uses Docker Compose for local development.  
You only need **Docker** and **Docker Compose** installed.

## 1️⃣ Clone the repository

- git clone https://github.com/<your-username>/reforme.git
- cd reforme

## 2️⃣ Create Environment variables
cp .env.example .env
- Fill out the value as needed

## 3️⃣ Create local Docker file
- cp docker-compose.example.yml docker-compose.yml


## 4️⃣ Start and build containers
- docker compose up --build


## 5️⃣ Run migrations (first-time setup)
- docker exec -it reforme_api.web /bin/bash
- python manage.py migrate

** You may have to trigger a small change in a project file such as a view to kickstart the server (Simply comment and uncomment a line of code)


💳 Stripe Setup (Local)

To test payments:
- Enable test mode on Stripe dashboard
- Configure public/secret keys in .env
- Visit /api/stripe/webhook to verify the webhook is connected

Use test cards:
- 4242 4242 4242 4242 (success)
- See stripe payment testing documentation here: https://docs.stripe.com/testing

👤 Admin Dashboard Credentials
- username: reforme_admin@gmail.com
- password: admin123! ( Please do not change the admin password for other to have access ☺ )

