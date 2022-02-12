from django.contrib import admin
from .models import Activity, PacedRun, Intervals, TimeTrial, CrossTrain
admin.site.register(Activity)
admin.site.register(PacedRun)
admin.site.register(Intervals)
admin.site.register(TimeTrial)
admin.site.register(CrossTrain)

# Register your models here.
