::

            __       __    __
  .--.--.--|__.-----|  |--|  |--.-----.-----.-----.
  |  |  |  |  |__ --|     |  _  |  _  |     |  -__|
  |________|__|_____|__|__|_____|_____|__|__|_____|


  ===================================
  wishbone_contrib.module.output.http
  ===================================

  Version: 3.0.2

  Submit data to a http API.
  --------------------------
  **Submit data to a http API.**

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

          - native_events(bool)(False)
             |  Submit Wishbone native events.

          - parallel_streams(int)(1)
             |  The number of outgoing parallel data streams.

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


