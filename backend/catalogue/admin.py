from django.contrib import admin

from .models import Donut


@admin.register(Donut)
class DonutAdmin(admin.ModelAdmin):
    """Admin for Donuts"""

    list_display = ["donut_code", "price", "available"]
    list_editable = ["available"]
    search_fields = ["donut_code"]
