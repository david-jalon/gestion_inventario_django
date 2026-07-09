from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Product, StockMovement


@receiver(post_save, sender=Product)
def track_stock_changes(sender, instance, created, **kwargs):
    if created:
        if instance.stock > 0:
            StockMovement.objects.create(
                product=instance,
                quantity=instance.stock,
                movement_type='entry',
                reason='Stock inicial',
            )
    else:
        try:
            old = sender.objects.get(pk=instance.pk)
            diff = instance.stock - old.stock
            if diff > 0:
                StockMovement.objects.create(
                    product=instance,
                    quantity=diff,
                    movement_type='entry',
                    reason='Ajuste de stock',
                )
            elif diff < 0:
                StockMovement.objects.create(
                    product=instance,
                    quantity=abs(diff),
                    movement_type='exit',
                    reason='Ajuste de stock',
                )
        except sender.DoesNotExist:
            pass
