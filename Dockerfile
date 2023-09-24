FROM python:3.11-alpine

COPY . .

CMD ["python", "main.py", "/var/rinha/source.rinha.json"]