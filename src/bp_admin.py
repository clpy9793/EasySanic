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
from sanic.response import *

bp_admin = Blueprint('admin', url_prefix='/admin')


@bp_admin.get('/')
async def test(req):
    return text('bp_admin')


if __name__ == '__main__':
    main()
