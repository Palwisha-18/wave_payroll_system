import csv
import io
import logging
from datetime import datetime

from api.lib.constants import JOB_GROUP_WAGES
from api.lib.utils import get_date_range
from api.models import Employee, TimeReport
from api.serializers import UploadCSVSerializer
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

logger = logging.getLogger('payroll_api')


class UploadCSVView(generics.CreateAPIView):
    serializer_class = UploadCSVSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        inputs_file = serializer.validated_data['inputs_file']

        report_id = int(inputs_file.name.split('-')[-1].split('.')[0])
        if TimeReport.objects.filter(report_id=report_id).exists():
            return Response({'error_message': f'Report with id {report_id} is already uploaded. Please try a report with different id!'}, status=status.HTTP_400_BAD_REQUEST)

        csv_reader = csv.DictReader(io.StringIO(inputs_file.read().decode('utf-8')))
        for row in csv_reader:
            try:
                employee_obj, created = Employee.objects.get_or_create(employee_id=str(row['employee id']),
                                                                       job_group_type=row['job group'])
                TimeReport.objects.create(
                    employee=employee_obj,
                    working_date=datetime.strptime(row['date'], "%d/%m/%Y"),
                    hours_worked=row['hours worked'],
                    report_id=report_id
                )
            except Exception as e:
                logger.info(f"Exception: {e}")

        return Response({'message': f'Report with id {report_id} successfully uploaded'}, status=status.HTTP_200_OK)


class PayrollRetrieveView(APIView):

    def get(self, request, *args, **kwargs):
        report_data = list(TimeReport.objects.values('employee_id',
                                                     'working_date',
                                                     'hours_worked',
                                                     'employee__job_group_type').order_by('employee_id',
                                                                                          'working_date'))

        employee_info = {}
        try:
            for item in report_data:
                if item['employee_id'] not in employee_info:
                    employee_info[item['employee_id']] = {}
                date_range = get_date_range(item['working_date'])

                if date_range not in employee_info[item['employee_id']]:
                    employee_info[item['employee_id']][date_range] = 0

                employee_info[item['employee_id']][date_range] += item['hours_worked'] * JOB_GROUP_WAGES[
                    item['employee__job_group_type']]

            payroll_info = self.payroll_formatter(employee_info)
        except Exception as e:
            logger.info(f"Exception: {e}")
            return Response({'error_message': f"{e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"payrollReport": payroll_info}, status=status.HTTP_200_OK)

    def payroll_formatter(self, payroll_info):
        employee_reports = []
        for employee_id in payroll_info:
            for period, payment in payroll_info[employee_id].items():
                employee_reports.append({
                    'employeeId': str(employee_id),
                    'payPeriod': {
                        'startDate': period[0],
                        'endDate': period[1]
                    },
                    'amountPaid': f'${payment}'
                })
        return {"employeeReports": employee_reports}
