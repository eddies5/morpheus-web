#!/usr/bin/env python

# THANKS TO http://ilab.cs.byu.edu/python/socket/echoserver.html

import select
import socket
import sys
import threading
from threading import Lock
import pickle
from collections import deque
import logging
from time import sleep
from morpheus.JobEntry import SubJobEntry


# THANKS TO http://www.shutupandship.com/2012/02/how-python-logging-module-works.html

logger = logging.getLogger('MORPHEUS')
logger.setLevel(logging.DEBUG)
frmt = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh = logging.FileHandler('master.log')
fh.setFormatter(frmt)
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)

class Master(object):
    ScheduledSubJobs = dict()
    scheduledLock = Lock()

    UnScheduledSubJobs = deque()

    results = dict()
    resultLock = Lock()

    subJobCounter = dict()
    counterLock = Lock()

    class Rescheduler(threading.Thread):
        def __init__(self):
            threading.Thread.__init__(self)

        def run(self):
            while 1:
                sleep(15)
                sLock = Master.scheduledLock
                sJobs = Master.ScheduledSubJobs
                sLock.acquire()
                for key in sJobs.keys():
                    Master.UnScheduledSubJobs.append(sJobs.pop(key))
                    logger.debug("putting back key--->>" + key)
                sLock.release()


    class ClientHandler(threading.Thread):
        def __init__(self, (client, address)):
            threading.Thread.__init__(self)
            self.client = client
            self.address = address
            self.size = 1024

        def partitionJob(self, je):
            dataParts  = je._data.split('\n')
            for i, dataPart in enumerate(dataParts) :
                print i, ": ", dataPart
                Master.UnScheduledSubJobs.append(SubJobEntry(je._func, dataPart, je._jobID, i))
            return len(dataParts)

        def run(self):
            data = self.client.recv(self.size)
            if data:
                message = data[0]

                if(message == "A"): # AVAILABILITY
                    logger.debug("Request: A.")
                    try:
                        sbj = Master.UnScheduledSubJobs.pop()
                        key = "{jId}.{sjid}".format(jId=sbj._jobID,sjid=sbj._subJobID)
                        Master.scheduledLock.acquire()
                        Master.ScheduledSubJobs[key] = sbj
                        Master.scheduledLock.release()
                        logger.debug("Job Scheduled: Job ID: " + str(sbj._jobID) + "subJob ID: " + str(sbj._subJobID))
                        self.client.send(pickle.dumps(sbj))
                    except IndexError:
                        self.client.send("No job to do.")
                    self.client.close()

                elif(message == "S"): # JOB SUBMISSION
                    filename = data[1:]
                    logger.debug("Request: S, " + filename)
                    with open(filename, "r") as f:
                        je = pickle.load(f)
                    self.client.close()
                    #record number of partitions
                    count = self.partitionJob(je)
                    Master.counterLock.acquire()
                    Master.subJobCounter[je._jobID] = count
                    Master.counterLock.release()

                    logger.debug("SJBs: " + str(Master.UnScheduledSubJobs))

                elif(message == "D"): # SUB-JOB COMPLETION

                    jobID, subJobID, result = data[1:].split(',')
                    logger.debug("Request: D, for job ID: " + jobID + ", " + subJobID + " done.")
                    key = "{jId}.{sjid}".format(jId=jobID,sjid=subJobID)
                    Master.scheduledLock.acquire()
                    subJob = Master.ScheduledSubJobs.pop(key, None)
                    Master.scheduledLock.release()
                    message = 'F'
                    if subJob:
                        message = 'S'
                        Master.resultLock.acquire()
                        Master.results.put(jobID, results.get(jobID, 0) + int(result))
                        Master.resultLock.release()
                        Master.counterLock.acquire()
                        Master.subJobCounter[jobID] -= 1
                        if Master.subJobCounter[jobID] == 0:
                            message = 'Z' + (str(jobID)+','+str(Master.results.get(jobID)))
                        Master.counterLock.release()

                    # subjob done
                    self.client.send(message)
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
        r = Master.Rescheduler()
        r.start()


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
