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
from base64 import b64encode, encodebytes
from hashlib import sha1
from urllib.parse import urlencode
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
    sig_uri = '/v3/r'
    data = {}
    data['openid'] = ""
    data['openkey'] = ""
    data['appid'] = ""
    data['ts'] = ""
    data['sig'] = ""
    data['pf'] = ""
    data['pfkey'] = ""
    data['zoneid'] = ""
    cookies = {}
    cookies['session_id'] = "open_id"
    cookies['session_id'] = "hy_gameid"
    cookies['session_type'] = "kp_actoken"
    cookies['session_type'] = "wc_actoken"
    cookies['org_loc'] = '/mpay/get_balance_m'
    for k, v in cookies.items():
        cookies[k] = urlencode(v)
    sig = gen_sign(data, sig_uri, "")
    data['sig'] = sig
    url += uri
    rst = await client_session.get(url)
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

def gen_sign(data, uri, appkey='', method='GET'):
    "OpenAPI V3.0"
    s1 = urlencode(uri).upper()
    s2 = ""
    s2 = ["{0}={1}".format(k, v) for k, v in data.items() if k != "sig"]
    s2 = "&".join(s2)
    s2 = urlencode(s2).upper()
    ret = "&".join([method, s1, s2])
    key = appkey + "&"
    sig = urlencode(b64encode(hmac.new(key.encode(), ret.encode(), 'sha1').digest()))
    return sig



# 192.168.1.249:8000/user/123
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
