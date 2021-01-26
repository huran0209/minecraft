#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import time
import subprocess
from mcrcon import MCRcon
from pathlib import Path


def getenv(key):
    value = os.getenv(key)
    if value is None:
        emsg = "E: not found {} in env!".format(key)
        raise ValueError(emsg)
    return value


def exec_sync():
    src_dir = Path("/mnt/src")
    if not src_dir.exists():
        emsg = "not found {}".format(src_dir)
        print(emsg)
        return False

    dest_dir = Path("/mnt/dest")
    if not dest_dir.exists():
        emsg = "not found {}".format(dest_dir)
        print(emsg)
        return False

    shell_cmd = [
        "rsync -a",
        "{}/".format(src_dir),
        "{}/".format(dest_dir),
        "--exclude='logs'",
        "--exclude='plugins'",
        "--exclude='spigot_server-*.jar'",
    ]
    res = subprocess.run(" ".join(shell_cmd), shell=True)
    if res.returncode == 0:
        return True
    else:
        return False


host = getenv("RWA_RCON_HOST")
port = getenv("RWA_RCON_PORT")
password = getenv("RWA_RCON_PASSWORD")
# connect
with MCRcon(host, password, int(port)) as mcr:

    msg = "The daily backup script has been launched,"
    mcr.command("say {}".format(msg))

    msg = "freezing the server for a short time."
    mcr.command("say {}".format(msg))

    # count down
    for i in range(4, 0, -1):
        time.sleep(1)
        mcr.command("say {}".format(i))

    # save
    mcr.command("save-all flush")

    # disable the server writing to the world files
    mcr.command("save-off")

    # backup data
    msg = "exporting data..."
    mcr.command("say {}".format(msg))

    result = exec_sync()
    if result:
        msg = "done!"
        mcr.command("say {}".format(msg))
    else:
        msg = "somthing went wrong, please check the docker log."
        mcr.command("say {}".format(msg))

    # enables the server writing to the world files
    mcr.command("save-on")
