#!/usr/bin/env python 

# MANY THANKS TO http://ilab.cs.byu.edu/python/socket/echoserver.html

import select 
import socket 
import sys 
import threading 
import pickle
from collections import deque
import logging

logger = logging.getLogger('master')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('master.log')
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)

class Master(object):
    ScheduledSubJobs = deque()
    UnScheduledSubJobs = deque()
    Slaves = deque()
    
    class ClientHandler(threading.Thread): 
        def __init__(self, (client, address)): 
            threading.Thread.__init__(self) 
            self.client = client 
            self.address = address 
            self.size = 1024 

        def partitionJob(je) :
            dataParts  = je._data.split('\n')
            for i, dataPart in enumerate(dataParts) :
                Master.UnScheduledSubJobs.append(SubJobEntry(je.func, dataParts, je._id, i))

        def run(self): 
            running = 1 
            while running: 
                data = self.client.recv(self.size)
                if data: 
                    message = data[0]
                    
                    if(message == "H"): #HEART BEAT
                        ID = data[1:]
                        logger.debug("Request: H, " + ID)
                        # CALL SOME METHOD
                        self.client.close() 
                        running = 0 
                    
                    elif(message == "S"): # JOB SUBMISSION
                        filename = data[1:]
                        je = pickle.load(filename)
                        logger.debug("Request: S, " + filename)
                        partitionJob(je)
                        self.client.close() 
                        running = 0 
                    
                    elif(message == "D"): # SUB-JOB COMPLETION
                        jobID = data[1:] #self.client.recv(self.size)
                        logger.debug("Request: D, job ID: " + jobID + " done.")
                        # subjob done
                        self.client.close() 
                        running = 0
                    
                    else: 
                        logger.debug("Invalid request.")
                        self.client.close() 
                        running = 0 
                
                else: 
                    self.client.close() 
                    running = 0  
    
    class Scheduler(threading.Thread):
        def __init__(self):
            threading.Thread.__init__(self)
            logger.debug("Created a scheduler.")

        def run(self):
            running = 1
            while running:
                while len(Master.UnScheduledSubJobs) != 0:
                    schedule()

        def schedule():
            while len(Master.Slaves) != 0:
                sjb = Master.UnScheduledSubJobs.pop()
                #assign the sub job!
                Master.ScheduledSubJobs.append(sbj)
                logger.debug("Job Scheduled: Job ID: " + sbj._jobID + "subJob ID: " + sbj._subJobID)
                break

            
    def __init__(self): 
        self.host = 'localhost' 
        self.port = 5000 
        self.backlog = 5 
        self.size = 1024 
        self.server = None 
        self.threads = []
        s = Master.Scheduler()
        s.start()
        self.threads.append(s)

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
            logger.debug("Could not open socket: " + message)
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
                    c = Master.ClientHandler(self.server.accept()) 
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

if __name__ == "__main__": 
    s = Master() 
    s.run()

class JobEntry(object):
    def __init__(self, func, data):
        self._func = func
        self._data = data

    def setId(self, id):
        self._id = id

class SubJobEntry(object):
    def __init__(self, func, data, jobID, subJobID):
        self._func       = func
        self._data       = data
        self._jobID      = jobID
        self._subJobID   = subJobID
