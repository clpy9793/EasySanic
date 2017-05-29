#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2017-05-30 02:01:01
# @Author  : Your Name (you@example.org)
# @Link    : http://example.org
# @Version : $Id$

"""
测试
"""

import os
import time
import aiohttp
from sanic import Sanic
from sanic import Blueprint
from sanic.response import *

bp_test = Blueprint('test')


@bp_test.route("/test")
async def test(request):
    "测试用"
    # url = app.url_for('hello')
    url = 'http://localhost:8000/info'
    async with aiohttp.ClientSession() as session:
        rst = await session.get(url)
        ret = await rst.text(encoding='utf8')
        return html(ret)


@bp_test.get('/error')
async def error(req):
    raise ServerError("Something bad happened", status_code=500)


@bp_test.route('/stop')
async def stop(request):
    bp_test.stop()
    return text('stop')


@bp_test.route("/stream")
async def ustream(request):
    async def sample_streaming_fn(response):
        response.write('foo,')
        response.write('bar')

    return stream(sample_streaming_fn, content_type='text/csv')


@bp_test.get('/hello')
async def hello(req):
    return text('hello world')


@bp_test.route('/json')
async def ujson(req):
    d = {'data': 'text'}
    if req.json:
        d.update(req.json)
    return json(d)


@bp_test.route('/query')
async def query(req):
    return json(req.args)


@bp_test.route('/bytes')
async def ubytes(req):
    print(req.body)
    return text(req.body)


@bp_test.get('/user/<name:[A-z]{1,20}>')
async def user(request, name):
    return json({'name': name})


@bp_test.get('/info')
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


@bp_test.get('/file/<file_name>')
async def get_file(file_name):
    return await file(file_name)
