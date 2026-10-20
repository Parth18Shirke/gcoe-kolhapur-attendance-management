from django.contrib import admin
from .models import Room

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['name', 'room_type', 'capacity', 'building', 'floor', 'is_active']
    list_filter = ['room_type', 'is_active']
    search_fields = ['name']
