#!/usr/bin/python 

# server socket in python
# spit out threads (and not processes)

import select 
import socket 
import sys 
import threading 

# master class to partition, schedule jobs
class Master(object):

	def __init__(self): 
        self.host = '' 
        self.port = 50000 
        self.backlog = 5 
        self.size = 1024 
        self.server = None 
        self.threads = [] 

    def open_socket(self): 
        try: 
            # use TCP and IPv4
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
            self.server.bind((self.host, self.port)) 
            self.server.listen(5) 
        except socket.error, (value, message): 
            if self.server: 
                self.server.close() 
            print "Could not open socket: " + message 
            sys.exit(1) 

    def run(self): 
        self.open_socket() 
        input = [self.server, sys.stdin] 
        running = 1 
        while running: 
            inputready, outputready, exceptready = select.select(input,[],[]) 

            for s in inputready: 

                if s == self.server: 
                    # handle the server socket: client, address = s.accept()
                    c = Client(self.server.accept()) 
                    c.start() 
                    self.threads.append(c) 

                elif s == sys.stdin: 
                    # handle standard input 
                    junk = sys.stdin.readline() 
                    running = 0 

        # close all threads 

        self.server.close() 
        for c in self.threads: 
            c.join() 

class Client(threading.Thread): 
    def __init__(self,(client,address)): 
        threading.Thread.__init__(self) 
        self.client = client 
        self.address = address 
        self.size = 1024 

    def run(self): 
        running = 1 
        while running: 
            data = self.client.recv(self.size) 
            if data: 
                self.client.send(data) 
            else: 
                self.client.close() 
                running = 0 

if __name__ == "__main__": 
    s = Server() 
    s.run()

class JobEntry(object):
    def __init__(self, func, data):
        self._func = func
        self._data = data
