
class Master(object):
# master class to partition, schedule jobs

	def __init__(self):
		print("do nothing")


class JobEntry(object):
    def __init__(self, func, data):
        self._func = func
        self._data = data
