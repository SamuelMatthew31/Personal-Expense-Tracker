from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Transaction(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='transactions'

    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)

    TYPE_CHOICES = [
        ('IN', 'Income'),
        ('EX', 'Expense'),
    ]

    type = models.CharField(max_length=2, choices=TYPE_CHOICES)
    category = models.CharField(max_length=100)
    description = models.CharField(blank=True)
    transaction_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-transaction_date', '-created_at']

    def __str__(self):
        return f"{self.type} - {self.category} - {self.amount}"
