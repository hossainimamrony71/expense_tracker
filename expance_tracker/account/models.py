from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

class User(AbstractUser):
    CHOICES_USER_TYPE = (
        ('admin', 'Admin'),
        ("ted", "TED"), 
        ("s2l", "S2L"),
    )
    balance = models.DecimalField(max_digits=200, decimal_places=2, default=0)
    loan_balance = models.DecimalField(max_digits=200, decimal_places=2, default=0)
    user_type = models.CharField(max_length=50,choices=CHOICES_USER_TYPE)

    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"