from django.contrib import admin
from .models import Entity


class EntityAdmin(admin.ModelAdmin):
    list_display = ['pk', 'name', 'code']
    list_editable = ['code']


admin.site.register(Entity, EntityAdmin)
