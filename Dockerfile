FROM node:22-alpine AS frontend
WORKDIR /ui
COPY server/frontend/package*.json ./
RUN npm ci
COPY server/frontend/ ./
RUN npm run build
FROM python:3.12-slim
WORKDIR /app
COPY server/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY server/ ./
COPY --from=frontend /ui/build ./frontend/build
RUN python manage.py collectstatic --noinput && useradd --create-home appuser && chown -R appuser /app
RUN mkdir -p /data && chown appuser /data
USER appuser
EXPOSE 8000
CMD ["gunicorn","djangoproj.wsgi:application","--bind","0.0.0.0:8000","--workers","2","--access-logfile","-"]
