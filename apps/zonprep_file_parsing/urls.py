from .views import SearchAppointmentOrPOViewset
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'search', SearchAppointmentOrPOViewset, basename='search')
urlpatterns = router.urls