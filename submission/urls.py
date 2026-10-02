from rest_framework.routers import DefaultRouter
from .views import FormSubmissionViewSet, ProcessExecutionViewSet


app_name = "submission"

router = DefaultRouter()
router.register("executions", ProcessExecutionViewSet, basename="execution")
router.register("submissions", FormSubmissionViewSet, basename="submission")

urlpatterns = router.urls

