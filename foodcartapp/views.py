import json
from django.http import JsonResponse
from django.templatetags.static import static
from django.db import transaction
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

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

    required_fields = ["firstname", "lastname", "phonenumber", "address", "products"]
    missing_fields = [field for field in required_fields if field not in order_data]

    if missing_fields:
        return Response(
            {"error": f"Отсутствуют обязательные поля: {', '.join(missing_fields)}"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not isinstance(order_data["products"], list):
        return Response(
            {"error": "Поле 'products' должно быть списком"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if len(order_data["products"]) == 0:
        return Response(
            {"error": "Список 'products' не может быть пустым"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    for i, item in enumerate(order_data["products"]):
        if not isinstance(item, dict):
            return Response(
                {"error": f"Элемент {i} в 'products' должен быть объектом"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if "product" not in item:
            return Response(
                {"error": f"Элемент {i} в 'products' должен содержать поле 'product'"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if "quantity" not in item:
            return Response(
                {"error": f"Элемент {i} в 'products' должен содержать поле 'quantity'"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            product_id = int(item["product"])
        except (ValueError, TypeError):
            return Response(
                {"error": f"Элемент {i}: поле 'product' должно быть числом"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            quantity = int(item["quantity"])
            if quantity <= 0:
                return Response(
                    {
                        "error": f"Элемент {i}: поле 'quantity' должно быть положительным числом"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except (ValueError, TypeError):
            return Response(
                {"error": f"Элемент {i}: поле 'quantity' должно быть числом"},
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
                        status=status.HTTP_400_BAD_REQUEST
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
