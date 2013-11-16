

class JobEntry(object):
    def __init__(self, func, data, job_id):
        self._func = func
        self._data = data
        self._jobID = job_id

class SubJobEntry(object):
    def __init__(self, func, data, jobID, subJobID):
        self._func       = func
        self._data       = data
        self._jobID      = jobID
        self._subJobID   = subJobID