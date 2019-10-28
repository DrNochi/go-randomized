#!/usr/bin/env bash

sudo docker run -u $(id -u):$(id -g) --gpus all --rm -it -v $(pwd):/gobby gobby
