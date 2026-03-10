from django.core.management.base import BaseCommand
from django.utils import timezone
from places.models import Place
from places.geocoder import get_or_create_coordinates


class Command(BaseCommand):
    help = "Обновляет устаревшие координаты в БД"

    def add_arguments(self, parser):
        parser.add_argument(
            "--days",
            type=int,
            default=30,
            help="Обновлять координаты старше N дней (по умолчанию 30)",
        )
        parser.add_argument(
            "--all", action="store_true", help="Обновить все координаты"
        )

    def handle(self, *args, **options):
        days = options["days"]
        update_all = options["all"]

        if update_all:
            places = Place.objects.all()
        else:
            cutoff_date = timezone.now() - timezone.timedelta(days=days)
            places = Place.objects.filter(updated_at__lt=cutoff_date)

        self.stdout.write(f"Найдено {places.count()} мест для обновления")

        updated = 0
        for place in places:
            self.stdout.write(f"Обновление: {place.address}")
            get_or_create_coordinates(place.address)
            updated += 1

        self.stdout.write(self.style.SUCCESS(f"Обновлено {updated} записей"))
