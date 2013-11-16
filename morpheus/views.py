from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, Http404
from master import JobEntry
import pickle
from morpheus.models import JobRecord

# Create your views here.
def job_submit(request):
    if request.method == 'POST':
        job = JobEntry(request.POST.get('function', None),
                        request.POST.get('data'))
        #save file into object file
        number_of_records = JobRecord.objects.filter().count()
        file_name = 'job' + str(number_of_records)
        print file_name
        with open(file_name, 'w') as fout:
            pickle.dump(job, fout)
        record = JobRecord(obj_name=file_name)
        record.save()

        return HttpResponse('job saved successfully job_id--->>' + str(number_of_records))

    return HttpResponse("Not a POST request")

def home(request):
	return render(request, 'morpheus/index.html')
