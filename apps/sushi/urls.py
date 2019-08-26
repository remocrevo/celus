from django.urls import path
from rest_framework.routers import SimpleRouter

from . import views

router = SimpleRouter()
router.register(r'sushi-credentials', views.SushiCredentialsViewSet, basename='sushi-credentials')
router.register(r'counter-report-type', views.CounterReportTypeViewSet)
router.register(r'sushi-fetch-attempt', views.SushiFetchAttemptViewSet)

urlpatterns = [
    path('sushi-fetch-attempt-stats/', views.SushiFetchAttemptStatsView.as_view())
]

urlpatterns += router.urls
