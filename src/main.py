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
import uvloop
import asyncio
import aiohttp
import aiofiles

from sanic import Sanic
from sanic import Blueprint
from sanic.response import *
from sanic.exceptions import *
from sanic.config import LOGGING
from sanic_session import InMemorySessionInterface
from config import config
from wzgj import bp_wzgj
from bp_admin import bp_admin
from bp_test import bp_test

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
# LOGGING['loggers']['network']['handlers'] = ['access.log']

app = Sanic()
app.static('/', '../static')

app.blueprint(bp_wzgj)
app.blueprint(bp_admin)
app.blueprint(bp_test)


if config:
    app.config.update(config)

ALL_REQ_COST = {}
session_interface = InMemorySessionInterface()

TCP_CHANNEL = {}
FLAG = None
async def daily_task():
    global FLAG
    # loop = asyncio.get_event_loop()
    # task = asyncio.start_server(EchoServerClientProtocol, '0.0.0.0', 8989, loop=loop)
    # loop.create_task(task)
    FLAG = True

class EchoServerClientProtocol(asyncio.Protocol):

    def connection_made(self, transport):
        print('999999999999999999999999999999999')
        peername = transport.get_extra_info('peername')
        print('Connection from {}'.format(peername))
        self.transport = transport

    def data_received(self, data):
        message = data.decode()
        print('Data received: {!r}'.format(message))
        print('Send: {!r}'.format(message))
        print('Close the client socket')
        # self.transport.write(data)
        # self.transport.close()

@app.listener('before_server_start')
async def before_server_start(app, loop):
    '''服务启动之前调用, 用以检查 pid'''

    pid = ""
    async with aiofiles.open('pid.txt', 'r') as f:
        pid = await f.read()
    if pid:
        os.system('kill -9 {0}'.format(pid))
    # app.add_task(daily_task())
    # loop.create_task(daily_task())
    # while True:
    #     if not FLAG:
    #         await asyncio.sleep(1)
    #     else:
    #         print("continue")
    #         break    


@app.listener('after_server_start')
async def after_server_start(app, loop):
    "服务启动后调用"
    # app.add_task(daily_task())
    # global client_session
    # client_session = aiohttp.ClientSession()
    pid = os.getpid()
    async with aiofiles.open('pid.txt', 'w') as f:
        await f.write(str(pid))
    # app.add_task(daily_task())



@app.middleware('request')
async def print_on_request(request):
    now = time.time()
    ALL_REQ_COST[id(request)] = now
    await session_interface.open(request)


@app.middleware('response')
async def print_on_response(request, response):
    now = time.time()
    cost = now - ALL_REQ_COST.pop(id(request))
    print('req/s: ', cost)
    await session_interface.save(request, response)


@app.exception(NotFound)
def not_found(request, exception):
    return text('<p>404 not found</p>')


@app.exception(ServerError)
def server_error(request, exception):
    return text('<p>500 Server Error</p>')


def main():
    loop = asyncio.get_event_loop()
    server = app.create_server(host='0.0.0.0', port=8000, debug=True)
    other_server = loop.create_server(EchoServerClientProtocol, '0.0.0.0', '8989')
    loop.run_until_complete(asyncio.gather(*[server, other_server]))
    # loop.run_forever()


if __name__ == "__main__":
    # asyncio.start_server(EchoServerClientProtocol, '0.0.0.0', 8989)

    # app.run(host="0.0.0.0", port=8000, debug=True, 
    #         before_start=lambda app, loop: asyncio.get_event_loop().run_until_complete(start_server))
    app.run(host="0.0.0.0", port=8000, debug=True)    
    # main()
