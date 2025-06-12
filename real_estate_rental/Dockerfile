# Dockerfile
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app
COPY . /app

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Создать папки для статики
RUN mkdir -p /app/staticfiles
RUN python manage.py collectstatic --noinput


# Копируем зависимости
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Открываем нужный порт
EXPOSE 8080

# Команда запуска (если у тебя Django)
CMD ["gunicorn", "real_estate_rental.wsgi:application", "--bind", "0.0.0.0:8080"]

