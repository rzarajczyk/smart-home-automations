#!/bin/bash
TAG=$(date '+%Y%m%d')
docker build -t rzarajczyk/smart-home-services:$TAG .
docker tag rzarajczyk/smart-home-services:$TAG rzarajczyk/smart-home-services:latest
docker push rzarajczyk/smart-home-services:$TAG
docker push rzarajczyk/smart-home-services:latest
