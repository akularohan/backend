# Anonymously — Backend

This is the FastAPI backend for **Anonymously**, powering real-time chat, image uploads, and temporary room management.

## ✨ Features
- Create and join chat rooms
- Optional passwords for private rooms
- Real-time WebSocket chat
- Image upload support
- Rooms automatically expire
- Tracks active users in rooms
- Uses MongoDB for lightweight storage

## 🚀 Run Locally
```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```
## 🔧 Environment Variables
Create a .env file:

MONGODB_URL=your-mongodb-url

DATABASE_NAME=your-databse-name
