from django.contrib import admin

# Register your models here.
from .models import CardLabel, Collection

admin.site.register(CardLabel)
admin.site.register(Collection)
