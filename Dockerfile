FROM python:3
ENV TZ="Europe/Warsaw"
ENV APP_ROOT="/smart-home-services"

RUN mkdir -p /smart-home-services
RUN mkdir -p /smart-home-services/config
RUN mkdir -p /smart-home-services/logs

WORKDIR /smart-home-services

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "./src/main/main.py"]
#CMD ["bash"]
