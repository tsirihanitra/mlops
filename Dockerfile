FROM python:3.10-slim


RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --timeout=300 -r requirements.txt

COPY src/ ./src/
COPY data/ ./data/

RUN python src/train.py

EXPOSE 5000

CMD ["python", "src/app.py"]
