from django.contrib import admin

from .models import BbaState


@admin.register(BbaState)
class BbaStateAdmin(admin.ModelAdmin):
    list_display = ("id", "updated_at")
    readonly_fields = ("updated_at",)
