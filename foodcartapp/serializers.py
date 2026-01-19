from rest_framework import serializers
from phonenumber_field.serializerfields import PhoneNumberField
from .models import Order, OrderItem, Product
from django.db import transaction


class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), required=True
    )
    quantity = serializers.IntegerField(min_value=1, required=True)

    class Meta:
        model = OrderItem
        fields = ["product", "quantity"]

    def validate(self, data):
        product = data.get("product")
        quantity = data.get("quantity")

        if not product:
            raise serializers.ValidationError({"product": "Товар обязателен"})

        if quantity <= 0:
            raise serializers.ValidationError(
                {"quantity": "Количество должно быть положительным числом"}
            )

        return data


class OrderSerializer(serializers.ModelSerializer):
    products = OrderItemSerializer(
        many=True,
        allow_empty=False,
        source="items",
    )
    phonenumber = PhoneNumberField(region="RU", required=True)

    class Meta:
        model = Order
        fields = ["firstname", "lastname", "phonenumber", "address", "products"]
        extra_kwargs = {
            "firstname": {"required": True, "allow_blank": False},
            "lastname": {"required": True, "allow_blank": False},
            "address": {"required": True, "allow_blank": False},
        }

    def create(self, validated_data):
        items_data = validated_data.pop("items")

        phone_number = validated_data.get("phonenumber")
        if phone_number:
            validated_data["phonenumber"] = str(phone_number)

        with transaction.atomic():
            order = Order.objects.create(**validated_data)

            for item_data in items_data:
                product = item_data.get("product")
                quantity = item_data.get("quantity")

                if not product:
                    raise serializers.ValidationError(
                        {"products": "Товар обязателен для каждой позиции"}
                    )

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price=product.price,
                )

        return order

    def validate(self, data):
        """Общая валидация заказа"""
        items = data.get("items", [])

        for item in items:
            product = item.get("product")
            if not product:
                raise serializers.ValidationError(
                    {"products": "Некорректный ID товара"}
                )

        return data

    def validate_products(self, value):
        if not value or len(value) == 0:
            raise serializers.ValidationError("Список 'products' не может быть пустым.")
        return value
