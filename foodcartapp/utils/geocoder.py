import requests
from django.conf import settings
from geopy.distance import geodesic
import logging

logger = logging.getLogger(__name__)


def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(
        base_url,
        params={
            "geocode": address,
            "apikey": apikey,
            "format": "json",
        },
    )
    response.raise_for_status()
    found_places = response.json()["response"]["GeoObjectCollection"]["featureMember"]

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant["GeoObject"]["Point"]["pos"].split(" ")
    return lat, lon


def calculate_distance(coord1, coord2):
    """
    Рассчитывает расстояние между двумя точками в км.
    coord1 и coord2 - кортежи (широта, долгота)
    """
    if not coord1 or not coord2:
        return None
    return round(geodesic(coord1, coord2).km, 3)


def get_coordinates(address):
    """
    Получает координаты адреса с обработкой ошибок.
    """
    try:
        return fetch_coordinates(settings.YANDEX_GEOCODER_API_KEY, address)
    except (requests.exceptions.RequestException, KeyError, IndexError) as e:
        logger.warning(f"Ошибка геокодирования для адреса {address}: {e}")
        return None
