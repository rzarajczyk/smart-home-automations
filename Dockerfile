FROM python:3-slim

WORKDIR /app

ENV AUTOMATION $AUTOMATION

COPY automations/$AUTOMATION/. .

RUN find .

RUN pwd

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "./src/main.py"]
