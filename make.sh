#!/usr/bin/env bash

set -e

python ./rlmeta/rlmeta.py \
    --support \
    --compile json.rlmeta \
    --copy gtkui.py \
    --copy editor.py \
    --copy languages.py \
    --copy main.py > rleditor.py

python rleditor.py --selftest
