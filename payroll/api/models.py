from django.db import models


class Employee(models.Model):
    GROUP_TYPES = [
        ('A', 'A'),
        ('B', 'B')
    ]
    employee_id = models.CharField(max_length=50, unique=True)
    job_group_type = models.CharField(max_length=50, choices=GROUP_TYPES)


class TimeReport(models.Model):
    report_id = models.IntegerField()
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='employee')
    working_date = models.DateField()
    hours_worked = models.FloatField()
