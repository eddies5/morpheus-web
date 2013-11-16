from django.db import models

# Create your models here.
class JobRecord(models.Model):
    result = models.CharField(max_length=255, blank=True,verbose_name='Calculation Result')
    obj_name = models.CharField(max_length=32, blank=False)