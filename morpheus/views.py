from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, Http404
from JobEntry import JobEntry
import pickle
from models import JobRecord
import socket
import json
from dwolla import DwollaUser

def job_submit(request):
    
    #save file into object file
    number_of_records = JobRecord.objects.filter().count()
    file_name = 'job' + str(number_of_records)
    print file_name
    print request.GET['function']
    print request.GET['data']
    print number_of_records
    job = JobEntry(request.GET['function'], request.GET['data'], number_of_records)
    with open(file_name, 'w') as fout:
        pickle.dump(job, fout)
    record = JobRecord(obj_name=file_name, status=False)
    record.save()

    # inform master about new job
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect( ('localhost', 5000))
    s.send('S' + file_name)

    s.close()

    json_data = json.dumps({'job_id' : record.pk})
    return HttpResponse(json_data, mimetype="application/json")


def home(request):
	return render(request, 'morpheus/index.html')


def check_status(request):
    print request.GET['job_id']
    job = JobRecord.objects.filter(pk=request.GET['job_id'])
    res = {'status' : 'no_job'}
    if len(job) == 1:
        # print job[0].status
        res['status'] = job[0].status

    return HttpResponse(json.dumps(res), mimetype="application/json")

def available(request):
    print request.GET['uid']
    #inform master about new slave
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('localhost', 5000))
    s.send('A')
    res = s.recv(1024)
    pickle.loads(res)
    s.close()

    return HttpResponse(json.dumps(res), mimetype="application/json")

def completion(request):
    # job_id, subjobid, result
    # phone number
    # s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # s.connect(('localhost', 5000))
    # s.send('D')
    # s.send(request.GET['job_id'])
    # s.send(request.GET['subjobid'])
    # s.send(request.GET['result'])
    # request.GET['phonenumber']
    # s.close()

    dw = DwollaUser('CQOdqAEDtrRgUqPXdMmT4UL2BiCH6QPYX59mKelw6tKaN90uOH')

    transactionId = dw.send_funds(0.01, '812-908-5908', '4810')
    print transactionId
    
    return HttpResponse(json.dumps({}), mimetype="application/json")
