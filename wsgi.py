#!/usr/bin/env python
# -*- coding:utf-8 -*-
from flask.ext.script import Manager, Server
from flask.ext.migrate import MigrateCommand
from config import config
from app import commands, create_app




app = create_app(config['default'])

if __name__ == '__main__':
    app.run()