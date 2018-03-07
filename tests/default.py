#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  default.py
#
#  Copyright 2018 Jelle Smet <development@smetj.net>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#

from wishbone_input_httpserver import HTTPServer
from wishbone.actorconfig import ActorConfig

from wishbone_output_http import HTTPOutClient
from wishbone.event import Event
from wishbone.utils.test.test_utils import getter


class SpinupServer(object):

    def __init__(self, *args, **kwargs):

        self.args = args
        self.kwargs = kwargs
        self.actor_config = ActorConfig('http', 100, 1, {}, "", disable_exception_handling=True)

    def __enter__(self):

        self.http = HTTPServer(self.actor_config, **self.kwargs)
        self.http.pool.createQueue("outbox")
        self.http.pool.queue.outbox.disableFallThrough()
        self.http.start()
        return self.http.pool

    def __exit__(self, *args):
        self.http.stop()


class SpinupClient(object):

    def __init__(self, *args, **kwargs):

        self.args = args
        self.kwargs = kwargs
        self.actor_config = ActorConfig('http', 100, 1, {}, "", disable_exception_handling=True)

    def __enter__(self):

        self.client = HTTPOutClient(self.actor_config, **self.kwargs)
        self.client.pool.queue.inbox.disableFallThrough()
        self.client.start()
        return self.client.pool

    def __exit__(self, *args):
        pass


def test_module_http_response_default():

    with SpinupServer() as server:
        with SpinupClient() as client:
            client.queue.inbox.put(
                Event(
                    "hello"
                )
            )
            server_event = getter(server.queue.outbox)
            assert server_event.get() == "hello"
