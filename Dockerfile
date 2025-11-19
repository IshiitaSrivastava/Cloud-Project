FROM python:3.11-slim
WORKDIR /app
COPY backend/ ./backend/
COPY frontend/ ./frontend/
WORKDIR /app/backend
RUN pip install --upgrade pip
RUN pip install flask flask-jwt-extended flask-cors SQLAlchemy passlib python-dotenv alembic
ENV FLASK_APP=app.py
EXPOSE 5000
CMD ["python", "app.py"]
