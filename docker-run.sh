#!/bin/bash
TMP=$(mktemp -d)
cp $(pwd)/config/smart-home-automations.yaml $TMP
echo "Temp directory is $TMP"
docker run -it --rm  \
    --name smart-home-automations \
    -v $TMP:/smart-home-automations/config \
    rzarajczyk/smart-home-automations:latest
