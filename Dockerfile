FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install PyTorch CPU version first to avoid CUDA dependencies
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Copy requirements and install other packages
COPY requirements.txt .
RUN pip install --no-cache-dir --timeout=1000 -r requirements.txt

COPY . .

EXPOSE 9000

CMD ["uvicorn", "api.dicionarioAPI:app", "--host", "0.0.0.0", "--port", "9000"]