from django.db import models
from apps.common.models import TimeStampedModel

class Room(TimeStampedModel):
    TYPE_CHOICES = [
        ('CLASSROOM', 'Classroom / Lecture Hall'),
        ('LAB', 'Laboratory / Practical Room'),
        ('SEMINAR_HALL', 'Seminar Hall / Auditorium'),
    ]

    name = models.CharField(max_length=100, unique=True, db_index=True)
    room_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='CLASSROOM')
    capacity = models.PositiveSmallIntegerField(default=60)
    building = models.CharField(max_length=100, blank=True)
    floor = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_room_type_display()})"
