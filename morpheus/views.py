from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, Http404
from JobEntry import JobEntry, SubJobEntry
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

start_string ="""<html>
    <head>
    </head>
    <body>
        <script type="text/javascript">

        var main = function(data) {"""


end_string = """
        }

        var returnAsyncResult = function(result) {
            window.location = 'result://localhost/' + result;
        }

        </script>
    </body>
</html> """

def available(request):
    #inform master about new slave
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('localhost', 5000))
    s.send('A')
    res = s.recv(1024)
    data = pickle.loads(res)
    print data._jobID
    print data._subJobID
    print data._data
    print data._func

    s.close()
    function = start_string + data._func + end_string
    final_data = {'func' : function, 'data' : data._data,
                    'jobID' : data._jobID, 'subJobID' : data._subJobID}

    return HttpResponse(json.dumps(final_data), mimetype="application/json")

def send_money(phone_number):
    dw = DwollaUser('CQOdqAEDtrRgUqPXdMmT4UL2BiCH6QPYX59mKelw6tKaN90uOH')
    transactionId = dw.send_funds(0.01, phone_number, '4810')
    print transactionId

def completion(request):

    message = 'D' + ','.join([request.GET.get('jobID',''),
                                request.GET.get('subJobID',''),
                                request.GET.get('result', '0')])
    phone = request.GET.get('phone_number', '')
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('localhost', 5000))
    s.send(message)
    res = s.recv(1024)
    if res[0] == 'S' and phone:
        print 'success'
        send_money(phone)
        #send
    elif res[0] == 'Z':
        print 'job end '
        job_id, result = res[1:].split(',')
        send_money(phone)
        job = JobRecord.objects.filter(pk=job_id)[0]
        job.status = True
        job.result = result
        job.save()

    s.close()
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

    return HttpResponse(json.dumps({}), mimetype="application/json")

def showtests(request):

    pass
