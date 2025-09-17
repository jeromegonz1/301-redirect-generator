FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./src /app/src

CMD ["streamlit", "run", "src/main.py", "--server.port=8000", "--server.address=0.0.0.0"]