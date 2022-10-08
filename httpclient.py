#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body
    def __str__(self):
        return f"Code: {self.code}\n{self.body}"

class HTTPClient(object):
    def get_host_port_path(self,url):
        try:
            o = urllib.parse.urlparse(url)
            if ":" in o.netloc:
                host, port = o.netloc.split(":")
                assert host != None
                assert port != None
                port = int(port)
                return host, port, o.path if o.path else "/" 
            else:
                return o.netloc, 80, o.path if o.path else "/"
        except:
            return None, None, None
    
    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        try:
            return int(data.split(" ")[1])
        except:
            return 500

    def get_headers(self,data):
        return data.split("\r\n\r\n")[0]

    def get_body(self, data):
        return data.split("\r\n\r\n")[1]
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        
        # Parse url
        host, port, reqPath = self.get_host_port_path(url)
        if host is None: return HTTPResponse(404)
        
        # Connect
        try:
            self.connect(host, port)
        except:
            return HTTPResponse(404)
        
        # Send GET REQUEST
        requestStr = ""
        requestStr += "GET {} HTTP/1.1\r\n".format(reqPath)
        requestStr += "Host: {}\r\n".format(host)
        requestStr += "Connection: close\r\n"
        requestStr += "\r\n"
        self.sendall(requestStr)

        # Get results
        res = self.recvall(self.socket)
        self.socket.close()

        # Parse results 
        resCode = self.get_code(res)
        resBody = self.get_body(res)
        resHeaders = self.get_headers(res)


        return HTTPResponse(resCode, resBody)

    def POST(self, url, args=None):
        # Parse url
        host, port, reqPath = self.get_host_port_path(url)
        if host is None: return HTTPResponse(404)
        
        # Connect
        try:
            self.connect(host, port)
        except:
            return HTTPResponse(404)

        parsedArgs = "" if not args else urllib.parse.urlencode(args)
        # Send POST REQUEST
        requestStr = ""
        requestStr += "POST {} HTTP/1.1\r\n".format(reqPath)
        requestStr += "Host: {}\r\n".format(host)
        requestStr += "Content-Type: application/x-www-form-urlencoded\r\n"
        requestStr += "Content-Length: {}\r\n".format(len(parsedArgs))
        requestStr += "Connection: close\r\n"
        requestStr += "\r\n"
        requestStr += parsedArgs

        self.sendall(requestStr)

        # # # Get results
        res = self.recvall(self.socket)
        self.socket.close()

        # # Parse results 
        resCode = self.get_code(res)
        resBody = self.get_body(res)
        resHeaders = self.get_headers(res)

        return HTTPResponse(resCode, resBody)


    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
