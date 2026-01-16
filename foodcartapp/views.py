import json
from django.http import JsonResponse
from django.templatetags.static import static
from django.db import transaction
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from phonenumber_field.phonenumber import PhoneNumber
from phonenumbers import NumberParseException

from .models import Product, Order, OrderItem


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse(
        [
            {
                "title": "Burger",
                "src": static("burger.jpg"),
                "text": "Tasty Burger at your door step",
            },
            {
                "title": "Spices",
                "src": static("food.jpg"),
                "text": "All Cuisines",
            },
            {
                "title": "New York",
                "src": static("tasty.jpg"),
                "text": "Food is incomplete without a tasty dessert",
            },
        ],
        safe=False,
        json_dumps_params={
            "ensure_ascii": False,
            "indent": 4,
        },
    )


def product_list_api(request):
    products = Product.objects.select_related("category").available()

    dumped_products = []
    for product in products:
        dumped_product = {
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "special_status": product.special_status,
            "description": product.description,
            "category": (
                {
                    "id": product.category.id,
                    "name": product.category.name,
                }
                if product.category
                else None
            ),
            "image": product.image.url,
            "restaurant": {
                "id": product.id,
                "name": product.name,
            },
        }
        dumped_products.append(dumped_product)
    return JsonResponse(
        dumped_products,
        safe=False,
        json_dumps_params={
            "ensure_ascii": False,
            "indent": 4,
        },
    )


def _validate_string_field(data, field_name, required=True):
    """Валидация строкового поля"""
    if field_name not in data:
        if required:
            return f"Это обязательное поле."
        return None

    value = data[field_name]

    if not isinstance(value, str):
        return "Not a valid string."

    if required and not value.strip():
        return "Это обязательное поле."

    return None


def _validate_phonenumber(data):
    """Валидация номера телефона"""
    if "phonenumber" not in data:
        return "Это обязательное поле."

    phonenumber = data["phonenumber"]

    if not isinstance(phonenumber, str):
        return "Not a valid string."

    if not phonenumber.strip():
        return "Это обязательное поле."

    try:
        phone_number = PhoneNumber.from_string(phonenumber, region="RU")
        if not phone_number.is_valid():
            return "Введен некорректный номер телефона."
    except NumberParseException:
        return "Введен некорректный номер телефона."

    return None


def _validate_products(data):
    """Валидация списка продуктов"""
    if "products" not in data:
        return "Это обязательное поле."

    products = data["products"]

    if not isinstance(products, list):
        return "Поле 'products' должно быть списком."

    if len(products) == 0:
        return "Список 'products' не может быть пустым."

    for i, item in enumerate(products):
        if not isinstance(item, dict):
            return f"Элемент {i} в 'products' должен быть объектом."

        if "product" not in item:
            return f"Элемент {i} в 'products' должен содержать поле 'product'."

        if "quantity" not in item:
            return f"Элемент {i} в 'products' должен содержать поле 'quantity'."

        try:
            product_id = int(item["product"])
        except (ValueError, TypeError):
            return f"Элемент {i}: поле 'product' должно быть числом."

        try:
            quantity = int(item["quantity"])
            if quantity <= 0:
                return f"Элемент {i}: поле 'quantity' должно быть положительным числом."
        except (ValueError, TypeError):
            return f"Элемент {i}: поле 'quantity' должно быть числом."

    return None


def _normalize_phone(phone_str):
    """Нормализация номера телефона"""
    try:
        phone_number = PhoneNumber.from_string(phone_str, region="RU")
        if phone_number.is_valid():
            return phone_number.as_e164
        return None
    except NumberParseException:
        return None


@api_view(["GET", "POST"])
def register_order(request):
    if request.method == "GET":
        return Response(
            {
                "message": "Для создания заказа отправьте POST запрос с JSON",
                "example": {
                    "firstname": "Иван",
                    "lastname": "Иванов",
                    "phonenumber": "+79001234567",
                    "address": "Москва, ул. Пушкина, д. 1",
                    "products": [
                        {"product": 1, "quantity": 2},
                        {"product": 3, "quantity": 1},
                    ],
                },
            }
        )

    order_data = request.data
    errors = {}

    string_fields = [
        ("firstname", True),
        ("lastname", True),
        ("address", True),
    ]

    for field_name, required in string_fields:
        error = _validate_string_field(order_data, field_name, required)
        if error:
            errors[field_name] = error

    phone_error = _validate_phonenumber(order_data)
    if phone_error:
        errors["phonenumber"] = phone_error

    products_error = _validate_products(order_data)
    if products_error:
        errors["products"] = products_error

    if errors:
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)

    normalized_phone = _normalize_phone(order_data["phonenumber"])
    if not normalized_phone:
        return Response(
            {"phonenumber": "Введен некорректный номер телефона."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        with transaction.atomic():
            order = Order.objects.create(
                firstname=order_data["firstname"],
                lastname=order_data["lastname"],
                phonenumber=order_data["phonenumber"],
                address=order_data["address"],
            )

            for item in order_data["products"]:
                product_id = item["product"]
                quantity = item["quantity"]

                try:
                    product = Product.objects.get(id=product_id)
                except Product.DoesNotExist:
                    return Response(
                        {"error": f"Товар с ID {product_id} не найден"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price=product.price,
                )

            return Response({"id": order.id}, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response(
            {"error": f"Ошибка при создании заказа: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
