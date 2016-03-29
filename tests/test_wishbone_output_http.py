#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  bb.py
#
#  Copyright 2016 Jelle Smet <development@smetj.net>
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

from wishbone.event import Event
from wishbone.actor import ActorConfig
from wishbone_output_http import HTTPOutClient
from wishbone.utils.test import getter

from gevent.pywsgi import WSGIServer
from gevent.queue import Queue
from gevent import spawn, sleep


class WebServer():

    def __init__(self):
        self.q = Queue()
        self.wsgi = WSGIServer(('', 8088), self.application, log=None)

    def application(self, env, start_response):
        start_response('200 OK', [('Content-Type', 'text/html')])
        i = env["wsgi.input"].readlines()
        env["wsgi.input"] = i

        self.q.put(env)
        yield "<b>hello world</b>"

    def start(self):
        spawn(self.wsgi.start)

    def stop(self):
        self.wsgi.stop()


class WebServerTimeout():

    def __init__(self):
        self.q = Queue()
        self.wsgi = WSGIServer(('', 8088), self.application, log=None)

    def application(self, env, start_response):
        sleep(10)
        start_response('200 OK', [('Content-Type', 'text/html')])
        i = env["wsgi.input"].readlines()
        env["wsgi.input"] = i
        self.q.put(env)
        yield "<b>hello world</b>"

    def start(self):
        spawn(self.wsgi.start)

    def stop(self):
        self.wsgi.stop()

def test_module_http_default():

    webserver = WebServer()
    webserver.start()

    actor_config = ActorConfig('httpoutclient', 100, 1, {}, "")
    http = HTTPOutClient(actor_config, url="http://localhost:8088/")
    http.pool.queue.inbox.disableFallThrough()
    http.start()

    e = Event('{"one": 1}')

    http.pool.queue.inbox.put(e)

    one = webserver.q.get()

    assert one["REQUEST_METHOD"] == "PUT"
    assert one["wsgi.input"][0] == '{"one": 1}'
    webserver.stop()

def test_module_http_post():

    webserver = WebServer()
    webserver.start()

    actor_config = ActorConfig('httpoutclient', 100, 1, {}, "")
    http = HTTPOutClient(actor_config, url="http://localhost:8088/", method="POST")
    http.pool.queue.inbox.disableFallThrough()
    http.start()

    e = Event('{"one": 1}')

    http.pool.queue.inbox.put(e)

    one = webserver.q.get()

    assert one["REQUEST_METHOD"] == "POST"
    assert one["wsgi.input"][0] == '{"one": 1}'
    webserver.stop()


def test_module_http_content_type():

    webserver = WebServer()
    webserver.start()

    actor_config = ActorConfig('httpoutclient', 100, 1, {}, "")
    http = HTTPOutClient(actor_config, url="http://localhost:8088/", content_type="monkeyballs")
    http.pool.queue.inbox.disableFallThrough()
    http.start()

    e = Event('{"one": 1}')

    http.pool.queue.inbox.put(e)

    one = webserver.q.get()

    assert one["CONTENT_TYPE"] == "monkeyballs"
    webserver.stop()


def test_module_http_accept():

    webserver = WebServer()
    webserver.start()

    actor_config = ActorConfig('httpoutclient', 100, 1, {}, "")
    http = HTTPOutClient(actor_config, url="http://localhost:8088/", accept="monkeyballs")
    http.pool.queue.inbox.disableFallThrough()
    http.start()

    e = Event('{"one": 1}')

    http.pool.queue.inbox.put(e)

    one = webserver.q.get()

    assert one["HTTP_ACCEPT"] == "monkeyballs"
    webserver.stop()


def test_module_http_username_password():

    webserver = WebServer()
    webserver.start()

    actor_config = ActorConfig('httpoutclient', 100, 1, {}, "")
    http = HTTPOutClient(actor_config, url="http://localhost:8088/", username="username", password="password")
    http.pool.queue.inbox.disableFallThrough()
    http.start()

    e = Event('{"one": 1}')

    http.pool.queue.inbox.put(e)

    one = webserver.q.get()

    assert one["HTTP_AUTHORIZATION"] == "Basic dXNlcm5hbWU6cGFzc3dvcmQ="
    webserver.stop()


def test_module_http_timeout():

    webserver = WebServerTimeout()
    webserver.start()

    actor_config = ActorConfig('httpoutclient', 100, 1, {}, "")
    http = HTTPOutClient(actor_config, url="http://localhost:8088/", timeout=0.5)
    http.pool.queue.inbox.disableFallThrough()
    http.pool.queue.failed.disableFallThrough()
    http.start()

    e = Event('{"one": 1}')

    http.pool.queue.inbox.put(e)

    sleep(2)
    one = getter(http.pool.queue.failed)
    assert "Read timed out" in one.dump(complete=True)["@errors"]["httpoutclient"][2]
    webserver.stop()
