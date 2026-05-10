# Traveloop

Traveloop is an interactive, modern web application designed to help users plan trips, discover local activities, and organize their travel notes effortlessly. Built with **Django**, Traveloop provides a premium, responsive experience utilizing glassmorphism design aesthetics, interactive destination slideshows, and smooth micro-animations.

**Live Demo:** [https://odoo-x-parul.onrender.com](https://odoo-x-parul.onrender.com)

**video Demo** https://youtu.be/MvFeBggaoqo?si=gZ6j6goTl8PJPZs_

---

## Screenshots
<img width="1903" height="863" alt="image" src="https://github.com/user-attachments/assets/10ef9b3b-c5bc-46c1-9436-c175c9766ca8" />
<img width="411" height="701" alt="image" src="https://github.com/user-attachments/assets/398517ef-99f5-4817-855d-8ed15bc32f86" />
<img width="1901" height="861" alt="image" src="https://github.com/user-attachments/assets/0a0efc07-f1d1-438b-b93e-8ceeaf247e8d" />
<img width="1901" height="772" alt="image" src="https://github.com/user-attachments/assets/f62b17e0-ed41-4ee2-8b41-ba1312e82e34" />
<img width="1902" height="697" alt="image" src="https://github.com/user-attachments/assets/697623e8-74e1-4b5e-95ee-2f0c71d3fea8" />
<img width="659" height="776" alt="image" src="https://github.com/user-attachments/assets/1b66c943-139a-439e-97fa-59d1a1e3be08" />
<img width="1896" height="789" alt="image" src="https://github.com/user-attachments/assets/9e45a9b2-8db7-4ff5-af57-1cf03bff81be" />
<img width="1899" height="856" alt="image" src="https://github.com/user-attachments/assets/52fbae84-2373-41c0-b65c-d96c75286b26" />
<img width="1904" height="867" alt="image" src="https://github.com/user-attachments/assets/065dad10-a8b5-4acd-b07f-16ed9925de21" />
<img width="1910" height="751" alt="image" src="https://github.com/user-attachments/assets/2f3597b9-2df7-4fcc-a78b-31c5218ce655" />
<img width="1894" height="864" alt="image" src="https://github.com/user-attachments/assets/3a9acf69-28a6-4a2c-8761-43a78790902f" />
<img width="1115" height="632" alt="image" src="https://github.com/user-attachments/assets/3b9750a3-4fc2-420a-aec9-cdd062eb201c" />
<img width="1899" height="857" alt="image" src="https://github.com/user-attachments/assets/187d6b3f-c00c-4b51-bd5b-c6a15ea56841" />
<img width="1898" height="833" alt="image" src="https://github.com/user-attachments/assets/ba3035cb-941e-4a9f-a5ec-e4765935ab48" />
<img width="1896" height="843" alt="image" src="https://github.com/user-attachments/assets/10fd6ba0-eca4-408e-9184-3d58d94f14ea" />
<img width="878" height="869" alt="image" src="https://github.com/user-attachments/assets/5867248d-2475-46e3-8b7f-d5b7f6c21e2d" />
<img width="916" height="853" alt="image" src="https://github.com/user-attachments/assets/baa2360a-e184-4210-b4c3-8be0b58421b5" />
<img width="1919" height="866" alt="image" src="https://github.com/user-attachments/assets/c01ba595-5b10-4016-b5ea-3b12c353a690" />
<img width="1117" height="677" alt="image" src="https://github.com/user-attachments/assets/661c54ac-f60a-4cab-96a2-1f8442461eae" />
<img width="953" height="668" alt="image" src="https://github.com/user-attachments/assets/2fcad94b-e0b0-49e1-9643-9aa9c8d6aa53" />
<img width="871" height="831" alt="image" src="https://github.com/user-attachments/assets/51b723ea-c3de-45f5-b559-2cb531a70c52" />
<img width="410" height="685" alt="image" src="https://github.com/user-attachments/assets/97e6e04f-5e42-4982-be24-c1238bc34c13" />


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


