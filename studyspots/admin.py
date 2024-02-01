from django.contrib import admin
from .models import *


class StudySpaceAdmin(admin.ModelAdmin):
    exclude = (
        'location_ordinal', 'comments', 'overall_ratings', 'comfort_ratings', 'noise_level_ratings',
        'crowdedness_ratings')
    list_display = ['name', 'get_owner']


@admin.register(Admin)
class AdminAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'is_admin']


admin.site.register(Location)
admin.site.register(PendingStudySpace)
admin.site.register(PendingLocation)
admin.site.register(StudySpace, StudySpaceAdmin)
