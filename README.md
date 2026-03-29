# 📄 PDF Compressor - Django Web App

A Django web application to compress PDF files to any custom target size.

## Features
- Upload PDF files (up to 50 MB)
- Set custom target size in KB
- Quick size presets (200KB, 300KB, 400KB, 500KB, 1MB, 2MB)
- Automatic quality adjustment to reach target size
- Download compressed PDF
- Compression history with stats
- Drag & drop file upload
- Dark modern UI
- Mobile responsive

---

## 🚀 Setup Instructions (PyCharm)

### Step 1: Open the project in PyCharm
1. Open PyCharm
2. Click **File → Open** and select the `pdf_compressor` folder
3. PyCharm will detect it as a Django project

### Step 2: Create Virtual Environment (Recommended)
In PyCharm Terminal (bottom panel):

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Create Database & Run Migrations

```bash
python manage.py makemigrations compressor
python manage.py migrate
```

### Step 5: Create Media Directories

```bash
# Windows
mkdir media\uploads media\compressed

# Mac/Linux
mkdir -p media/uploads media/compressed
```

### Step 6: Run the Server

```bash
python manage.py runserver
```

### Step 7: Open in Browser

Go to: **http://127.0.0.1:8000**

---

## 📁 Project Structure

```
pdf_compressor/
│
├── manage.py                  # Django management script
├── requirements.txt           # Python dependencies
├── db.sqlite3                 # SQLite database (auto-created)
│
├── pdf_compressor/            # Project settings
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── compressor/                # Main app
│   ├── __init__.py
│   ├── admin.py               # Admin panel config
│   ├── apps.py
│   ├── forms.py               # Upload form
│   ├── models.py              # PDFFile model
│   ├── urls.py                # App URLs
│   ├── utils.py               # ✨ Compression logic
│   ├── views.py               # Views (upload, result, download)
│   │
│   └── templates/compressor/
│       ├── base.html          # Base template with styling
│       ├── home.html          # Upload page
│       ├── result.html        # Compression result page
│       └── history.html       # History page
│
└── media/                     # Uploaded & compressed files
    ├── uploads/
    └── compressed/
```

---

## 🎯 How It Works

1. **Upload** a PDF file and enter your target size in KB
2. The app first tries **optimization only** (garbage collection, deflation)
3. If still too large, it **reduces image quality** step by step (80% → 10%)
4. At each step, it checks if the file is ≤ target size
5. Stops as soon as target is reached, keeping the **best possible quality**
6. Shows stats: original size, compressed size, and % reduction
7. **Download** the compressed file

---

## ⚙️ Configuration

In `pdf_compressor/settings.py`:

- `FILE_UPLOAD_MAX_MEMORY_SIZE` — Max upload size (default: 50 MB)
- `TIME_ZONE` — Set to `'Asia/Kolkata'` (change if needed)

---

## 🛠️ Optional: Create Admin User

```bash
python manage.py createsuperuser
```

Then visit: **http://127.0.0.1:8000/admin/** to manage uploaded files.

---

## 📋 Requirements

- Python 3.8+
- Django 4.2+
- PyMuPDF (fitz)
- Pillow
