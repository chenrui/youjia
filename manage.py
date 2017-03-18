#!/usr/bin/env python
# -*- coding:utf-8 -*-
from flask.ext.script import Manager, Server
from flask.ext.migrate import MigrateCommand
from config import config
from app import commands, create_app


if __name__ == "__main__":
    server = Server(host="0.0.0.0", port=8080)
    app = create_app(config['default'])
    manager = Manager(app)
    manager.add_command("runserver", server)
    manager.add_command("drop_db", commands.DropDB())
    manager.add_command("create_db", commands.CreateDB())
    manager.add_command('db', MigrateCommand)
    manager.add_command('init_data', commands.InitData())
    manager.run(default_command='runserver')
