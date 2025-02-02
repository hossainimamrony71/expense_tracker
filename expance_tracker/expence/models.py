from django.db import models
from account.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError

class ExpenceCategory(models.Model):
    creted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='expence_category')

    name = models.CharField(max_length=255)
    description = models.TextField()
    def __str__(self):
        return f"{self.name}"
    


class Transaction(models.Model):
    TRANSACTION_TYPE_CHOICES = (
        ('expense', 'Expense'),
        ("user_allocated_money", "Add money to department"),
        ("admin_allocated_money", "Add money to Admin"),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="transaction")
    ammount = models.DecimalField(max_digits=200, decimal_places=2)
    transaction_type = models.CharField(max_length=50, choices=TRANSACTION_TYPE_CHOICES)
    category = models.ForeignKey( ExpenceCategory, on_delete=models.CASCADE, related_name="category", blank=True, null=True)
    source = models.CharField(max_length=150, default="cash")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} --{self.ammount} "



class LoanRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('declined', 'Declined'),
    )
    
    from_department = models.CharField(max_length=50, choices=User.CHOICES_USER_TYPE)
    to_department = models.CharField(max_length=50, choices=User.CHOICES_USER_TYPE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    requested_at = models.DateField(auto_now_add=True)
    approved_at = models.DateField(null=True, blank=True)
    approved_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='approved_loans')
    
    def __str__(self):
        return f"Loan from {self.get_from_department_display()} to {self.get_to_department_display()} - {self.amount}"
    
    def approve(self, user):
        if self.status != 'pending':
            raise ValueError('Loan is not pending')

        from_user = User.objects.filter(user_type = self.from_department).first()
        to_user = User.objects.filter(user_type = self.to_department).first()
        
        if not to_user or not from_user:
            raise ValueError('User not found')
        
        if self.amount >  to_user.balance:
            raise ValueError('Insufficient balance')
        self.status = "approved"
        self.approved_at = timezone.now()
        self.approved_by = user
        self.save()
        
        #deduct amount form lending department
        to_user.balance  -= self.amount
        to_user.save()
        
        #add amount to requesting department
        from_user.balance += self.amount
        from_user.save()
        
        # Update loan balances
        to_user.loan_balance += self.amount  # Lender is owed more (good)
        from_user.loan_balance -= self.amount  # Borrower owes more (bad)
        from_user.save()
        to_user.save()
        
    def decline(self, user):
        if self.status != 'pending':
            raise ValueError('Loan is not pending')
        self.status = "declined"
        self.approved_at = timezone.now()
        self.approved_by = user
        self.save()
    
    def save(self, *args, **kwargs):
        if self.pk is not None:
            orginal = LoanRequest.objects.get(pk = self.pk)
            if orginal.status == 'approved':
                raise ValidationError('Approved loan requests cannot be updated.')
        super().save(*args, **kwargs)