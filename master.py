#!/usr/bin/env python 

# THANKS TO http://ilab.cs.byu.edu/python/socket/echoserver.html

import select 
import socket 
import sys 
import threading 
import pickle
from collections import deque
import logging


# THANKS TO http://www.shutupandship.com/2012/02/how-python-logging-module-works.html

logger = logging.getLogger('MORPHEUS')
logger.setLevel(logging.DEBUG)
frmt = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh = logging.FileHandler('master.log')
fh.setFormatter(frmt)
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)

class Master(object):
    ScheduledSubJobs = deque()
    UnScheduledSubJobs = deque()
    jobMap = {} # jobID -> subJobID -> Boolean
    lock = Lock()
    
    class ClientHandler(threading.Thread): 
        def __init__(self, (client, address)): 
            threading.Thread.__init__(self) 
            self.client = client 
            self.address = address 
            self.size = 1024 

        def partitionJob(self, je):
            dataParts  = je._data.split('\n')
            lock.acquire()
            jobMap[je._jobID] = {}
            for i, dataPart in enumerate(dataParts) :
                Master.UnScheduledSubJobs.append(SubJobEntry(je._func, dataParts, je._jobID, i))
                jobMap[je._jobID][i] = True
            lock.release()

        def schedule(self):
            sjb = Master.UnScheduledSubJobs.pop()
            Master.ScheduledSubJobs.append(sbj)
            logger.debug("Job Scheduled: Job ID: " + sbj._jobID + "subJob ID: " + sbj._subJobID)
            return sjb

        def run(self): 
            data = self.client.recv(self.size)
            if data: 
                message = data[0]
                
                if(message == "A"): # AVAILABILITY
                    logger.debug("Request: A.")
                    if len(Master.UnScheduledSubJobs):
                        sjb = self.schedule()
                        self.client.send(pickle.dumps(sbj))
                    else:
                        self.client.send("No job to do.")
                    self.client.close() 

                elif(message == "S"): # JOB SUBMISSION
                    filename = data[1:]
                    logger.debug("Request: S, " + filename)
                    with open(filename, "r") as f:
                        je = pickle.load(f)
                    self.partitionJob(je)
                    self.client.close() 
                    logger.debug("SJBs: " + str(Master.UnScheduledSubJobs))
                
                elif(message == "D"): # SUB-JOB COMPLETION
                    jobID, subJobID, result = data[1:]
                    logger.debug("Request: D, for job ID: " + jobID + ", " + subJobID + " done.")
                    lock.acquire()
                    del jobMap[jobID][subJobID]
                    ???
                    lock.release()
                    # subjob done
                    self.client.close() 
                
                else: 
                    logger.debug("Invalid request.")
                    self.client.close() 
            
            else: 
                self.client.close() 
            
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
