FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc gettext \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip setuptools && pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["sh", "-c", "\
  python manage.py migrate --noinput && \
  python manage.py collectstatic --noinput && \
  python manage.py compilemessages || true && \
  python manage.py createsuperuser_if_not_exists && \
  gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 120"]
