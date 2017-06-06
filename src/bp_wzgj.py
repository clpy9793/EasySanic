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
import uuid
import time
import hmac
import random
import asyncio
import aiohttp
import aiofiles
import traceback
from sanic import response
from base64 import b64encode, encodebytes
from hashlib import sha1
from urllib.parse import urlencode, quote, quote_plus
from sanic import Blueprint
from config import APP_KEY
try:
    import ujson as json
except ImportError:
    import json


bp_wzgj = Blueprint('wzgj', url_prefix='/wzgj')


@bp_wzgj.get('/test')
async def test(req):
    return response.text('bp_wzgj')


@bp_wzgj.get('/get_balance_m')
async def get_balance_m(req):
    "查询余额接口"
    # https://ysdk.qq.com/mpay/get_balance_m
    # https://ysdktest.qq.com/mpay/get_balance_m
    try:
        print('\n\n\n参数', req.args, '\n\n\n', req.raw_args)
        args = req.raw_args
        url = "https://ysdk.qq.com"
        uri = "/mpay/get_balance_m"
        sig_uri = '/v3/r' + uri
        params = {}
        channel = args['channel']
        params['openid'] = args['puid'].upper()
        params['openkey'] = args['token'].upper()
        params['appid'] = '1106173342'
        params['ts'] = int(time.time())
        params['sig'] = ""
        params['pf'] = args['pf']
        # params['pfkey'] = 'xaxasxqwxw'
        params['pfkey'] = args['pfkey']
        # params['pfkey'] = params['pfkey'][:-1] + params['pfkey'][0]
        # params['zoneid'] = '1_{0}'.format(args['puid'])
        params['zoneid'] = 1
        cookies = {}
        cookies['session_id'] = "open_id" if channel == 1 else "hy_gameid"
        cookies['session_type'] = "kp_actoken" if channel == 1 else "wc_actoken"
        cookies['org_loc'] = '/mpay/get_balance_m'
        for k, v in cookies.items():
            cookies[k] = quote(v)
        sig = gen_sign(params, sig_uri)
        params['sig'] = sig
        url += uri
        async with aiohttp.ClientSession(cookies=cookies) as session:
            print('\nparams:\n')
            for k in sorted(params.keys()):
                print(k, '\t', params[k])
            s = "&".join(['{0}={1}'.format(k, params[k]) for k in sorted(params.keys())])
            print('最终发送的请求串\n', url + '?' + s, '\n')
            rst = await session.get(url, params=params)
            ret = await rst.text(encoding='utf8')
            ret = json.loads(ret)
            print('\n\n\n查询结果\n', ret)
    except Exception as e:
        traceback.print_exc()
    finally:
        return response.json({'ret': "0", "msg": "success"})


@bp_wzgj.get('/mpay/pay_m')
async def pay_m(req):
    "扣除游戏币接口"
    # https://ysdk.qq.com/mpay/pay_m
    # https://ysdktest.qq.com/mpay/pay_m
    args = req.args['param']
    args = req.raw_args
    url = 'https://ysdktest.qq.com'
    uri = "/mpay/pay_m"
    sig_uri = '/v3/r'
    channel = 1
    params = {}
    params['openid'] = args['openid']
    params['openkey'] = args['openkey']
    params['appid'] = args['appid']
    params['ts'] = int(time.time())
    params['sig'] = ""
    params['pf'] = args['pf']
    params['pfkey'] = args['pfkey']
    params['zoneid'] = args['zoneid']
    params['amt'] = args['amt']
    params['billno'] = uuid.uuid4().hex
    cookies = {}
    cookies['session_id'] = "open_id" if channel == 1 else "hy_gameid"
    cookies['session_type'] = "kp_actoken" if channel == 1 else "wc_actoken"
    cookies['org_loc'] = '/mpay/get_balance_m'
    for k, v in cookies.items():
        cookies[k] = quote(v)
    sig = gen_sign(params, sig_uri, "")
    params['sig'] = sig
    url += uri
    async with aiohttp.ClientSession(cookie=cookies) as session:
        rst = await session.get(url, params=params)
        ret = await rst.json()
        status = int(ret['ret'])
        if status != 0 and status != 1004:
            print('扣除游戏币失败\n', ret)
        return response.json(ret)


@bp_wzgj.get('/cancel_pay_m')
async def cancel_pay_m(req):
    "取消支付接口, 因订单号未确定, 此接口无用"
    # https://ysdk.qq.com/mpay/cancel_pay_m
    # https://ysdktest.qq.com/mpay/cancel_pay_m
    d = req.args['param']
    args = req.raw_args
    url = 'https://ysdktest.qq.com'
    uri = "/mpay/cancel_pay_m "
    sig_uri = '/v3/r'
    channel = 1
    params = {}
    params['openid'] = args['openid']
    params['openkey'] = args['openkey']
    params['appid'] = args['appid']
    params['ts'] = int(time.time())
    params['sig'] = ""
    params['pf'] = args['pf']
    params['pfkey'] = args['pfkey']
    params['zoneid'] = args['zoneid']
    params['amt'] = args['amt']
    params['billno'] = args['billno']
    cookies = {}
    cookies['session_id'] = "open_id" if channel == 1 else "hy_gameid"
    cookies['session_type'] = "kp_actoken" if channel == 1 else "wc_actoken"
    cookies['org_loc'] = '/mpay/get_balance_m'
    for k, v in cookies.items():
        cookies[k] = quote(v)

    sig = gen_sign(params, sig_uri, "")
    params['sig'] = sig
    url += uri

    async with aiohttp.ClientSession(cookie=cookies) as session:
        rst = await session.get(url, params=params)
        ret = await rst.json()
        status = int(ret['ret'])
        if status != 0:
            print('取消支付失败\n', ret)
        return response.json(ret)


@bp_wzgj.get('/present_m')
async def present_m(req):
    "直接赠送接口"
    # https://ysdk.qq.com/mpay/present_m
    # https://ysdktest.qq.com/mpay/present_m
    args = req.raw_args
    url = 'https://ysdktest.qq.com'
    uri = "/mpay/present_m"
    sig_uri = '/v3/r'
    channel = 1
    params = {}
    params['openid'] = args['openid']
    params['openkey'] = args['openkey']
    params['appid'] = args['appid']
    params['ts'] = int(time.time())
    params['sig'] = ""
    params['pf'] = args['pf']
    params['pfkey'] = args['pfkey']
    params['zoneid'] = args['zoneid']
    params['presenttimes'] = args['presenttimes']
    params['billno'] = uuid.uuid4().hex
    cookies = {}
    cookies['session_id'] = "open_id" if channel == 1 else "hy_gameid"
    cookies['session_type'] = "kp_actoken" if channel == 1 else "wc_actoken"
    cookies['org_loc'] = '/mpay/get_balance_m'
    for k, v in cookies.items():
        cookies[k] = quote(v)
    sig = gen_sign(params, sig_uri, "")
    params['sig'] = sig
    url += uri
    async with aiohttp.ClientSession(cookies=cookies) as session:
        rst = await session.get(url, params=params)
        ret = await rst.json()
        status = int(ret['ret'])
        if status != 0:
            print('赠送游戏币失败\n', ret)
        return response.json(ret)


def tgen_sign(data, uri, appkey=APP_KEY, method='GET'):
    '''OpenAPI V3.0'''
    print('gen_sign:\n', data, '\n', uri, '\n', appkey, '\n')
    s1 = quote(uri).upper()
    s2 = ""
    s2 = ["{0}={1}".format(k, v) for k, v in data.items() if k != "sig"]
    s2 = "&".join(s2)
    s2 = quote(s2).upper()
    ret = "&".join([method, s1, s2])
    key = appkey + "&"
    sig = quote(
        b64encode(hmac.new(key.encode(), ret.encode(), 'sha1').digest()))
    print('\n结果:\n', sig.strip().lower())
    return sig.strip().lower()


def gen_sign(data, uri, appkey=APP_KEY, method='GET'):
    '''OpenAPI V3.0'''
    # data = '''appid=15499&format=json&openid=00000000000000000000000014BDF6E4&openkey=AB43BF3DC5C3C79D358CC5318E41CF59&pf=myapp_m_qq-00000000-android-00000000-ysdk&pfkey=CA641BC173479B8C0B35BC84873B3DB9&ts=1340880299&userip=112.90.139.30&zoneid=1'''
    # data = {i.split('=')[0]: i.split('=')[1] for i in data.split('&')}
    print('\n\ndata\n', data)
    s = "&".join(['{0}={1}'.format(k, data[k]) for k in sorted(data.keys()) if k != 'sig'])
    print('\n请求参数\n', s)
    s1 = quote_plus(uri)
    s2 = ""
    s2 = ["{0}={1}".format(k, data[k]) for k in sorted(data.keys()) if k != 'sig']
    s2 = "&".join(s2)
    s2 = quote_plus(s2)
    ret = "&".join([method, s1, s2])
    print('\nret\n', ret)
    key = appkey + "&"
    sig = quote_plus(
        b64encode(hmac.new(key.encode(), ret.encode(), 'sha1').digest()))
    print('\n结果:\n', sig)

    print('\n所有参数\n', data, '\n', uri, '\n', appkey)
    return sig


def main():
    pass

if __name__ == '__main__':
    main()
