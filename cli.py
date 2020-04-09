#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : cli.py
# @Author: zaoshu
# @Date  : 2020-02-20
# @Desc  : 

from subprocess import Popen

from colorama import Fore, Style
from flask_script import Manager

import config
from app import app
from model.db import clean_db_session
from model.user import User

manager = Manager(app)


def after_run_begin():
    """speed up model register"""
    User.select().get(1)
    clean_db_session()


@manager.option(
    '-d', '--debug', action='store_true',
    default=config.DEBUG,
    help="Start the web server in debug mode")
@manager.option(
    '-n', '--no-reload', action='store_false', dest='no_reload',
    default=config.FLASK_USE_RELOAD,
    help="Don't use the reloader in debug mode")
@manager.option(
    '-a', '--address', default=config.ADDRESS,
    help="Specify the address to which to bind the web server")
@manager.option(
    '-p', '--port', default=config.PORT,
    help="Specify the port on which to run the web server")
@manager.option(
    '-w', '--workers',
    default=config.WORKERS,
    help="Number of gunicorn web server workers to fire up")
@manager.option(
    '-s', '--socket', default=None,
    help="Path to a UNIX socket as an alternative to address:port, e.g. "
         "/var/run/zed.sock. "
         "Will override the address and port values.")
def runserver(debug, no_reload, address, port, workers, socket):
    """Starts a Faraday web server."""
    debug = debug or config.DEBUG
    if debug:
        print(Fore.BLUE + '-=' * 20)
        print(
            Fore.YELLOW + "Starting Zed server in " +
            Fore.RED + "DEBUG" +
            Fore.YELLOW + " mode ENV: " +
            Fore.RED + config.ENV
        )
        print(Fore.BLUE + '-=' * 20)
        print(Style.RESET_ALL)
        app.run(
            host='0.0.0.0',
            port=int(port),
            threaded=True,
            debug=True,
            use_reloader=no_reload)
    else:
        addr_str = " unix:{socket} " if socket else " {address}:{port} "
        cmd = (
                "gunicorn "
                "-w {workers} "
                "-b " + addr_str +
                "--limit-request-line 0 "
                "--limit-request-field_size 0 "
                "--pid pid.log "
                "-k flask_sockets.worker "
                "--timeout 120 "
                "app:app").format(**locals())
        print(Fore.GREEN + "Starting server with command: ")
        print(Fore.YELLOW + cmd)
        print(Style.RESET_ALL)
        Popen(cmd, shell=True).wait()


if __name__ == "__main__":
    after_run_begin()
    manager.run()
