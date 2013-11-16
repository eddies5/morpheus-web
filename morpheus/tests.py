from django.test import TestCase
from django.test.client import Client

# Create your tests here.
class JobSubmitTestCase(TestCase):
    def test_job_submit(self):
        c = Client()
        response = c.post('/submit', {'function' : 'def semaple() { sample function}',
            'data' : 'sample data here you go'})
        print response.content
        # second record
        response = c.post('/submit', {'function' : 'def semaple2() { sample function}',
            'data' : 'sample data here you go2'})
        print response.content
        #third record
        response = c.post('/submit', {'function' : 'def semaple3() { sample function}',
            'data' : 'sample data here you go1'})
        print response.content