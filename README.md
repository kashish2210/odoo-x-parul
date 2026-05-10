# Traveloop

Traveloop is an interactive, modern web application designed to help users plan trips, discover local activities, and organize their travel notes effortlessly. Built with **Django**, Traveloop provides a premium, responsive experience utilizing glassmorphism design aesthetics, interactive destination slideshows, and smooth micro-animations.

**Live Demo:** [https://odoo-x-parul.onrender.com](https://odoo-x-parul.onrender.com)

---

## Screenshots

*(Add screenshots of your application here)*

### Dashboard
<!-- <img src="link-to-dashboard-screenshot.png" alt="Dashboard" width="800"> -->

### Activity Search & Interactive Slideshows
<!-- <img src="link-to-activities-screenshot.png" alt="Activities Search" width="800"> -->

### Trip Notes & Planning
<!-- <img src="link-to-notes-screenshot.png" alt="Trip Notes" width="800"> -->

---

## Features

- **Dynamic Destination Discovery:** Explore top regional selections with immersive, city-specific image galleries.
- **Interactive Slideshow Popups:** Click on destination cards to view a beautiful, swipeable fullscreen slideshow of local imagery.
- **Trip Planning & Management:** Create, track, and manage ongoing, upcoming, and completed trips.
- **Smart Filtering & Sorting:** Effortlessly search through activities and trip notes with instant grouping and sorting parameters.
- **Quick View Modals:** Instantly see activity details (cost, duration, popularity) without leaving your search flow.
- **Responsive & Premium UI:** Crafted using vanilla CSS with a focus on dark mode elegance, glassmorphism, and responsive flexbox layouts.

---

## Technology Stack

- **Backend:** Python, Django 5.2
- **Database:** PostgreSQL (Production) / SQLite (Local)
- **Frontend:** HTML5, Vanilla CSS, Vanilla JavaScript
- **Deployment:** Render
- **Static File Serving:** WhiteNoise

---

## Local Development Setup

To run this project locally, follow these steps:

### 1. Clone the repository
```bash
git clone https://github.com/kashish2210/odoo-x-parul.git
cd odoo-x-parul
```

### 2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup Environment Variables
Create a `.env` file in the root directory and add the following:
```env
SECRET_KEY=your-local-secret-key
DEBUG=True
# DATABASE_URL=postgresql://user:password@host/dbname  # Uncomment if using Postgres locally
```

### 5. Run Migrations
```bash
python manage.py migrate
```

### 6. Start the Development Server
```bash
python manage.py runserver
```
Visit `http://127.0.0.1:8000` in your browser.

---

## Deployment (Render)

This project is configured for easy deployment on Render using the provided `build.sh` script.

1. Connect your repository to Render as a **Web Service**.
2. Set the Environment to **Python 3**.
3. **Build Command:** `bash build.sh`
4. **Start Command:** `gunicorn traveloop.wsgi:application`
5. **Environment Variables:**
   - `DATABASE_URL`: Your Render PostgreSQL Internal/External URL
   - `SECRET_KEY`: A secure random string
   - `DEBUG`: `False`


