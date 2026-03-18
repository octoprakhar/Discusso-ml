# 1. Start with Python 3.12 Slim
FROM python:3.12-slim

# 2. Set the working directory
WORKDIR /backend

# 3. Install necessary system tools (optional but recommended for ML builds)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 4. Install CPU-only Torch FIRST (This is the "Secret Sauce")
# This tells pip to look at the specific PyTorch CPU index
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# 5. Copy and install the rest of your requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy your project files (honoring .dockerignore)
COPY . .

# 7. Start the server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
