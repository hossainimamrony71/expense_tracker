# filters.py
import django_filters
from .models import Transaction
from account.models import User

# filters.py
class TransactionFilter(django_filters.FilterSet):
    # **Category Filters**
    category = django_filters.NumberFilter(field_name='category__id', lookup_expr='exact')
    category_name = django_filters.CharFilter(field_name='category__name', lookup_expr='icontains')

    # **Transaction Type Filter**
    transaction_type = django_filters.CharFilter(field_name='transaction_type', lookup_expr='exact')

    # **Date Filters**
    start_date = django_filters.DateFilter(field_name='created_at', lookup_expr='gte')
    end_date = django_filters.DateFilter(field_name='created_at', lookup_expr='lte')

    # **Department Filters (user_type)**
    user_type = django_filters.CharFilter(field_name='user__user_type', lookup_expr='exact')
    user_type_name = django_filters.CharFilter(method='filter_user_type_name')

    # **Amount Filters**
    min_ammount = django_filters.NumberFilter(field_name='ammount', lookup_expr='gte')
    max_ammount = django_filters.NumberFilter(field_name='ammount', lookup_expr='lte')

    # **Source Filter**
    source = django_filters.CharFilter(field_name='source', lookup_expr='icontains')

    class Meta:
        model = Transaction
        fields = [
            'category', 'category_name', 'transaction_type',
            'start_date', 'end_date', 'user_type', 'user_type_name',
            'min_ammount', 'max_ammount', 'source',
        ]

    def filter_user_type_name(self, queryset, name, value):
        return queryset.filter(user__get_user_type_display__icontains=value)
