from django.db import migrations


def fill_orderitem_prices(apps, schema_editor):
    OrderItem = apps.get_model("foodcartapp", "OrderItem")

    for order_item in OrderItem.objects.filter(price=0).select_related("product"):
        if order_item.product:
            order_item.price = order_item.product.price
            order_item.save()


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(fill_orderitem_prices),
    ]
