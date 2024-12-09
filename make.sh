#!/usr/bin/env bash

set -e

python ./rlmeta/rlmeta.py \
    --support \
    --compile json.rlmeta \
    --compile txtlist.rlmeta \
    --compile rlmeta/src/parser.rlmeta \
    --compile rlmeta.rlmeta \
    --copy gtkgui.py \
    --copy gui.py \
    --copy editor.py \
    --copy languages.py \
    --copy main.py > rleditor.py

python rleditor.py --selftest
