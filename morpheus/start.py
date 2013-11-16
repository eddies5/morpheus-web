import subprocess

#create a separate process for running the master.py
masterProcess = subprocess.call("python master.py", shell=True)

#process for running djangoserver
serverProcess = subprocess.call("python ../manage.py runserver", shell=True)