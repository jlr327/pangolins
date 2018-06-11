import aiohttp
import argparse
import asyncio
from datetime import datetime
from collections import deque

# Leaky Bucket Rate Limiting Algorithm
class LeakyBucketRateLimiter:
    def __init__(self, queries_per_second_limit):
        self._bucket_queue = 0
        self._loop = asyncio.get_event_loop()
        self._queries_per_second_limit = queries_per_second_limit
        self._time_of_query_calls_queue = deque()

    async def __aenter__(self):
        self._bucket_queue += 1

        # Determine if need to throttle client's current rate of queries per second
        while True:
            # Check current rate of queries issued per length of time
            # Ensure that one or more queries have been issued so that do not get an out-of-bounds error
            if len(self._time_of_query_calls_queue) >= 1:
                _current_query_rate = len(self._time_of_query_calls_queue) / (self._loop.time() - self._time_of_query_calls_queue[0])
                print('Throttling...\n: current rate of ', _current_query_rate, \
                    'exceeds desired queries per second rate of ', self._queries_per_second_limit, '\n')
            else:
                _current_query_rate = 0

            if _current_query_rate <= self._queries_per_second_limit:
                print('No longer a need to throttle; current rate is less than the desired queries/second rate\n') #, current rate of ', _current_query_rate, ' is less than desired rate of ', self._queries_per_second_limit, ' queries per second.')
                break

                                    # [-1]: Get the rightmost element in deque
            tm = self._loop.time() - self._time_of_query_calls_queue[-1]
            interval = 1.0 / self._queries_per_second_limit
            await asyncio.sleep(self._bucket_queue * interval - tm) # Sleep

        self._bucket_queue -= 1

        """
        Ensure that queue doesn't grow beyond necessary lengths
        Need to store the called times for the queries within the last second at least
          s.t. we can calculate rate.
        """
        if len(self._time_of_query_calls_queue) == self._queries_per_second_limit:
            self._time_of_query_calls_queue.popleft()

        self._time_of_query_calls_queue.append(self._loop.time())

    async def __aexit__(self, exc_type, exc, tb):
        await print('exiting context')

async def main(desired_queries_per_second_rate=1, url='http://localhost:8080/{}', num_iterations=50):
    num_queries = 0
    loop = asyncio.get_event_loop()

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

    rate_limiter = LeakyBucketRateLimiter(desired_queries_per_second_rate)
    start_time = datetime.now()
    await asyncio.wait([io_operation(rate_limiter) for i in range(num_iterations*desired_queries_per_second_rate)])
    time_delta = (datetime.now() - start_time).total_seconds()
    print('Desired QPS:', desired_queries_per_second_rate, 'Achieved QPS:', num_queries / time_delta)

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
        # TODO FINISH PENDING TASKS
        loop.close()
