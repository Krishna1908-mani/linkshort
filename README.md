<<<<<<< HEAD
<<<<<<< HEAD
# LinkShort FastAPI Full Stack - Fixed Structure

This project is a URL shortener built with FastAPI, React/Vite, and MongoDB.

## Fixed problems

- Recreated the correct folder structure.
- Moved backend files into `backend/app`.
- Moved API routers into `backend/app/routers`.
- Moved frontend files into `frontend/src`.
- Added missing `__init__.py` files.
- Added `frontend/vite.config.js`.
- Removed broken flattened dependency files from the submitted zip.
- Added `.env.example` files.

## Default admin

Email: `admin@linkshort.com`
Password: `admin123`

## Backend run

```powershell
cd backend
py -3.11 -m venv venv
venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
copy .env.example .env
python scripts\seed_admin.py
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 5000
```

Open: `http://localhost:5000/api/docs`

## Frontend run

Open a second PowerShell terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open: `http://localhost:5173`

## MongoDB

MongoDB must be running before running `seed_admin.py` or the backend. The default connection is:

```env
MONGO_URI=mongodb://127.0.0.1:27017/linkshortener_fastapi
```

Use MongoDB Compass or local MongoDB service.
=======
# linkshort
>>>>>>> ff60e909379948b9b5b4325a0337d0c14376f068
=======
# linkshort
>>>>>>> a2e42c9bb27e9421f9cd382b4363c54fa92bed2a
