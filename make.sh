#!/usr/bin/env bash

set -e

python ./rlmeta/rlmeta.py \
    --support \
    --compile json.rlmeta \
    --copy main.py > rleditor.py

python rleditor.py --selftest
