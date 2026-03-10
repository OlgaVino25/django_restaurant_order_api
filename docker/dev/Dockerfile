FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["gunicorn", "star_burger.wsgi:application", "--bind", "0.0.0.0:8000"]