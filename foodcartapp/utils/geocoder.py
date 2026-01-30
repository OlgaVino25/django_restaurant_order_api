import requests
from django.conf import settings
from geopy.distance import geodesic
import logging
from django.utils import timezone
from requests.exceptions import RequestException

logger = logging.getLogger(__name__)


def fetch_coordinates(apikey, address):
    """Получает координаты через API Яндекса."""
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(
        base_url,
        params={
            "geocode": address,
            "apikey": apikey,
            "format": "json",
        },
        timeout=10,
    )
    response.raise_for_status()
    found_places = response.json()["response"]["GeoObjectCollection"]["featureMember"]

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant["GeoObject"]["Point"]["pos"].split(" ")
    return float(lat), float(lon)


def calculate_distance(coord1, coord2):
    """
    Рассчитывает расстояние между двумя точками в км.
    coord1 и coord2 - кортежи (широта, долгота)
    """
    if not coord1 or not coord2:
        return None
    return round(geodesic(coord1, coord2).km, 3)


def get_or_create_coordinates(address):
    """
    Получает координаты адреса из БД или API Яндекса.
    Кэширует результат в БД.
    """
    from ..models import Place

    if not address or not address.strip():
        return None

    try:
        place = Place.objects.get(address=address)

        if place.lat and place.lon:
            days_old = (timezone.now() - place.updated_at).days
            if days_old < 30:
                return (place.lat, place.lon)

        try:
            coords = fetch_coordinates(settings.YANDEX_GEOCODER_API_KEY, address)
        except (RequestException, KeyError, IndexError, ValueError) as e:
            logger.warning(f"Ошибка геокодирования для адреса {address}: {e}")

            place.save()
            return (place.lat, place.lon) if place.lat and place.lon else None

        if coords:
            place.lat, place.lon = coords
            place.save()
            return coords
        else:
            place.save()
            return None

    except Place.DoesNotExist:

        try:
            coords = fetch_coordinates(settings.YANDEX_GEOCODER_API_KEY, address)
        except (RequestException, KeyError, IndexError, ValueError) as e:
            logger.warning(f"Ошибка геокодирования для адреса {address}: {e}")

            Place.objects.create(address=address, lat=None, lon=None)
            return None

        if coords:
            place = Place.objects.create(address=address, lat=coords[0], lon=coords[1])
            return coords
        else:
            Place.objects.create(address=address, lat=None, lon=None)
            return None


def get_coordinates(address):
    """Алиас для обратной совместимости"""
    return get_or_create_coordinates(address)
