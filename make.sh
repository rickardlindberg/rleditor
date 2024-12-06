#!/usr/bin/env bash

set -e

python ./rlmeta/rlmeta.py \
    --support \
    --compile json.rlmeta \
    --compile txtlist.rlmeta \
    --copy gtkgui.py \
    --copy gui.py \
    --copy editor.py \
    --copy languages.py \
    --copy structures.py \
    --copy main.py > rleditor.py

python rleditor.py --selftest
