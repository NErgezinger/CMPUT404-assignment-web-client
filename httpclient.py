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

import time
import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse
from urllib.parse import quote

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_host_port_path(self, url):
        if url[:7] == 'http://':
            url = url[7:]
        elif url[:8] == 'https://':
            url = url[8:]

        host_port = url.split('/')[0].split(':')
        host = host_port[0]
        if len(host_port) > 1:
            port = int(host_port[1])
        else:
            port = 80
        path = '/' + '/'.join(url.split('/')[1:])

        return host, port, path

    def get_code(self, data):
        return int(data.split()[1])

    def get_headers(self,data):
        return data.split("\r\n\r\n")[0]

    def get_body(self, data):
        return data.split("\r\n\r\n")[1]
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.shutdown(socket.SHUT_WR)
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
        return buffer.decode('ISO-8859-1')

    def GET(self, url, args=None):

        host, port, path = self.get_host_port_path(url)

        data_send = "GET " + path + " HTTP/1.1\r\n" + "Host: " + host + "\r\nAccept: */*\r\nConnection: close\r\n\r\n"

        self.connect(host, port)
        self.sendall(data_send)

        data_recv = self.recvall(self.socket)

        code = self.get_code(data_recv)
        body = self.get_body(data_recv)

        self.close()

        return HTTPResponse(code, body)

    def POST(self, url, args=None):
            
        host, port, path = self.get_host_port_path(url)

        data_send = "POST " + path + " HTTP/1.1\r\n" + "Host: " + host + "\r\nAccept: */*\r\nConnection: close\r\nUser-Agent: Assignment/2\r\n"

        if args is not None:

            arg_string = ""
            for i, (key, value) in enumerate(args.items()):
                arg_string += quote(key) + '=' + quote(value)
                if i != len(args)-1:
                    arg_string += '&'
            
            content_length = len(arg_string)

            data_send += "Content-Length: " + str(content_length) + "\r\n"
            data_send += "Content-Type: application/x-www-form-urlencoded\r\n\r\n"

            data_send += arg_string
        else:
            data_send += "Content-Length: 0"
        
        data_send += '\r\n\r\n'

        print(data_send)

        self.connect(host, port)
        self.sendall(data_send)

        data_recv = self.recvall(self.socket)

        code = self.get_code(data_recv)
        body = self.get_body(data_recv)

        self.close()

        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        response = client.command( sys.argv[2], sys.argv[1] )
        print("Code:", response.code)
        print("Body:")
        print(response.body)
    elif (len(sys.argv) == 4):

        # Split data string into dict
        args_split = sys.argv[3].split('&')
        args = {}
        for arg in args_split:
            key, value = arg.split('=')
            args[key] = value
        
        response = client.command( sys.argv[2], sys.argv[1], args )
        print("Code:", response.code)
        print("Body:")
        print(response.body)
    else:
        response = client.command( sys.argv[1] )
        
