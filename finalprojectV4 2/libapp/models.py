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
    edition = models.CharField(max_length=100, null=True, blank=True)
    volume = models.IntegerField(null=True, blank=True)
    pages = models.IntegerField(null=True, blank=True)
    publisher = models.CharField(max_length=100)
    year = models.IntegerField()
    isbn = models.CharField(max_length=20, unique=True)
    
    
    date_borrowed = models.DateTimeField(null=True, blank=True)
    days_remaining = models.IntegerField(default=5)  
    status = models.CharField(max_length=10, choices=ACCESSION_NUMBER_CHOICES, default='available')

    def __str__(self):
        return self.title
