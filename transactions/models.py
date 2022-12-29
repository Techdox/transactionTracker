from django.db import models
# Create your models here.

class AmexTransaction(models.Model):
    # Fields for storing information about the transaction
    CATEGORY_CHOICES = (
        ('lifestyle', 'Lifestyle'),
        ('bills', 'Bills'),
        ('transportation', 'Transportation'),
        ('entertainment', 'Entertainment'),
        ('other', 'Other'),
    )
    date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    merchant = models.CharField(max_length=255)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    notes = models.TextField(blank=True)
    reimbursable = models.BooleanField(default=False)
    def __str__(self):
        return f'Transaction {self.id}: {self.merchant} {self.notes} {self.date} ({self.amount})'
