# HAProxy Histogram Exporter for Prometheus

This package exports haproxy statistics as histrgrams for [prometheus](https://prometheus.io).

It is complementary to [haproxy_exporter](https://github.com/prometheus/haproxy_exporter).
It does extract the haproxy log sent to the embedded syslog daemon,
analyzes them and makes the histograms available through HTTP.

See the [our wiki](https://github.com/baloise/haproxy_histogram_exporter/wiki) for more info.


## Performance
About 5000 requests / second depending on your setup. Beyond this rate syslog packets are dropped.

## Run locally
To run the [prometheus client libraries for python](https://github.com/prometheus/client_python) are required:

```bash
pip install prometheus_client
```

... or without pip

```bash
git clone https://github.com/prometheus/client_python.git && ln -s client_python/prometheus_client/ .
```

and then run with

```bash
./main.py
```

## Docker
To build the haproxy histogram exporter as a Docker container, run:

```bash
docker build -t baloise/haproxy-histogram-exporter:latest .
```

To run the haproxy histogram exporter as a Docker container, run:

```bash
docker run -p 8080:80 -p 8514:514/udp baloise/haproxy-histogram-exporter
```
    
## Test
To test the docker image you may adjust and then run:

```bash
./test.py
```
    
... and then lookup [the generated metrics](http://127.0.0.1:8080/metrics) to see the histograms buckets
