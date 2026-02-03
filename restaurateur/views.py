from django import forms
from django.shortcuts import redirect, render
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test

from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views


from foodcartapp.models import (
    Product,
    Restaurant,
    RestaurantMenuItem,
    Order,
    OrderItem,
)
from places.models import Place
from django.db.models import Case, When, Value, IntegerField
from places.geocoder import get_coordinates
from django.db.models import Prefetch
from collections import defaultdict
from places.geocoder import calculate_distance


class Login(forms.Form):
    username = forms.CharField(
        label="Логин",
        max_length=75,
        required=True,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Укажите имя пользователя"}
        ),
    )
    password = forms.CharField(
        label="Пароль",
        max_length=75,
        required=True,
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Введите пароль"}
        ),
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, "login.html", context={"form": form})

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:  # FIXME replace with specific permission
                    return redirect("restaurateur:RestaurantView")
                return redirect("start_page")

        return render(
            request,
            "login.html",
            context={
                "form": form,
                "ivalid": True,
            },
        )


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy("restaurateur:login")


def is_manager(user):
    return user.is_staff  # FIXME replace with specific permission


@user_passes_test(is_manager, login_url="restaurateur:login")
def view_products(request):
    restaurants = list(Restaurant.objects.order_by("name"))
    products = list(Product.objects.prefetch_related("menu_items"))

    products_with_restaurant_availability = []
    for product in products:
        availability = {
            item.restaurant_id: item.availability for item in product.menu_items.all()
        }
        ordered_availability = [
            availability.get(restaurant.id, False) for restaurant in restaurants
        ]

        products_with_restaurant_availability.append((product, ordered_availability))

    return render(
        request,
        template_name="products_list.html",
        context={
            "products_with_restaurant_availability": products_with_restaurant_availability,
            "restaurants": restaurants,
        },
    )


@user_passes_test(is_manager, login_url="restaurateur:login")
def view_restaurants(request):
    return render(
        request,
        template_name="restaurants_list.html",
        context={
            "restaurants": Restaurant.objects.all(),
        },
    )


def _get_order_queryset():
    """Возвращает QuerySet заказов с аннотацией для сортировки."""
    return (
        Order.objects.with_total_price()
        .exclude(status="completed")
        .select_related("restaurant")
        .prefetch_related(
            Prefetch(
                "items",
                queryset=OrderItem.objects.select_related("product"),
            )
        )
        .annotate(
            status_order=Case(
                When(status="pending", then=Value(1)),
                When(status="assembly", then=Value(2)),
                When(status="delivery", then=Value(3)),
                default=Value(99),
                output_field=IntegerField(),
            )
        )
        .order_by("status_order", "-created_at")
    )


def _collect_addresses(orders, restaurants):
    """Собирает все адреса для геокодирования."""
    addresses_to_geocode = set()

    for order in orders:
        addresses_to_geocode.add(order.address)

    for restaurant in restaurants:
        addresses_to_geocode.add(restaurant.address)

    return addresses_to_geocode


def _build_coordinates_cache(addresses_to_geocode):
    """Создает кэш координат для адресов."""
    existing_places = Place.objects.filter(address__in=addresses_to_geocode)
    coordinates_cache = {}

    for place in existing_places:
        if place.lat and place.lon:
            coordinates_cache[place.address] = (place.lat, place.lon)

    for address in addresses_to_geocode:
        if address not in coordinates_cache:
            coords = get_coordinates(address)
            coordinates_cache[address] = coords

    return coordinates_cache


def _build_restaurant_products_cache():
    """Создает кэш товаров, доступных в каждом ресторане."""
    restaurant_menu_items = RestaurantMenuItem.objects.filter(
        availability=True
    ).select_related("restaurant", "product")

    restaurant_products = {}
    for menu_item in restaurant_menu_items:
        restaurant_id = menu_item.restaurant.id
        if restaurant_id not in restaurant_products:
            restaurant_products[restaurant_id] = set()
        restaurant_products[restaurant_id].add(menu_item.product.id)

    return restaurant_products


def _get_order_product_ids(order):
    """Возвращает множество ID товаров в заказе."""
    return set(item.product.id for item in order.items.all())


def _get_restaurants_with_distances(order_coords, restaurants, coordinates_cache):
    """Возвращает список ресторанов с расстояниями до заказа."""
    restaurants_with_distances = []

    for restaurant in restaurants:
        restaurant_coords = coordinates_cache.get(restaurant.address)
        distance = None

        if order_coords and restaurant_coords:
            distance = calculate_distance(order_coords, restaurant_coords)

        restaurants_with_distances.append(
            {
                "restaurant": restaurant,
                "distance": distance,
                "has_distance": distance is not None,
            }
        )

    restaurants_with_distances.sort(
        key=lambda x: (
            x["distance"] is None,
            x["distance"] if x["distance"] is not None else float("inf"),
        )
    )

    return restaurants_with_distances


def _process_order_with_restaurant(order, coordinates_cache, total_price):
    """Обрабатывает заказ с уже выбранным рестораном."""
    order_coords = coordinates_cache.get(order.address)
    distance_to_selected = None

    if order_coords and order.restaurant.address in coordinates_cache:
        restaurant_coords = coordinates_cache.get(order.restaurant.address)
        if restaurant_coords:
            distance_to_selected = calculate_distance(order_coords, restaurant_coords)

    return {
        "order": order,
        "selected_restaurant": {
            "restaurant": order.restaurant,
            "distance": distance_to_selected,
            "has_distance": distance_to_selected is not None,
        },
        "available_restaurants": [],
        "total_price": total_price,
        "order_has_coords": order_coords is not None,
    }


def _process_order_without_restaurant(
    order, coordinates_cache, restaurant_products, all_restaurants, total_price
):
    """Обрабатывает заказ без выбранного ресторана."""
    order_coords = coordinates_cache.get(order.address)
    order_product_ids = _get_order_product_ids(order)

    matching_restaurants = []
    for restaurant in all_restaurants:
        available_products = restaurant_products.get(restaurant.id, set())
        if order_product_ids.issubset(available_products):
            matching_restaurants.append(restaurant)

    restaurants_with_distances = _get_restaurants_with_distances(
        order_coords, matching_restaurants, coordinates_cache
    )

    return {
        "order": order,
        "selected_restaurant": None,
        "available_restaurants": restaurants_with_distances,
        "total_price": total_price,
        "order_has_coords": order_coords is not None,
    }


@user_passes_test(is_manager, login_url="restaurateur:login")
def view_orders(request):
    orders = _get_order_queryset()
    all_restaurants = list(Restaurant.objects.all())

    addresses_to_geocode = _collect_addresses(orders, all_restaurants)
    coordinates_cache = _build_coordinates_cache(addresses_to_geocode)

    restaurant_products = _build_restaurant_products_cache()

    orders_data = []
    for order in orders:
        total_price = order.total_price

        if order.restaurant:
            order_data = _process_order_with_restaurant(
                order, coordinates_cache, total_price
            )
        else:
            order_data = _process_order_without_restaurant(
                order,
                coordinates_cache,
                restaurant_products,
                all_restaurants,
                total_price,
            )

        orders_data.append(order_data)

    return render(
        request,
        template_name="order_items.html",
        context={
            "order_items": orders_data,
        },
    )
