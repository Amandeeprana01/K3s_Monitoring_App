FROM python:3.11-slim

WORKDIR /app

COPY . /app

RUN pip install prometheus_client psutil

EXPOSE 8000

CMD ["python", "app.py"]
