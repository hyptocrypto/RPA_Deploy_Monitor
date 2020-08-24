#!/bin/bash

docker stop $(docker ps -a -q)
sleep 4
docker system prune --all --force --volumes
