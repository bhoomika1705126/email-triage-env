FROM python:3.10-slim

WORKDIR /app

# Copy dependency files
COPY requirements.txt .
COPY pyproject.toml .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir uvicorn fastapi

# Copy application code
COPY environment.py openenv.yaml ./
COPY server.py ./
COPY tasks/ ./tasks/

# Expose port
EXPOSE 7860

# Run the server using uvicorn (recommended for FastAPI)
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "7860", "--log-level", "info"]