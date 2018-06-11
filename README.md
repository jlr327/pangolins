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
