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
    job = JobEntry(request.GET['function'], request.GET['data'], number_of_records + 1)
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
    job = JobRecord.objects.filter(pk=int(request.GET['job_id']))
    print str( )
    res = {'status' : 'no_job'}
    if len(job) == 1:
        # print job[0].status
        res['status'] = job[0].status
        print "computation value " + str( job[0].result )
        if res['status']:
            print 'puting result'
            res['result'] = job[0].result

    return HttpResponse(json.dumps(res), mimetype="application/json")

start_string ="""<html>
    <head>
    </head>
    <body>
        <script type="text/javascript">"""


end_string = """

        var returnAsyncResult = function(result) {
            window.location = 'result://localhost/' + result;
        }

        </script>
    </body>
</html> """

def available(request):
    #inform master about new slave
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('localhost', 5000))
        s.send('A')

        res = s.recv(1024)
        data = pickle.loads(res)
        s.close()
        function = start_string + data._func + end_string
        final_data = {'func' : function, 'data' : data._data,
                    'jobID' : data._jobID, 'subJobID' : data._subJobID}
    except (socket.error, IndexError) as e:
        print e
        final_data = dict()

    return HttpResponse(json.dumps(final_data), mimetype="application/json")

def send_money(phone_number):
    try:
        dw = DwollaUser('CQOdqAEDtrRgUqPXdMmT4UL2BiCH6QPYX59mKelw6tKaN90uOH')
        transactionId = dw.send_funds(0.01, phone_number, '4810', dest_type='Phone')
        print transactionId
    except Exception as e:
        print 'Failed to send money --> ' + str(e)

def completion(request):
    # print request

    print request.GET['jobID']
    print request.GET['subJobID']
    print request.GET['result']
    print request.GET['phone_number']

    message = 'D' + ','.join([request.GET.get('jobID',''),
                                request.GET.get('subJobID',''),
                                request.GET.get('result', '0')])
    phone = request.GET.get('phone_number', '')
    try:
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
            job = JobRecord.objects.filter(pk=int(job_id))
            print 'list of records--> ' + str(len(job))
            job = job[0]
            job.status = True
            print 'slave submission result'  + str(result)
            job.result = result
            print 'elem id = ' +str(job.pk)
            job.save()

        s.close()
    except Exception as e:
        print e

    # except socket.error, e:
    #     print e
    # except
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
