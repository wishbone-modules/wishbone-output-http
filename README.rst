::

              __       __    __
    .--.--.--|__.-----|  |--|  |--.-----.-----.-----.
    |  |  |  |  |__ --|     |  _  |  _  |     |  -__|
    |________|__|_____|__|__|_____|_____|__|__|_____|
                                       version 2.1.2

    Build composable event pipeline servers with minimal effort.


    ====================
    wishbone.output.http
    ====================

    Version: 1.0.1

    Posts data to the requested URL
    -------------------------------


        Posts data to a remote URL


        Parameters:

            - selection(str)("@data")
               |  The part of the event to submit externally.
               |  Use an empty string to refer to the complete event.

            - method(str)("PUT")*
               |  The http method to use. PUT/POST

            - content_type(str)("application/json")*
               |  The content type to use.

            - accept(str)("text/plain")*
               |  The accept value to use.

            - url(str)("http://localhost")
               |  The url to submit the data to

            - username(str)*
               |  The username to authenticate

            - password(str)*
               |  The password to authenticate

            - allow_redirects(bool)(False)
               |  Allow redirects.

            - timeout(float)(10)*
               |  The maximum amount of time in seconds the request is allowed to take.


        Queues:

            - inbox
               |  Incoming messages

            - outbox
               |  Outgoing messges
