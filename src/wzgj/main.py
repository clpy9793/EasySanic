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
import logging
from sanic import response
from base64 import b64encode, encodebytes
from hashlib import sha1
from urllib.parse import urlencode, quote, quote_plus
from sanic import Blueprint
from .config import APP_KEY, YSDK_URL, APP_ID
from concurrent.futures import TimeoutError
try:
    import ujson as json
except ImportError:
    import json
# logging.basicConfig(filename='wzgj/error.log', level=logging.ERROR)
logger = logging.getLogger('wzgj/errors.log')
# logging.debug('debug message')
# logging.info('info message')
# logging.warn('warn message')
# logging.error('error message')
# logging.critical('critical message')
WS = {}

PAY_PARAM = {}

bp_wzgj = Blueprint('wzgj', url_prefix='/wzgj')


@bp_wzgj.get('/test')
async def test(req):
    print(req.ip)
    # logger.info(req.ip)
    return response.text('%s' % req.ip[0])


@bp_wzgj.middleware('request')
async def on_request(request):
    pass


@bp_wzgj.middleware('response')
async def print_on_response(request, response):
    # if request.path.startswith('/wzgj'):
        # logging.info(response.body)

    # if request.app.blueprint == request.app.blueprints['wzgj']:
    #     print('wzgj')

    # else:
    #     print(request.app.blueprint)
    #     print(request.app.blueprints['wzgj'])
    #     print('非wzgj')
    # print('\n\n')
    # print(dir(request.app))
    # for i in dir(request.app):
        # if i[0] == '_':
        #     continue
        # print('%s:\t' % i, getattr(request.app, i), '\n')
    # print('\n\n')
    # print(id(bp_wzgj))
    # print(id(request.app))
    # print(str(request.app.register_blueprint))
    pass


@bp_wzgj.post('/update')
async def update(req):
    # print(req.json)
    print(req.headers)
    print(req.body)
    for i in req.values():
        print(i)
    # print(req.values())
    print(req.args)
    print(req.raw_args)
    print(req.json)
    return response.text('update')


# @bp_wzgj.get('/post_address')
# async def post_address(req):
#     ip = req.raw_args.get('ip')
#     if ip:
#         d = u'''{
#             "version": 1,
#             "severVerson": "2.140.4",
#             "updateAddress": "http://app1101994120.imgcache.qzoneapp.com/app1101994120/Inland/Online/VersionV2.130/VersionAndroidAll/2.130.4/update.php",
#             "rootAddress": "http://app1101994120.imgcache.qzoneapp.com/app1101994120/Inland/Online/VersionV2.130/VersionAndroidAll/2.130.4/",
#             "defaultSeverID": 61,
#             "announcementAndroid": {"default": "", "Android_360": ""},
#             "internalAnnouncementFilePath": "http://%s/announcement.txt",
#             "internalAnnouncementVersion": 53,
#             "updateMsg": "",
#             "serverInUpdate": "",
#             "updateByteSize": 0,
#             "severs":
#             [
#                 {"id": 1, "name": "挂机一服", "address": %s, "port": 9596, "state": "full", "order": 1},
#                 {"id": 2, "name": "挂机二服", "address": %s, "port": 9596, "state": "full", "order": 1},
#                 {"id": 3, "name": "挂机三服", "address": %s, "port": 9596, "state": "full", "order": 1},
#                 {"id": 4, "name": "挂机四服", "address": %s, "port": 9596, "state": "full", "order": 1}
#             ]
#         }''' % (ip, ip, ip, ip, ip)
#         print(os.listdir('../'))
#         with open('../static/servers.php', 'w') as f:
#             f.write(d)
#         return response.text('更新服务器地址成功')

#     return response.text('更新服务器地址失败')



@bp_wzgj.get('/mpay/get_balance_m')
async def get_balance_m(req):
    '''查询余额接口'''
    print('\n\n[NAME]:\t', 'get_balance_m')
    try:
        url = YSDK_URL
        uri = "/mpay/get_balance_m"
        sig_uri = '/v3/r' + uri
        puid = req.raw_args.get('puid').lower()
        args = PAY_PARAM[puid]
        args['lastest'] = False
        ws = WS[puid]
        cookies = {}
        channel = int(args['channel'])

        cookies['session_id'] = 'openid' if channel == 1 else "hy_gameid"
        cookies['session_type'] = "kp_actoken" if channel == 1 else "wc_actoken"
        cookies['org_loc'] = '/mpay/get_balance_m'
        cookies['appid'] = APP_ID
        for k, v in cookies.items():
            cookies[k] = quote_plus(v)
        async with aiohttp.ClientSession(cookies=cookies) as session:
            # 请求参数
            args = PAY_PARAM[puid]
            params = {}
            params['openid'] = puid.upper()
            params['openkey'] = args['payToken'].upper()
            params['appid'] = APP_ID
            params['ts'] = int(time.time())
            params['sig'] = ""
            params['pf'] = args['pf']
            params['pfkey'] = args['pfkey']
            params['zoneid'] = 1
            print('\n[params]:\n', params)
            print('\n[args]:\n', args)
            print('\n[cookies]:\n', cookies)
            sig = gen_sign(params, sig_uri)
            params['sig'] = sig
            url += uri
            s = "&".join(['{0}={1}'.format(k, params[k]) for k in sorted(params.keys())])
            print('\n[REQ]:\n', url + '?' + s)
            rst = await session.get(url, params=params)
            ret = await rst.text(encoding='utf8')
            try:
                ret = json.loads(ret)
            except Exception:
                print('[ERROR]:\t', ret)
                return response.text('-1')
            print('\n\n\n[RET]:\n', ret)
            if int(ret['ret']) == 0:
                return response.text(str(ret['balance']))
    except Exception as e:
        traceback.print_exc()
        return response.text('-1')


@bp_wzgj.get('/mpay/pay_m')
async def pay_m(req):
    '''扣除游戏币接口'''
    print('\n\n[NAME]:\t', 'pay_m')
    try:
        url = YSDK_URL
        uri = "/mpay/pay_m"
        sig_uri = '/v3/r' + uri
        puid = req.raw_args.get('puid').lower()
        args = PAY_PARAM[puid]
        args['lastest'] = False
        ws = WS[puid]
        cookies = {}
        channel = int(args['channel'])
        cookies['session_id'] = "openid" if channel == 1 else "hy_gameid"
        cookies['session_type'] = "kp_actoken" if channel == 1 else "wc_actoken"
        cookies['org_loc'] = '/mpay/pay_m'
        cookies['appid'] = APP_ID
        for k, v in cookies.items():
            cookies[k] = quote_plus(v)
        async with aiohttp.ClientSession(cookies=cookies) as session:
            # 请求参数
            args = PAY_PARAM[puid]
            params = {}
            params['openid'] = puid.upper()
            params['openkey'] = args['payToken'].upper()
            params['appid'] = APP_ID
            params['ts'] = int(time.time())
            params['sig'] = ""
            params['pf'] = args['pf']
            params['pfkey'] = args['pfkey']
            params['zoneid'] = 1
            params['amt'] = req.raw_args['amt']
            # params['billno'] = uuid.uuid4().hex
            params['billno'] = random.randint(1, 99999999999999999)
            sig = gen_sign(params, sig_uri)
            params['sig'] = sig
            print('\n[params]:\n', params)
            print('\n[args]:\n', args)
            print('\n[cookies]:\n', cookies)
            url += uri
            s = "&".join(['{0}={1}'.format(k, params[k]) for k in sorted(params.keys())])
            print('\n[REQ]:\n', url + '?' + s)
            rst = await session.get(url, params=params)
            ret = await rst.text(encoding='utf8')
            try:
                ret = json.loads(ret)
            except Exception:
                print('[ERROR]:\t', ret)
                return response.text('-1')
            print('\n[RET]:\n', ret)
            if int(ret['ret']) == 0:
                return response.text('success')
            return response.text('-1')
    except Exception as e:
        traceback.print_exc()
        return response.text('-1')


@bp_wzgj.get('/mpay/cancel_pay_m')
async def cancel_pay_m(req):
    '''取消支付接口, 因订单号未确定, 此接口无用'''
    d = req.raw_args['param']
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


@bp_wzgj.get('/mpay/present_m')
async def present_m(req):
    '''直接赠送接口'''
    print('\n\n[NAME]:\t', 'present_m')
    try:
        url = YSDK_URL
        uri = "/mpay/present_m"
        sig_uri = '/v3/r' + uri
        puid = req.raw_args.get('puid').lower()
        args = PAY_PARAM[puid]
        args['lastest'] = False
        ws = WS[puid]
        cookies = {}
        channel = int(args['channel'])
        cookies['session_id'] = 'openid' if channel == 1 else "hy_gameid"
        # cookies['session_id'] = puid.upper() if channel == 1 else "hy_gameid"
        cookies['session_type'] = "kp_actoken" if channel == 1 else "wc_actoken"
        cookies['org_loc'] = '/mpay/present_m'
        for k, v in cookies.items():
            cookies[k] = quote_plus(v)
        async with aiohttp.ClientSession(cookies=cookies) as session:
            # 请求参数
            args = PAY_PARAM[puid]
            params = {}
            params['openid'] = puid.upper()
            params['openkey'] = args['payToken'].upper()
            params['appid'] = APP_ID
            params['ts'] = int(time.time())
            params['sig'] = ""
            params['pf'] = args['pf']
            params['pfkey'] = args['pfkey']
            params['zoneid'] = 1
            params['presenttimes'] = req.raw_args['presenttimes']
            params['billno'] = uuid.uuid4().hex
            sig = gen_sign(params, sig_uri)
            params['sig'] = sig
            print('\n[params]:\n', params)
            print('\n[args]:\n', args)
            print('\n[cookies]:\n', cookies)
            url += uri
            s = "&".join(['{0}={1}'.format(k, params[k]) for k in sorted(params.keys())])
            print('\n[REQ]:\n', url + '?' + s)
            rst = await session.get(url, params=params)
            ret = await rst.text(encoding='utf8')
            try:
                ret = json.loads(ret)
            except Exception:
                print('[ERROR]:\t', ret)
                return response.text('-1')
            print('\n[RET]:\n', ret)
            if int(ret['ret']) == 0:
                return response.text('success')
            return response.text('-1')
    except Exception as e:
        traceback.print_exc()
        return response.text('-1')


@bp_wzgj.websocket('/')
async def ws_wzgj(req, ws):
    global WS
    global PAY_PARAM
    print('[INFO]: new connection')
    while True:
        try:
            data = await asyncio.wait_for(ws.recv(), timeout=10)
            if not await handle(data, ws):
                print('[ERROR]:\tbreak')
                break
                # pass
            # name = await asyncio.wait_for(ws.recv(), timeout=5)
            # print(name)
            # print("\n< {}".format(name))
            # greeting = "Hello {}!".format(name)
            # await ws.send(greeting)
            # print("> {}\n".format(greeting))
        except TimeoutError:
            print('\n\n[INFO]:')
            print('\n[WS-COUNT]:\t', len([i for i in WS if isinstance(i, str)]))
            for k, v in WS.items():
                if not isinstance(k, str):
                    continue
                print('ws:\t', k, 'puid:\t', v, '\n')
            if ws.state == 1:
                if ws not in WS:
                    print('\n\n[OUT]:\t', 1)
                    await ws.send("1")
                else:
                    print('\n\n[OUT]:\t', 2)
                    await ws.send("2")

            # else:
            #     break
    puid = WS.get(ws)
    if puid:
        WS.pop(puid, 0)
        WS.pop(ws, 0)
        PAY_PARAM.pop(puid, 0)


async def handle(data, ws):
    print('\n\n[IN]:\t', data)
    try:
        data = parse_query_string(data)
        msg_id = int(data.get('msg_id'))
        print('[MSG_ID]:\t', msg_id)
        if not msg_id:
            return
        if msg_id == 1:
            return await bind_puid(data, ws)
        elif msg_id == 2:
            return update_pay_param(data, ws)
    except AssertionError as e:
        print('[ERROR]:\t', e.message)
    except Exception as e:
        traceback.print_exc()
        print('\n\n[ERROR]:\n', data)
        pass


async def bind_puid(data, ws):
    '''绑定puid和ws'''
    global WS
    puid = data['puid'].lower()
    if puid in WS:
        origin = WS[puid]
        print('\n[INFO]:\t', '重复连接\t', puid, origin.state)
        WS.pop(puid, 0)
        WS.pop(origin, 0)
        await origin.close()
    WS[puid] = ws
    WS[ws] = puid
    print('\n\n[PUID-WS]:\t{0}\t{1}', puid, ws)
    return True


def update_pay_param(data, ws):
    '''更新支付参数'''
    global PAY_PARAM
    puid = WS[ws]
    if data['puid'].lower() != puid:
        return False
    params = {}
    params['pf'] = data['pf']
    if 'pfkey' in data:
        params['pfkey'] = data['pfkey']
    else:
        params['pfkey'] = data['pf_key']
    params['payToken'] = data['payToken']
    params['accessToken'] = data['accessToken']
    params['channel'] = data['channel']
    params['update_time'] = int(time.time())
    params['lastest'] = True
    PAY_PARAM[puid] = params
    return True


def parse_query_string(s):
    ret = {}
    for i in s.split('&'):
        key, val = i.split('=')
        ret[key] = val
    return ret


def gen_sign(data, uri, appkey=APP_KEY, method='GET'):
    '''OpenAPI V3.0'''
    s = "&".join(['{0}={1}'.format(k, data[k]) for k in sorted(data.keys()) if k != 'sig'])
    s1 = quote_plus(uri)
    s2 = ""
    s2 = ["{0}={1}".format(k, data[k]) for k in sorted(data.keys()) if k != 'sig']
    s2 = "&".join(s2)
    s2 = quote_plus(s2)
    ret = "&".join([method, s1, s2])
    key = appkey + "&"
    sig = quote_plus(
        b64encode(hmac.new(key.encode(), ret.encode(), 'sha1').digest()))
    print('\nsig:\t', sig)
    return sig


def main():
    pass

if __name__ == '__main__':
    main()
