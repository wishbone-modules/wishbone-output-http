#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  httpoutclient.py
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

from gevent import monkey; monkey.patch_all()
from wishbone.module import OutputModule
import requests
from gevent.pool import Pool


class HTTPOutClient(OutputModule):

    '''**Submit data to a http API.**

    Submit data to a http API.


    Parameters::

        - accept(str)("text/plain")*
           |  The accept value to use.

        - additional_headers(dict)({})
           |  A dictionary of additional headers.

        - allow_redirects(bool)(False)*
           |  Allow redirects.

        - content_type(str)("application/json")*
           |  The content type to use.

        - method(str)("PUT")
           |  The http method to use. PUT/POST

        - native_event(bool)(False)
           |  Submit Wishbone native events.

        - password(str)*
           |  The password to authenticate

        - pool_size(int)(1)
           |  The outgoing pool size.

        - selection(str)("data")*
           |  The part of the event to submit externally.
           |  Use an empty string to refer to the complete event.

        - url(str)("http://localhost:19283")*
           |  The url to submit the data to

        - username(str)*
           |  The username to authenticate

        - timeout(float)(10)*
           |  The maximum amount of time in seconds the request is allowed to take.

        - verify_ssl(bool)(True)
           |  Validate the SSL certificate


    Queues::

        - inbox
           |  Incoming messages

    '''

    def __init__(self, config,
                 selection="data", payload=None, native_event=False,
                 method="PUT", pool_size=1,
                 content_type="application/json", accept="text/plain",
                 additional_headers={},
                 url="http://localhost:19283", username=None, password=None,
                 allow_redirects=False, timeout=10, verify_ssl=True):

        OutputModule.__init__(self, config)
        self.pool.createQueue("inbox")
        self.registerConsumer(self.consume, "inbox")
        self.out_pool = Pool(self.kwargs.pool_size)

    def preHook(self):

        if self.kwargs.url.startswith('https'):
            monkey.patch_ssl()

    def consume(self, event):

        data = self.getDataToSubmit(event)
        data = self.encode(data)

        status_code, server_response = self.submitData(
            method=event.kwargs.method,
            content_type=event.kwargs.content_type,
            accept=event.kwargs.accept,
            additional_headers=event.kwargs.additional_headers,
            username=event.kwargs.username,
            password=event.kwargs.password,
            data=data
        )

        event.set(server_response, "tmp.%s.server_response" % (self.name))
        event.set(status_code, "tmp.%s.status_code" % (self.name))

        if not str(status_code).startswith("2"):
            raise Exception("Failed to submit data. Reason: %s" % (server_response))
        else:
            self.logging.info("Submitted data for event id '%s'to '%s' with status '%s'." % (event.get('uuid'), event.kwargs.url, status_code))

    def submitData(self, method, content_type, accept, additional_headers, username, password, data):

        headers = {'Content-type': content_type, 'Accept': accept}
        headers.update(self.kwargs.additional_headers)
        if self.kwargs.username is not None and self.kwargs.password is not None:
            auth = (username, password)
        else:
            auth = None
        try:
            if method.lower() == "put":
                response = requests.put(
                    self.kwargs.url,
                    data=str(data),
                    auth=auth,
                    headers=headers,
                    allow_redirects=self.kwargs.allow_redirects,
                    timeout=self.kwargs.timeout,
                    verify=self.kwargs.verify_ssl
                )
            elif method.lower() == "post":
                response = requests.post(
                    self.kwargs.url,
                    data=str(data),
                    auth=auth,
                    headers=headers,
                    allow_redirects=self.kwargs.allow_redirects,
                    timeout=self.kwargs.timeout,
                    verify=self.kwargs.verify_ssl
                )

            else:
                raise Exception("Invalid http method defined: '%s'. Event dropped." % method)
        except Exception as err:
            raise Exception("Failed to execute request. Reason: %s. Event dropped." % (err))
        else:
            response.close()

        try:
            server_response = response.json()
        except Exception:
            server_response = response.text

        return response.status_code, server_response
