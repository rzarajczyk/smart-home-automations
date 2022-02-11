#!/bin/bash
TAG=$(date '+%Y%m%d')
docker build -t rzarajczyk/smart-home-automations:$TAG .
docker tag rzarajczyk/smart-home-automations:$TAG rzarajczyk/smart-home-automations:latest
docker push rzarajczyk/smart-home-automations:$TAG
docker push rzarajczyk/smart-home-automations:latest
