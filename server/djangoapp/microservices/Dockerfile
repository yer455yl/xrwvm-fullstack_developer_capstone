FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m nltk.downloader -d /usr/local/nltk_data vader_lexicon
COPY app.py .
RUN useradd --create-home appuser
USER appuser
EXPOSE 5050
CMD ["gunicorn","app:app","--bind","0.0.0.0:5050"]
