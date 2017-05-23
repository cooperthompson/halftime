from django.db import models


class ScheduleManager(models.Manager):
    def get_queryset(self):
        return super(ScheduleManager, self).get_queryset()
