from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'report-type', views.ReportTypeViewSet, basename='report-type')
router.register(r'metric', views.MetricViewSet)
router.register(r'import-batch', views.ImportBatchViewSet)
router.register(r'manual-data-upload', views.ManualDataUploadViewSet,
                basename='manual-data-upload')


urlpatterns = [
    path('chart-data/<report_name>/', views.Counter5DataView.as_view(),
         name='report_type_chart_data'),
    path('chart-data/', views.Counter5DataView.as_view(), {'report_name': None},
         name='chart_data'),
    path('raw-data/', views.RawDataExportView.as_view()),
    path('manual-data-upload/<pk>/preflight', views.ManualDataUploadPreflightCheckView.as_view(),
         name='manual_data_upload_preflight')
]

urlpatterns += router.urls
