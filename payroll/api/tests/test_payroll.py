import os

from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework.test import APITestCase


class TestPayRoll(APITestCase):

    def setUp(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.join(dir_path, "test-01.csv")
        inputs_file = open(file_path, 'rb')
        self.data = SimpleUploadedFile(content=inputs_file.read(),
                                       name=inputs_file.name,
                                       content_type='multipart/form-data')

        self.upload_csv_url = reverse("upload-csv")
        self.retrieve_payroll_url = reverse("retrieve-payroll")

    def test_upload_csv(self):
        # python manage.py test api.tests.test_payroll.TestPayRoll.test_upload_csv

        response = self.client.post(self.upload_csv_url, {'inputs_file': self.data}, format='multipart')
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual('Report with id 1 successfully uploaded', response_data['message'])

    def test_upload_csv_and_retrieve_payroll(self):
        # python manage.py test api.tests.test_payroll.TestPayRoll.test_upload_csv_and_retrieve_payroll

        response = self.client.post(self.upload_csv_url, {'inputs_file': self.data}, format='multipart')
        self.assertEqual(response.status_code, 200)

        response = self.client.get(self.retrieve_payroll_url)
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(3, len(response_data['payrollReport']['employeeReports']))
        self.assertEqual('$150.0', response_data['payrollReport']['employeeReports'][0]['amountPaid'])
        self.assertEqual('$240.0', response_data['payrollReport']['employeeReports'][1]['amountPaid'])
        self.assertEqual('$230.0', response_data['payrollReport']['employeeReports'][2]['amountPaid'])
