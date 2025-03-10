from django.db import models
from django.utils import timezone
from datetime import timedelta

class Book(models.Model):
    ACCESSION_NUMBER_CHOICES = [
        ('borrowed', 'Borrowed'),
        ('available', 'Available'),
        ('returned', 'Returned'),
    ]
    
    accession_number = models.CharField(max_length=20, unique=True)
    author = models.CharField(max_length=100)
    title = models.CharField(max_length=200)
    publisher = models.CharField(max_length=100)
    
    date_borrowed = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=ACCESSION_NUMBER_CHOICES, default='available')
    user = models.ForeignKey('User', null=True, blank=True, on_delete=models.SET_NULL)

    @property
    def expected_return_date(self):
        if self.date_borrowed:
            return self.date_borrowed + timedelta(days=5)  
        return None # if not borrowed

    @property
    def days_remaining(self):
        if self.date_borrowed:
            # Calculate the number of days from the borrowing date to now
            borrowed_days = (timezone.now().date() - self.date_borrowed.date()).days

            # If borrowed today, default to 5 days remaining
            if borrowed_days == 0:
                return 5

            # Calculate remaining days normally
            return 5 - borrowed_days

        # Default to 5 days for books not borrowed yet
        return 5

    def __str__(self):
        return self.title


class User(models.Model):
    USER_TYPE_CHOICES = [
        ('Student', 'Student'),
        ('Staff', 'Staff'),
    ]

    id_number = models.CharField(max_length=6, unique=True)  # 6-digit unique ID
    name = models.CharField(max_length=100) 
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)  # Either Student or Staff

    def __str__(self):
        return f"{self.name} ({self.user_type})"
