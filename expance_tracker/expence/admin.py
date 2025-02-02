from django.contrib import admin
from .models import ExpenceCategory, Transaction

# @admin.register(ExpenceCategory)
# class ExpenceCategoryAdmin(admin.ModelAdmin):
#     list_display = ('name', 'description', 'created_by')  # Correct field name, fixed typo
#     search_fields = ('name', 'description')
#     list_filter = ('created_by',)  # Correct field name, fixed typo

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'category', 'source', 'created_at')
    search_fields = ('user__username', 'category__name', 'source')
    list_filter = ('created_at', 'source', 'category__name')

    def amount(self, obj):
        return obj.ammount  # Fix any previous typos

    amount.short_description = 'Amount'




from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, LoanRequest


@admin.register(LoanRequest)
class LoanRequestAdmin(admin.ModelAdmin):
    list_display = ('from_department', 'to_department', 'amount', 'status', 'requested_at', 'approved_at')
    list_filter = ('status', 'from_department', 'to_department')
    actions = ['approve_loan_requests', 'decline_loan_requests']

    def approve_loan_requests(self, request, queryset):
        for loan_request in queryset.filter(status='pending'):
            try:
                loan_request.approve(user=request.user)
                self.message_user(request, f"Loan {loan_request.id} approved.")
            except ValueError as e:
                self.message_user(request, f"Error approving loan {loan_request.id}: {e}", level='error')
    approve_loan_requests.short_description = "Approve selected loan requests"

    def decline_loan_requests(self, request, queryset):
        for loan_request in queryset.filter(status='pending'):
            try:
                loan_request.decline(user=request.user)
                self.message_user(request, f"Loan {loan_request.id} declined.")
            except ValueError as e:
                self.message_user(request, f"Error declining loan {loan_request.id}: {e}", level='error')
    decline_loan_requests.short_description = "Decline selected loan requests"
