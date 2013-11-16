#!/usr/bin/env python 

# server socket in python
# spit out threads (and not processes)

import select 
import socket 
import sys 
import threading 
import pickle


# master class to partition, schedule jobs
class Master(object):
    def __init__(self): 
        self.host = 'localhost' 
        self.port = 5000 
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
                    # handle the server socket: s.accept() returns client, address
                    c = ClientHandler(self.server.accept()) 
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

# messages: heartbeat: H (from phone), job submission: S (from eddie), I am done: D (phone)

class ClientHandler(threading.Thread): 
    def __init__(self, (client, address)): 
        threading.Thread.__init__(self) 
        self.client = client 
        self.address = address 
        self.size = 1024 
        self.subJobs = {}

    def partitionJob(je) :
        subQueue   = Queue()
        dataParts  = je._data.split('\n')
        counter    = 0
        for dataPart in dataParts :
            self.subJobs[counter] = SubJobEntry(je.func, dataParts, je._id)
            subQueue.put(counter)
            counter += 1

        return subQueue

    def run(self): 
        running = 1 
        while running: 
            data = self.client.recv(self.size)
            if data: 
                m = data[0]
                if(m =="H"):
                    #hearbeat
                    #print "H"
                    self.client.close() 
                    running = 0 
                elif(m=="S"):
                    #print "S"
                    self.client.send("send the filename:")
                    filename = self.client.recv(self.size)
                    je = pickle.load(filename)
                    q = partitionJob(je)
                    #method that split split the job
                    self.client.close() 
                    running = 0 
                elif(m=="D"):
                    #print "D"
                    self.client.send("send the ID:")
                    jobID = self.client.recv(self.size)
                    print "job id: ", jobID
                    # subjob done
                    self.client.close() 
                    running = 0
                else: 
                    print "else"
                    self.client.close() 
                    running = 0 
            else: 
                self.client.close() 
                running = 0 

if __name__ == "__main__": 
    s = Master() 
    s.run()

class JobEntry(object):
    def __init__(self, func, data):
        self._func = func
        self._data = data

    def setId(self, id):
        self._id = id

    def setSubJobIds(self, ids):
        self._subJobIds = ids

class SubJobEntry(object):
    def __init__(self, func, data, id, counter):
        self._func    = func
        self._data    = data
        self._id      = id
        self._counter = counter


