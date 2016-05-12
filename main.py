#!/usr/bin/env python3

import argparse
import re
import socketserver
from prometheus_client import start_http_server
from prometheus_client import Histogram

_INF = float("inf")
default_time_buckets = [.01, .025, .05, .075, .1, .25, .5, .75,
                        1.0, 2.5, 5.0, 7.5, 10.0, _INF]
default_size_buckets = [100, 250, 500, 750, 1e3, 5e3, 1e4, 1e5, 1e6, _INF]
histo_tt = None
histo_tr = None
histo_size = None

HAPROXY_LINE_REGEX = re.compile(
    # 127.0.0.1:39759
    # [09/Dec/2013:12:59:46.633]
    # loadbalancer default/instance8
    r'.*\s+'
    # 0/51536/1/48082/99627
    r'(?P<tq>-?\d+)/(?P<tw>-?\d+)/(?P<tc>-?\d+)/'
    r'(?P<tr>-?\d+)/(?P<tt>\+?\d+)\s+'
    # 200 83285
    r'(?P<status_code>-?\d+)\s+(?P<bytes_read>\+?\d+)\s+'
    # - - ----
    r'.*\s+'  # ignored by now, should capture cookies and termination state
    # 87/87/87/1/0
    r'(?P<act>\d+)/(?P<fe>\d+)/(?P<be>\d+)/'
    r'(?P<srv>\d+)/(?P<retries>\+?\d+)\s+'
    # 0/67
    r'(?P<queue_server>\d+)/(?P<queue_backend>\d+)\s+'
    # {77.24.148.74}
    r'.*'
    # "GET /path/to/whatever HTTP/1.1"
    r'"(?P<method>\w+)\s+'
    r'(?P<path>/[^\s]*)'
    r'\s+(?P<protocol>\w+/\d\.\d)"'
    r'\Z'  # end of line
)

class SyslogUDPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data = bytes.decode(self.request[0].strip())
        matches = HAPROXY_LINE_REGEX.match(str(data))
        if matches is None:
            return
        try:
            path = matches.group("path")
            tt = float(matches.group("tt"))
            tr = float(matches.group("tr"))
            bytes_read = float(matches.group("bytes_read"))
            # values in the log are in milliseconds
            # we use floating point seconds in the histogram
            try:
                histo_tt.labels(path).observe(tt/1000)
                histo_tr.labels(path).observe(tr/1000)
                histo_size.labels(path).observe(bytes_read)
            except ValueError:
                pass
        except IndexError:
            pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--metrics_port', type=int, default=8080, nargs='?',
                   help='HTTP metrics server port')
    parser.add_argument('--syslog_port', type=int, default=8514, nargs='?',
                   help='syslog server port')
    parser.add_argument('buckets', type=float, default=default_time_buckets,
                   nargs='*', help='Histogram time buckets')
    args = parser.parse_args()
    
    print("Create histograms with time buckets:", args.buckets)
    print("Create histograms with size buckets:", default_size_buckets)
    histo_tt = Histogram('response_time_total_seconds',
                        'HTTP reponse time in seconds',
                        ['path'], buckets=tuple(args.buckets))
    histo_tr = Histogram('response_time_server_seconds',
                        'Backend server reponse time in seconds',
                        ['path'], buckets=tuple(args.buckets))
    histo_size = Histogram('response_content_size_bytes',
                           'HTTP response content size in bytes',
                           ['path'], buckets=tuple(default_size_buckets))

    try:
        print("Starting metrics server on port", args.metrics_port)
        start_http_server(args.metrics_port)

        print("Starting syslog server on port", args.syslog_port)
        server = socketserver.UDPServer(("0.0.0.0", args.syslog_port),
                                        SyslogUDPHandler)
        server.serve_forever(poll_interval=0.5)
    except KeyboardInterrupt:
        print ("Crtl+C Pressed. Shutting down.")
