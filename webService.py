import sys
import argparse
import asyncio
from datetime import datetime
from aiohttp import web
import random

class Timer:
    """
    This is the class that will interrupt every one second to provide an update
    as to how many request the web service has received in the last second

    numSeconds: number of seconds to wait between calling the callback function
                provided as a parameter to the constructor for instantiated Timer
                objects

    callback:   callback function that the objects of type Timer class will call
                at the time interval specified by numSeconds
    """

    def __init__(self, num_seconds, callback):
        self._num_seconds = num_seconds
        self._callback = callback
        asyncio.ensure_future(self.run())

    async def run(self):
        while (True):
            await asyncio.sleep(self._num_seconds)
            await self._callback()

class Service:
    """
    Service class handles the creation of the web service application, which is
    made asyncronous using the event loop provided by the asyncio package.

    Web service handles multiple client connections and cleans itself up when
    killed by a KeyboardInterrupt or when an exception is encountered.

    params:
    port:   port number to host the web service on
            default: 8080

    url:    url to host the web service on
            default: 0.0.0.0 (localhost)
    """
    def __init__(self, delay=False, port=8080, url='0.0.0.0'):
        self._sem = asyncio.Semaphore(1000)
        self._port = port
        self._url = url
        self._counter = 0

    def run(self):
        try:
            # set timer to count received requests for one second until callback
            timer = Timer(1, self.counter_callback)
            app = web.Application()
            app.router.add_route('GET', '/{name}', self.response)
            # web.run_app(app)

            self._loop = asyncio.get_event_loop()
            handler = app.make_handler()
            f = self._loop.create_server(handler, self._url, self._port)
            srv = self._loop.run_until_complete(f)
            print('Web service on', srv.sockets[0].getsockname())

        except Exception as e:
            print('Error in setup ', e)

        try:
            self._loop.run_forever()
        except KeyboardInterrupt:
            print('KeyboardInterrupt')
            pass

        finally:
            self._loop.run_until_complete(handler.finish_connections(1.0))
            srv.close()
            self._loop.run_until_complete(srv.wait_closed())
            self._loop.run_until_complete(app.finish())
            self._loop.close()


    async def response(self, request, delay=False):
        if delay:
            delay = random.randint(0, 3)
            await asyncio.sleep(delay)
        else:
            delay = 0
        headers = {"content_type": "text/html", "delay": str(delay)}

        # JR: TODO Make this file read async
        with open("test.html", "rb") as html_body:
            response = web.Response(body=html_body.read(), headers=headers)
            self._sem.acquire()
            self._counter += 1
            self._sem.release()
        return response

    async def counter_callback(self):
        self._sem.acquire()
        print('Requests per second received: ', self._counter)
        self._counter = 0 # reset for use in the following second
        self._sem.release()

if __name__ == "__main__":
    if sys.version_info[0] != 3 or sys.version_info[1] < 5:
        print("This script requires Python version 3.5")
        sys.exit(1)

    parser = argparse.ArgumentParser(description='Define whether to include a \
                delay in responses to clients;\
                enabling this option better emulates the real networked world.')
    parser.add_argument('--delay', metavar='D', type=bool,
                        default=False,
                        help='a bool corresponding to whether to delay query responses.')
    args = parser.parse_args()

    service = Service(delay=args.delay)
    service.run()
