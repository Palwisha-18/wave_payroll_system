from django.urls import include, path
from api.views import UploadCSVView, PayrollRetrieveView


urlpatterns = [
    path('auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('upload-csv/', UploadCSVView.as_view(), name='upload-csv'),
    path('retrieve-payroll/', PayrollRetrieveView.as_view(), name='retrieve-payroll'),
]