import json
from django.http import JsonResponse
from django.templatetags.static import static
from django.db import transaction

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


def register_order(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))
            print("=" * 50)
            print("Получен заказ:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            print("=" * 50)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Неверный JSON"}, status=400)

        try:
            with transaction.atomic():
                order = Order.objects.create(
                    address=data.get("address", ""),
                    firstname=data.get("firstname", ""),
                    lastname=data.get("lastname", ""),
                    phonenumber=data.get("phonenumber", ""),
                )

                order_items = []
                for item in data.get("products", []):
                    product_id = item.get("product")
                    quantity = item.get("quantity", 1)

                    try:
                        product = Product.objects.get(id=product_id)
                        OrderItem.objects.create(
                            order=order,
                            product=product,
                            quantity=quantity,
                            price=product.price,
                        )
                    except Product.DoesNotExist:
                        continue

                return JsonResponse({"id": order.id, "status": "ok"})

        except Exception as e:
            print(f"Ошибка при создании заказа: {e}")
            return JsonResponse({"error": "Ошибка при создании заказа"}, status=500)

    return JsonResponse({"error": "Метод не разрешен"}, status=405)
