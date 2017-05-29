#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2017-05-29 22:35:38
# @Author  : Your Name (you@example.org)
# @Link    : http://example.org
# @Version : $Id$
"""
YSDK 支付相关接口
"""
import os
import time
import hmac
import random
import asyncio
import aiohttp
import aiofiles
from base64 import b64encode, encodebytes
from hashlib import sha1
from urllib.parse import urlencode
from sanic import Blueprint
from sanic.response import *

bp_wzgj = Blueprint('wzgj', url_prefix='/wzgj')


@bp_wzgj.get('/test')
async def test(req):
    return text('bp_wzgj')


@bp_wzgj.get('/get_balance_m')
async def get_balance_m(req):
    "查询余额接口"
    # https:// ysdk.qq.com/mpay/get_balance_m
    # https://ysdktest.qq.com/mpay/get_balance_m
    d = req.args['param']
    url = "https://ysdktest.qq.com"
    uri = "/mpay/get_balance_m"
    sig_uri = '/v3/r'
    params = {}
    params['openid'] = ""
    params['openkey'] = ""
    params['appid'] = ""
    params['ts'] = ""
    params['sig'] = ""
    params['pf'] = ""
    params['pfkey'] = ""
    params['zoneid'] = ""
    cookies = {}
    cookies['session_id'] = "open_id"
    cookies['session_id'] = "hy_gameid"
    cookies['session_type'] = "kp_actoken"
    cookies['session_type'] = "wc_actoken"
    cookies['org_loc'] = '/mpay/get_balance_m'
    for k, v in cookies.items():
        cookies[k] = urlencode(v)
    sig = gen_sign(params, sig_uri, "")
    params['sig'] = sig
    url += uri
    async with aiohttp.ClientSession(cookie=cookies) as session:
        rst = await session.get(url, params=params)
        ret = await rst.json()
        if int(ret['ret']) != 0:
            print('查询余额失败\n', ret)
        return json(ret)


@bp_wzgj.get('/mpay/pay_m')
async def pay_m(req):
    "扣除游戏币接口"
    # https://ysdk.qq.com/mpay/pay_m
    # https://ysdktest.qq.com/mpay/pay_m
    d = req.args['param']
    url = 'https://ysdktest.qq.com'
    uri = "/mpay/pay_m"
    sig_uri = '/v3/r'
    params = {}
    params['openid'] = ""
    params['openkey'] = ""
    params['appid'] = ""
    params['ts'] = ""
    params['sig'] = ""
    params['pf'] = ""
    params['pfkey'] = ""
    params['zoneid'] = ""
    params['amt'] = ""
    params['billno'] = ""
    cookies = {}
    cookies['session_id'] = "open_id"
    cookies['session_id'] = "hy_gameid"
    cookies['session_type'] = "kp_actoken"
    cookies['session_type'] = "wc_actoken"
    cookies['org_loc'] = '/mpay/get_balance_m'
    for k, v in cookies.items():
        cookies[k] = urlencode(v)
    sig = gen_sign(params, sig_uri, "")
    params['sig'] = sig
    url += uri
    async with aiohttp.ClientSession(cookie=cookies) as session:
        rst = await session.get(url, params=params)
        ret = await rst.json()
        status = int(ret['ret'])
        if status != 0 and status != 1004:
            print('扣除游戏币失败\n', ret)
        return json(ret)


@bp_wzgj.get('/cancel_pay_m')
async def cancel_pay_m(req):
    "取消支付接口"
    # https://ysdk.qq.com/mpay/cancel_pay_m
    # https://ysdktest.qq.com/mpay/cancel_pay_m
    d = req.args['param']
    url = 'https://ysdktest.qq.com'
    uri = "/mpay/cancel_pay_m "
    sig_uri = '/v3/r'
    params = {}
    params['openid'] = ""
    params['openkey'] = ""
    params['appid'] = ""
    params['ts'] = ""
    params['sig'] = ""
    params['pf'] = ""
    params['pfkey'] = ""
    params['zoneid'] = ""
    params['amt'] = ""
    params['billno'] = ""
    cookies = {}
    cookies['session_id'] = "open_id"
    cookies['session_id'] = "hy_gameid"
    cookies['session_type'] = "kp_actoken"
    cookies['session_type'] = "wc_actoken"
    cookies['org_loc'] = '/mpay/get_balance_m'
    for k, v in cookies.items():
        cookies[k] = urlencode(v)
    sig = gen_sign(params, sig_uri, "")
    params['sig'] = sig
    url += uri
    async with aiohttp.ClientSession(cookie=cookies) as session:
        rst = await session.get(url, params=params)
        ret = await rst.json()
        status = int(ret['ret'])
        if status != 0:
            print('取消支付失败\n', ret)
        return json(ret)


@bp_wzgj.get('/present_m')
async def present_m(req):
    "直接赠送接口"
    # https://ysdk.qq.com/mpay/present_m
    # https://ysdktest.qq.com/mpay/present_m
    d = req.args['param']
    url = 'https://ysdktest.qq.com'
    uri = "/mpay/present_m"
    sig_uri = '/v3/r'
    params = {}
    params['openid'] = ""
    params['openkey'] = ""
    params['appid'] = ""
    params['ts'] = ""
    params['sig'] = ""
    params['pf'] = ""
    params['pfkey'] = ""
    params['zoneid'] = ""
    params['presenttimes'] = ""
    params['billno'] = ""
    cookies = {}
    cookies['session_id'] = "open_id"
    cookies['session_id'] = "hy_gameid"
    cookies['session_type'] = "kp_actoken"
    cookies['session_type'] = "wc_actoken"
    cookies['org_loc'] = '/mpay/get_balance_m'
    for k, v in cookies.items():
        cookies[k] = urlencode(v)
    sig = gen_sign(params, sig_uri, "")
    params['sig'] = sig
    url += uri
    async with aiohttp.ClientSession(cookie=cookies) as session:
        rst = await session.get(url, params=params)
        ret = await rst.json()
        status = int(ret['ret'])
        if status != 0:
            print('赠送游戏币失败\n', ret)
        return json(ret)


def gen_sign(data, uri, appkey='', method='GET'):
    "OpenAPI V3.0"
    s1 = urlencode(uri).upper()
    s2 = ""
    s2 = ["{0}={1}".format(k, v) for k, v in data.items() if k != "sig"]
    s2 = "&".join(s2)
    s2 = urlencode(s2).upper()
    ret = "&".join([method, s1, s2])
    key = appkey + "&"
    sig = urlencode(
        b64encode(hmac.new(key.encode(), ret.encode(), 'sha1').digest()))
    return sig


if __name__ == '__main__':
    main()
