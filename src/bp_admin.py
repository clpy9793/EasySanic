#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2017-05-29 22:35:38
# @Author  : Your Name (you@example.org)
# @Link    : http://example.org
# @Version : $Id$
"""
后台管理相关
"""
import os
from sanic import Blueprint
from sanic import response
from subprocess import check_output

bp_admin = Blueprint('admin', url_prefix='/admin')


@bp_admin.get('/')
async def test(req):
    return response.text('bp_admin')

@bp_admin.route('/restart')
async def restart(req):
    # origin = os.path.abspath(__file__)
    # origin_dir = os.path.dirname(origin)
    # print(os.listdir())
    os.chdir('/workspace/')
    # print(check_output(['python restart.py'], shell=True).decode())
    os.system('python restart.py')
    return response.text("Success")



def main():
    pass


if __name__ == '__main__':
    main()
