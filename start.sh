#!/usr/bin/env bash

# generic python program start script

ENTRYPOINT='main.py'

SCRIPTLOCATION=$(dirname -- "$(readlink -f -- "$BASH_SOURCE")")
cd $SCRIPTLOCATION

#echo "ensuring venv..."
python3 -m venv venv
source $SCRIPTLOCATION/venv/bin/activate

#echo "installing deps..."
pip -q install -r requirements.txt
#echo "complete."

#echo "starting..."
python3 $ENTRYPOINT "$@"