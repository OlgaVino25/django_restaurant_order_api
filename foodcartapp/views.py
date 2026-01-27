from django.http import JsonResponse
from django.templatetags.static import static
from django.db import transaction
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import Product, Order, OrderItem
from .serializers import OrderSerializer


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

    serializer = OrderSerializer(data=request.data)

    if serializer.is_valid():
        try:
            with transaction.atomic():
                order = serializer.save()
                order_serializer = OrderSerializer(order)
                return Response(order_serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {"error": f"Ошибка при создании заказа: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
