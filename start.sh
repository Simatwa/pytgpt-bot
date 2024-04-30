#!/usr/bin/bash
BOTDIR="pytgpt-bot"

function setup(){
    export PATH="$PATH:$HOME/.local/bin"
    if [ -d "$BOTDIR" ]; then
       cd "$BOTDIR"
       git checkout master
       git pull origin master
    
    else
       git clone -b master https://github.com/Simatwa/pytgpt-bot.git "$BOTDIR"
       cd "$BOTDIR"
    
    fi
    pip install -U pip
    pip install .
    pip install pymysql
}

function move_to_path(){
    # environment variables
    cp ../.env .
}

function start_server(){
    python "run.py"
}

setup
move_to_path
start_server
