FROM python:3.11.5-slim-bullseye

WORKDIR /usr/src/cinerate-backend

COPY . .

RUN apt-get update && apt-get install -y curl python3-venv \
    && python3 -m pip install --upgrade pip \
    && pip install -r requirements.txt

EXPOSE 8000

ENTRYPOINT ["python3", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
