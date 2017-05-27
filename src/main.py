#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2017-05-26 09:05:01
# @Author  : Your Name (you@example.org)
# @Link    : http://example.org
# @Version : $Id$

import os
import time
import random
import asyncio
import aiohttp
from sanic import Sanic
from sanic import Blueprint
from sanic.response import json
from sanic.response import text
from sanic.response import html
from sanic.response import file
from sanic.response import stream
from sanic.response import redirect
from sanic.exceptions import NotFound
from sanic.exceptions import ServerError
from config import config

app = Sanic()
app.static('/files', '../static')

client_session = None

if config:
    app.config.update(config)

ALL_REQ_COST = {}


async def daily_task():
    print('task start.')
    while True:
        await asyncio.sleep(1)


@app.listener('after_server_start')
async def after_server_start(app, loop):
    # app.add_task(daily_task())
    global client_session
    client_session = aiohttp.ClientSession()
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


@app.route("/")
async def test(request):
    url = app.url_for('hello')
    return redirect(url)


@app.get('/error')
async def error(req):
    raise ServerError("Something bad happened", status_code=500)


@app.route('/stop')
async def stop(request):
    app.stop()
    return text('stop')


@app.route("/stream")
async def ustream(request):
    async def sample_streaming_fn(response):
        response.write('foo,')
        response.write('bar')

    return stream(sample_streaming_fn, content_type='text/csv')


@app.get('/hello')
async def hello(req):
    return text('hello world')


@app.route('/json')
async def ujson(req):
    d = {'data': 'text'}
    if req.json:
        d.update(req.json)
    return json(d)


@app.route('/query')
async def query(req):
    return json(req.args)


@app.route('/bytes')
async def ubytes(req):
    print(req.body)
    return text(req.body)


@app.get('/user/<name:[A-z]{1,20}>')
async def user(request, name):
    return json({'name': name})


@app.get('/info')
async def info(req):
    d = {}
    d['ip'] = req.ip
    d['url'] = req.url
    d['scheme'] = req.scheme
    d['host'] = req.host
    d['path'] = req.path
    d['query_string'] = req.query_string
    d['cookies'] = req.cookies
    if req.json:
        d.update(req.json)
    res = "".join(["<p>{0}\t{1}</p>".format(k, v) for k, v in d.items()])
    # return text(res)
    return html(res, headers={'time': int(time.time())})


@app.get('/file/<file_name>')
async def get_file(file_name):
    return await file(file_name)


@app.get('/wzgj/get_balance_m')
async def get_balance_m(req):
    "查询余额接口"
    # https:// ysdk.qq.com/mpay/get_balance_m
    # https://ysdktest.qq.com/mpay/get_balance_m
    url = "https://ysdktest.qq.com"
    uri = "/mpay/get_balance_m"
    rst = await client_session.get('http://127.0.0.1:8000/info')
    r = await rst.text(encoding='utf8')
    print(r)
    return json({})

@app.get('/wzgj/mpay/pay_m')
async def pay_m(req):
    "扣除游戏币接口"
    return json({})    

@app.get('/wzgj/cancel_pay_m')
async def cancel_pay_m(req):
    "取消支付接口"
    return json({})

@app.get('/wzgj/present_m')
async def present_m(req):
    "直接赠送接口"
    return json({})




# 192.168.1.249:8000/user/123
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
