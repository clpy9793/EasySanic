#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2017-05-26 09:05:01
# @Author  : Your Name (you@example.org)
# @Link    : http://example.org
# @Version : $Id$

import os
import time
import hmac
import random
import asyncio
import aiohttp
import aiofiles
from sanic import Sanic
from sanic import Blueprint
from sanic.response import *
from sanic.exceptions import *
from sanic.config import LOGGING
from config import config
from bp_wzgj import bp_wzgj
from bp_admin import bp_admin
from bp_test import bp_test


LOGGING['loggers']['network']['handlers'] = ['access.log']

app = Sanic()
app.static('/files', '../static')
app.blueprint(bp_wzgj)
app.blueprint(bp_admin)
app.blueprint(bp_test)


if config:
    app.config.update(config)

ALL_REQ_COST = {}


async def daily_task():
    print('task start.')
    while True:
        await asyncio.sleep(1)


@app.listener('before_server_start')
async def before_server_start(app, loop):
    "服务启动之前调用, 用以检查 pid"
    # app.add_task(daily_task())
    # global client_session
    # client_session = aiohttp.ClientSession()
    pid = ""
    async with aiofiles.open('pid.txt', 'r') as f:
        pid = await f.read()
    if pid:
        # print(pid, 'kill')
        os.system('kill -9 {0}'.format(pid))
        # os.system('sudo kill -9 {0}'.format(pid))


    


@app.listener('after_server_start')
async def after_server_start(app, loop):
    "服务启动后调用"
    # app.add_task(daily_task())
    # global client_session
    # client_session = aiohttp.ClientSession()
    pid = os.getpid()
    async with aiofiles.open('pid.txt', 'w') as f:
        await f.write(str(pid))

    loop.create_task(daily_task())


@app.middleware('request')
async def print_on_request(request):
    now = time.time()
    ALL_REQ_COST[id(request)] = now


@app.middleware('response')
async def print_on_response(request, response):
    now = time.time()
    cost = now - ALL_REQ_COST.pop(id(request))
    print('req/s: ', cost)


@app.exception(NotFound)
def not_found(request, exception):
    return text('<p>404 not found</p>')


@app.exception(ServerError)
def server_error(request, exception):
    return text('<p>500 Server Error</p>')


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
