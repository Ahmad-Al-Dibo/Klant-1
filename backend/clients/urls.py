from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'', views.ClientViewSet, basename='client')
router.register(r'(?P<client_pk>\d+)/contacts', views.ClientContactViewSet, basename='client-contact')
router.register(r'(?P<client_pk>\d+)/addresses', views.AddressViewSet, basename='client-address')

urlpatterns = [
    path('', include(router.urls)),
    path('stats/', views.ClientStatsView.as_view(), name='client-stats'),
    path('export/', views.ClientExportView.as_view(), name='client-export'),
    path('import/', views.ClientImportView.as_view(), name='client-import'),
    path('search/', views.ClientSearchView.as_view(), name='client-search'),
    path('bulk-delete/', views.ClientBulkDeleteView.as_view(), name='client-bulk-delete'),
    path('industry-list/', views.IndustryListView.as_view(), name='industry-list'),
]