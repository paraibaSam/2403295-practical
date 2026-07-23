FROM python:3.12-slim
WORKDIR /app
COPY web/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY web /app
RUN useradd -m appuser && chown -R appuser /app
USER appuser
CMD ["python", "app.py"]