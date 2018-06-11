# Description:

This suite of scripts implements a web service application (webService.py) and
two types of rate-limiting clients. One of the clients uses the token bucket
network traffic shaping approach (tokenClient.py) and the other client type
implements the leaky bucket network traffic shaping approach (leakyBucketClient.py).

# To run:

## Web service application:
######  python3 webService.py [--delay True]

  --delay commandline argument allows the user to specify whether to add a delay
  to web service application's responses to client queries. Adding a delay allows
  the web service application to more accurately emulate the delays often seen
  in general networked connections.


## Token rate limiting algorithm Implementation:
######  python3 tokenClient.py [--queries_per_second_rate 1 --iterations 10 --url http://localhost:8080/{}]

  --queries_per_second_rate commandline argument allows the user to specify how
  many queries per second the client should be throttled to abide within. Queries
  per second corresponds to the rate at which queries are sent from the client to
  the web service application.

  --iterations commandline argument allows the user to specify how many iterations
  to run this client for. More iterations, the longer the client runs for.

  --url commandline argument is the url AND port number of the web application
  service and is the complete address for the client to resolve the web service
  at; example: http://localhost:8080/{}.


## Leaky bucket rate limiting algorithm implemenation:
######  python3 leakyBucketClient.py [--queries_per_second_rate 1 --iterations 10 --url http://localhost:8080/{}]

  --queries_per_second_rate commandline argument allows the user to specify how
  many queries per second the client should be throttled to abide within. Queries
  per second corresponds to the rate at which queries are sent from the client to
  the web service application.

  --iterations commandline argument allows the user to specify how many iterations
  to run this client for. More iterations, the longer the client runs for.

  --url commandline argument is the url AND port number of the web application
  service and is the complete address for the client to resolve the web service
  at; example: http://localhost:8080/{}.


## TODO: Bugs to be fixed:
(1) When there is no web service running and when the leaky bucket client script is subsequently started, the script raises exceptions, tries to close the asyncio event loop regardless of pending tasks, and tries to call sys.exit([with a non-zero exit code]). None of these approaches kill the queued tasks in the asyncio event loop. TODO: Read documentation to learn how to more effectively and cleanly close the event loop and cancel any queue tasks following an exception being raised by a thread, such as an exception that the client is not connected to the web server. I see connection-specific documentation relating to streaming connections, but haven't found the correspondent documentation for non-streaming connections yet.
