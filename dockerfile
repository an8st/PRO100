# 1. Базовый образ: Python 3.9 slim
FROM python:3.9-slim

# 2. Установим системные зависимости (ffmpeg и т. п.)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      ffmpeg \
      build-essential \
    && rm -rf /var/lib/apt/lists/*

# 3. Рабочая директория
WORKDIR /app

# 4. Скопировать requirements.txt и установить Python-зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Скопировать весь код приложения
COPY . .

# 6. Переменные окружения для Flask
ENV FLASK_APP=run.py \
    FLASK_ENV=production \
    FLASK_RUN_HOST=0.0.0.0

# 7. Открыть порт (по умолчанию SocketIO/Flask слушает 5000)
EXPOSE 5000

# 8. Команда запуска с eventlet для Socket.IO
CMD ["python", "run.py"]
