FROM python:3.8-alpine

WORKDIR /app

COPY /app .

COPY requirements.txt /tmp

RUN pip install -r /tmp/requirements.txt && rm -rf /tmp/requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]