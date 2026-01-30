from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField
from django.db.models import F, Sum, Value, DecimalField, ExpressionWrapper
from django.db.models.functions import Coalesce
from decimal import Decimal
from django.db.models import Count

class Restaurant(models.Model):
    name = models.CharField("название", max_length=50)
    address = models.CharField(
        "адрес",
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        "контактный телефон",
        max_length=50,
        blank=True,
    )

    class Meta:
        verbose_name = "ресторан"
        verbose_name_plural = "рестораны"

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = RestaurantMenuItem.objects.filter(availability=True).values_list(
            "product"
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField("название", max_length=50)

    class Meta:
        verbose_name = "категория"
        verbose_name_plural = "категории"

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField("название", max_length=50)
    category = models.ForeignKey(
        ProductCategory,
        verbose_name="категория",
        related_name="products",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        "цена", max_digits=8, decimal_places=2, validators=[MinValueValidator(0)]
    )
    image = models.ImageField("картинка")
    special_status = models.BooleanField(
        "спец.предложение",
        default=False,
        db_index=True,
    )
    description = models.TextField(
        "описание",
        max_length=400,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = "товар"
        verbose_name_plural = "товары"

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name="menu_items",
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="menu_items",
        verbose_name="продукт",
    )
    availability = models.BooleanField("в продаже", default=True, db_index=True)

    class Meta:
        verbose_name = "пункт меню ресторана"
        verbose_name_plural = "пункты меню ресторана"
        unique_together = [["restaurant", "product"]]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class OrderQuerySet(models.QuerySet):
    """
    Аннотирует каждый заказ полем total_price - общей суммой заказа.

    Returns:
        QuerySet с дополнительным полем total_price
    """

    def with_total_price(self):
        multiplication = ExpressionWrapper(
            F("items__price") * F("items__quantity"),
            output_field=DecimalField(),
        )

        return self.annotate(
            total_price=Coalesce(Sum(multiplication), Value(Decimal("0.00")))
        )


class Order(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        verbose_name="Ресторан для приготовления",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
    )

    STATUS_CHOICES = [
        ("pending", "Необработанный"),
        ("assembly", "Готовится"),
        ("delivery", "Доставка"),
        ("completed", "Выполнено"),
    ]

    PAYMENT_CHOICES = [("cash", "Наличные"), ("card", "Карта")]

    address = models.TextField("Адрес доставки", max_length=100)
    firstname = models.CharField("Имя", max_length=50, db_index=True)
    lastname = models.CharField("Фамилия", max_length=50, blank=True, db_index=True)
    phonenumber = PhoneNumberField("Телефон", region="RU", db_index=True)
    created_at = models.DateTimeField("Создан", default=timezone.now, db_index=True)
    called_at = models.DateTimeField("Позвонили", null=True, blank=True, db_index=True)
    delivered_at = models.DateTimeField(
        "Доставили", null=True, blank=True, db_index=True
    )
    status = models.CharField(
        "Статус",
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
        db_index=True,
    )

    payment = models.CharField(
        "Способ оплаты",
        max_length=20,
        choices=PAYMENT_CHOICES,
        db_index=True,
    )

    comments = models.TextField("Комментарий", blank=True)

    objects = OrderQuerySet.as_manager()

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Заказ №{self.id} от {self.firstname}"

    def get_available_restaurants(self):
        """
        Возвращает QuerySet ресторанов, которые могут приготовить этот заказ.
        Ресторан может приготовить заказ, если у него есть ВСЕ товары из заказа.
        """
        order_product_ids = self.items.values_list("product_id", flat=True).distinct()

        if not order_product_ids:
            return Restaurant.objects.none()

        restaurants_with_products = (
            Restaurant.objects.filter(
                menu_items__product_id__in=order_product_ids,
                menu_items__availability=True,
            )
            .annotate(matching_products=Count("menu_items__product_id", distinct=True))
            .filter(matching_products=len(order_product_ids))
            .distinct()
        )

        return restaurants_with_products


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="items", verbose_name="Заказ"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="order_items",
        verbose_name="Товар",
    )
    quantity = models.PositiveIntegerField(
        "Количество", default=1, validators=[MinValueValidator(1)]
    )
    price = models.DecimalField(
        "Цена на момент заказа",
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )

    class Meta:
        verbose_name = "Позиция заказа"
        verbose_name_plural = "Позиции заказа"

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
