from django.db import models

# Create your models here.
from django.db import models
class Offers(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новое'),
        ('interesting', 'Интересно'),
        ('not_interesting', 'Не интересно'),
    ]

    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField( null=True, blank=True)
    wanted_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    buyer = models.CharField(max_length=255, null=True, blank=True)
    projects = models.PositiveIntegerField( null=True, blank=True)  # Здесь можно использовать другой тип, если нужно
    deal = models.CharField(max_length=20, null=True, blank=True)
    last_time = models.CharField(max_length=255, null=True, blank=True)
    offers = models.PositiveIntegerField( null=True, blank=True)
    url = models.URLField(max_length=200, null=True, blank=True)
    kwork_id = models.PositiveIntegerField()
    status = models.CharField(max_length=255, null=True, blank=True)
    files = models.TextField( null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True , null=True)
    updated_at = models.DateTimeField(auto_now=True , null=True)
    def __str__(self):
        return f'{self.title} - {self.kwork_id} '