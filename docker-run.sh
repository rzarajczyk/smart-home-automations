#!/bin/bash
docker run -it --rm  \
    --name smart-home-services \
    -v $(pwd)/config:/smart-home-services/config \
    -v $(pwd)/logs:/smart-home-services/logs \
    rzarajczyk/smart-home-services:latest
