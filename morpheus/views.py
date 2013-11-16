from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, Http404
from master import JobEntry
import pickle
from morpheus.models import JobRecord
import socket

# Create your views here.
def job_submit(request):

    job = JobEntry(request.GET.get('function', None),
                    request.GET.get('data', None))
    #save file into object file
    number_of_records = JobRecord.objects.filter().count()
    file_name = 'job' + str(number_of_records)
    print file_name

    with open(file_name, 'w') as fout:
        pickle.dump(job, fout)
    record = JobRecord(obj_name=file_name,status=False)
    record.save()

    #inform master about new job
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect( ('localhost', 5000))
    s.send('j')
    s.send(file_name)
    s.close()

    json_data = simplejson.dumps({'job_id' : record.pk})

    return HttpResponse(json_data, mimetype="application/x-javascript")


def home(request):
	return render(request, 'morpheus/index.html')
