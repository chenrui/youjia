#!/usr/bin/env python
# -*- coding:utf-8 -*-
from config import config
from app import create_app


app = create_app(config['default'])

if __name__ == '__main__':
    app.run()
