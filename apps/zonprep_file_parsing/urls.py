from django.urls import path
from .views import (SearchAppointmentOrPOViewset, ZonprepAppointmentViewset,
                    ZonprepPurchaseOrderViewset, ZonprepActionViewset)
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'search', SearchAppointmentOrPOViewset, basename='search')
router.register(r'actions', ZonprepActionViewset, basename='actions')

urlpatterns = [
    # List route with appointments
    path('appointments/', ZonprepAppointmentViewset.as_view({'get': 'list'}), name='appointment-list'),
    # Retrieve route with appointments
    path('appointments/<str:appointment_id>/', ZonprepAppointmentViewset.as_view({'get': 'retrieve'}), name='appointment-detail'),
    # Retry appointments to external fulfillment
   
    # List route with purchase orders
    path('purchase-orders/', ZonprepPurchaseOrderViewset.as_view({'get': 'list'}), name='purchase-order-list'),
    # Retrieve route with purchase orders
    path('purchase-orders/<str:po_number>/', ZonprepPurchaseOrderViewset.as_view({'get': 'retrieve'}), name='purchase-order-detail'),
]

urlpatterns = router.urls + urlpatterns