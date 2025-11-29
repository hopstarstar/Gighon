FROM python:3.10-slim

WORKDIR /app
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

# expose port (Render sets PORT env var)
ENV PORT=10000
CMD exec gunicorn --bind 0.0.0.0:$PORT main:app
