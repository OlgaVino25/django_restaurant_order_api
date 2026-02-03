from django.contrib import admin
from .models import Place


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ["address", "lat", "lon", "updated_at"]
    list_filter = ["updated_at"]
    search_fields = ["address"]
    readonly_fields = ["updated_at"]
    ordering = ["-updated_at"]

    fieldsets = (
        ("Информация о месте", {"fields": ("address", "lat", "lon", "updated_at")}),
    )
