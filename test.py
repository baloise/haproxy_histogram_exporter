#!/usr/bin/env python3

import socket
 
def gen(path, tr, tt, size):
    s = "Dec 8 11:33:30 localhost haproxy[0]: 127.0.0.1:666 [08/Dec/2014:11:32:20.938] el_proxy el_proxy/el02.server.com 0/0/1/{0}/{1} 200 {2} - - ---- 1/1/1/0/0 0/0 \"GET {3} HTTP/1.1\""
    return s.format(tr, tt, size, path)


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

tt = 55
size=305
for idx in range(5):
    path = "/foo" + str(idx)
    for tr in range(0, 50000, 22):
        msg = gen(path, tr, tt, size)
        print(msg)
        sock.sendto(bytes(msg, "utf-8"), ("127.0.0.1", 8514))
 

