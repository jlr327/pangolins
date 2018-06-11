import aiohttp
import argparse
import asyncio
from datetime import datetime
from collections import deque
import sys

# Token Traffic Limiting Algorithm
class TokenRateLimiter:
    """
    Implements token algorithm for rate limitation of http client get
    requests.

    @params:
    replenish_rate: the rate at which tokens are replenished (tokens per second)

    max_tokens: the maximun number of tokens storable in the token bucket

    query_size: the size of the issued queries; corresponds to the number of tokens
                required to issue a query. In this case, only get queries are
                supported.

    """

    # Query size: Could be set to random to better reflect real world, especially
    # post queries
    def __init__(self, replenish_rate=1, max_tokens=1, query_size=1):
        self._max_tokens = max_tokens
        self._tokens = self._max_tokens
        self._loop = asyncio.get_event_loop()
        self._updated_at = self._loop.time()
        self._replenish_rate = replenish_rate
        self._query_size = query_size

    async def wait_for_token(self):
        while self._tokens < self._query_size:
            print('Waiting for tokens...: require: %d tokens, currently have: %.2f'
                % (self._query_size, self._tokens))
            self.add_new_tokens()
            await asyncio.sleep(1)

        self._tokens -= self._query_size

    def add_new_tokens(self):
        now = self._loop.time()
        time_since_update = now - self._updated_at
        new_tokens = time_since_update * self._replenish_rate

        if new_tokens > 0:
            self._tokens = min(self._tokens + new_tokens, self._max_tokens)
            self._updated_at = now

    async def __aenter__(self):
        await self.wait_for_token()

    async def __aexit__(self, exc_type, exc, tb):
        pass

async def main(desired_queries_per_second_rate=1, url='http://localhost:8080/{}', num_iterations=10):
    num_queries = 0

    async def io_operation(rate_limiter):
        async with rate_limiter:
            # If query rate is less than specified rate, issue get query from
            # client to service
            async with aiohttp.ClientSession(loop=loop) as client:
                try:
                    async with await client.get(url) as resp:
                            print('Sending get query')
                            nonlocal num_queries
                            num_queries += 1
                except Exception as e:
                    print('Exception: Client cannot connect to server! ', e)
                    sys.exit(1)

    try:
        loop = asyncio.get_event_loop()
        rate_limiter = TokenRateLimiter()
        start_time = loop.time() # datetime.now()
        await asyncio.wait([io_operation(rate_limiter) for i in range(num_iterations*desired_queries_per_second_rate)])
        time_delta = (loop.time() - start_time) #.total_seconds()
        print('Desired queries per second: ', desired_queries_per_second_rate, \
                'Achieved queries per second: ', num_queries / time_delta)
    except Exception as e:
        print('Exception: ', e)

if __name__ == "__main__":
    if sys.version_info[0] != 3 or sys.version_info[1] < 5:
        print("This script requires Python version 3.5")
        sys.exit(1)

    parser = argparse.ArgumentParser(description='Define queries per second, iterations to be run, and url of web service.')
    parser.add_argument('--queries_per_second_rate', metavar='QPS', type=int,
                        default=1,
                        help='an integer corresponding to the desired queries per second rate for the client')
    parser.add_argument('--iterations', metavar='I', type=int,
                        default=10,
                        help='number of iterations to have the client query the web service for')
    parser.add_argument('--url', metavar='URL',
                        default='http://localhost:8080/{}',
                        help='url of web service (include port)')

    args = parser.parse_args()

    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main(desired_queries_per_second_rate=args.queries_per_second_rate, url=args.url, num_iterations=args.iterations))
    except Exception as e:
        print('Exception! ', e)
    finally:
        pending = asyncio.Task.all_tasks()
        loop.run_until_complete(asyncio.gather(*pending))
        loop.close()
