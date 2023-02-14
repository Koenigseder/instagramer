#!/bin/bash

docker rm -f instagramer
docker volume rm -f instagramervol
docker run -d --rm --name instagramer -v instagramervol:/resources --env-file .env -p 8080:8080 instagramer