from django.db import models


class Place(models.Model):
    address = models.CharField("Адрес", max_length=200, unique=True, db_index=True)
    lat = models.FloatField("Широта", null=True, blank=True, db_index=True)
    lon = models.FloatField("Долгота", null=True, blank=True, db_index=True)
    updated_at = models.DateTimeField("Дата обновления", auto_now=True, db_index=True)

    class Meta:
        verbose_name = "Место"
        verbose_name_plural = "Места"
        ordering = ["address"]

    def __str__(self):
        return (
            f"{self.address}: {self.lat}, {self.lon}"
            if self.lat and self.lon
            else self.address
        )
