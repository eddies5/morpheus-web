from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, Http404
from master import JobEntry
import pickle

# Create your views here.
def job_submit(request):
    if request.method == 'POST':
        job = JobEntry(request.POST.get('function', None),
                        request.POST.get('data'))
        with open('object_file.p', 'w') as fout:
            pickle.dump(job, fout)
        return HttpResponse('job saved successfully')

    return HttpResponse("Not a POST request")
