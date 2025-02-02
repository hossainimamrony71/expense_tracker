from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import  ExpenceCategroyViewset, user_allocated_money,TransactionViewset,admin_allocated_money, LoanRequestViewSet

router = DefaultRouter()
router.register(r"expence_category", ExpenceCategroyViewset, basename="expence_category")
router.register(r"transaction", TransactionViewset, basename="transaction")
router.register(r"loan_requests", LoanRequestViewSet, basename='loanrequest')
urlpatterns = [
    path("", include(router.urls)),
    path('user_allocated_money/', user_allocated_money, name='user_allocated_money'),
    path('admin_allocated_money/', admin_allocated_money, name='admin_allocated_money'),
]
