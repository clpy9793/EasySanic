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


class EchoServerClientProtocol(asyncio.Protocol):

    def connection_made(self, transport):
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


def main():
    pass

if __name__ == '__main__':
    main()
