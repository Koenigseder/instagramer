#!/bin/bash

docker image rm -f instagramer
docker build --rm -t instagramer:latest src