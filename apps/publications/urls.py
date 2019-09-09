from rest_framework.routers import SimpleRouter
from rest_framework_nested.routers import NestedSimpleRouter

from logs.views import CustomDimensionsViewSet, OrganizationReportTypesViewSet
from organizations.urls import router as organization_router
from . import views

root_router = SimpleRouter()
root_router.register(r'platform', views.AllPlatformsViewSet, basename='all-platforms')

org_sub_router = NestedSimpleRouter(organization_router, r'organization', lookup='organization')
org_sub_router.register(r'platform', views.PlatformViewSet, basename='platform')
org_sub_router.register(r'detailed-platform', views.DetailedPlatformViewSet,
                        basename='detailed-platform')
org_sub_router.register(r'platform-interest', views.PlatformInterestViewSet,
                        basename='platform-interest')
org_sub_router.register('title', views.TitleViewSet, basename='title')
org_sub_router.register(r'title-count', views.TitleCountsViewSet, basename='title-count')

org_sub_router.register(r'dimensions', CustomDimensionsViewSet,
                        basename='organization-dimensions')
org_sub_router.register(r'report-types', OrganizationReportTypesViewSet,
                        basename='organization-report-types')
org_sub_router.register(r'sushi-credentials-count', views.PlatformSushiCredentialsViewSet,
                        basename='organization-sushi-credentials-count')


title_sub_router = NestedSimpleRouter(org_sub_router, r'title', lookup='title')
title_sub_router.register('reports', views.TitleReportTypeViewSet,
                          basename='title-reports')
title_sub_router.register('report-views', views.TitleReportDataViewViewSet,
                          basename='title-report-data-views')

platform_sub_router = NestedSimpleRouter(org_sub_router, r'platform', lookup='platform')
platform_sub_router.register('title', views.PlatformTitleViewSet, basename='platform-title')
platform_sub_router.register('title-count', views.PlatformTitleCountsViewSet,
                             basename='platform-title-count')
platform_sub_router.register('reports', views.PlatformReportTypeViewSet,
                             basename='platform-reports')
platform_sub_router.register('report-views', views.PlatformReportDateViewViewSet,
                             basename='platform-report-data-views')

platform_title_sub_router = NestedSimpleRouter(platform_sub_router, r'title', lookup='title')
platform_title_sub_router.register('reports', views.PlatformTitleReportTypeViewSet,
                                   basename='platform-title-reports')
platform_title_sub_router.register('report-views', views.PlatformTitleReportDataViewViewSet,
                                   basename='platform-title-report-data-views')

urlpatterns = [
]

urlpatterns += root_router.urls
urlpatterns += org_sub_router.urls
urlpatterns += platform_sub_router.urls
urlpatterns += title_sub_router.urls
urlpatterns += platform_title_sub_router.urls

