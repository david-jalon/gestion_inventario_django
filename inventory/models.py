from django.db import models


class MovementType(models.TextChoices):
    ENTRY = 'entry', 'Entrada'
    EXIT = 'exit', 'Salida'


# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name
    
class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    low_stock_threshold = models.IntegerField(default=5)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @property
    def is_low_stock(self):
        return self.stock <= self.low_stock_threshold


class StockMovement(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='movements')
    quantity = models.PositiveIntegerField()
    movement_type = models.CharField(max_length=10, choices=MovementType.choices)
    reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at', '-pk']

    def __str__(self):
        return f"{self.get_movement_type_display()} - {self.product.name} ({self.quantity})"


class CompanySettings(models.Model):
    company_name = models.CharField(max_length=100, default='Mi Empresa')
    logo = models.ImageField(upload_to='company/', blank=True, null=True)
    currency_symbol = models.CharField(max_length=10, default='$')

    class Meta:
        verbose_name_plural = 'company settings'

    def save(self, *args, **kwargs):
        if not self.pk and CompanySettings.objects.exists():
            existing = CompanySettings.objects.first()
            for field in self._meta.fields:
                if field.name != 'id':
                    setattr(existing, field.name, getattr(self, field.name))
            existing.save()
            return existing
        return super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return self.company_name