#!/bin/bash
docker run -it --rm  \
    --name smart-home-automations \
    -v $(pwd)/config:/smart-home-automations/config \
    -v $(pwd)/logs:/smart-home-automations/logs \
    rzarajczyk/smart-home-automations:latest
