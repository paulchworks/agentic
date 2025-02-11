FROM python:3.11-slim-buster
WORKDIR /app
COPY requirements.txt .

RUN pip install -r requirements.txt
RUN crewai install

COPY . .

EXPOSE 8000

CMD ["panel", "serve", "app.py", "--port", "8000", "--allow-websocket-origin", "*"]
