from django.db import models
from django.utils import timezone


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
    days_remaining = models.IntegerField(default=5)
    status = models.CharField(max_length=10, choices=ACCESSION_NUMBER_CHOICES, default='available')
    
    # Associate the book with a user
    user = models.ForeignKey('User', null=True, blank=True, on_delete=models.SET_NULL)
    
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

