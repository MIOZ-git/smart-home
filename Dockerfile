# Используем официальный образ Python
FROM python:3.11-slim

# Устанавливаем Node.js
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы зависимостей
COPY requirements.txt .
COPY package.json .

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Устанавливаем Node.js зависимости
RUN npm install

# Копируем исходный код
COPY . .

# Создаем директорию для статических файлов
RUN mkdir -p public

# Открываем порты
EXPOSE 3000 5000

# Создаем скрипт запуска
RUN echo '#!/bin/bash\n\
echo "Запуск Python бэкенда..."\n\
python smart_home_backend.py &\n\
echo "Запуск Node.js сервера..."\n\
node server.js\n\
wait' > start.sh && chmod +x start.sh

# Запускаем приложение
CMD ["./start.sh"] 