FROM python:3
ENV TZ="Europe/Warsaw"

RUN mkdir -p /smart-home-automations
RUN mkdir -p /smart-home-automations/config
RUN mkdir -p /smart-home-automations/logs

WORKDIR /smart-home-automations

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "./src/main/main.py"]
