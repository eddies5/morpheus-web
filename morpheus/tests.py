from django.test import TestCase
from django.test.client import Client

# Create your tests here.
class JobSubmitTestCase(TestCase):
    def test_job_submit(self):
        c = Client()
        response = c.post('/submit', {'function' : 'def semaple() { sample function}',
            'data' : 'sample data here you go'})
        print response.content

