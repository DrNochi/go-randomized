#!/usr/bin/env bash

sudo docker run -u $(id -u):$(id -g) --gpus all --rm -it -v $(pwd):/gobby -p 5000:5000 gobby
