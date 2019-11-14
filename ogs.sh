#!/usr/bin/env bash

export PYTHONPATH=$(pwd)

node node_modules/gtp2ogs/gtp2ogs.js \
        --username Randomzied \
        --apikey $OGS_API_KEY \
        --showboard \
        --noclock \
        --persist \
        --maxconnectedgames 1 \
        --boardsizes 19 \
        -- python scripts/run_gtp.py
