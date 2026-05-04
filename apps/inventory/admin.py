from django.contrib import admin
from .models import ObjectOfExpenditure, ObjectCode, ItemCode, Item

admin.site.register(ObjectOfExpenditure)
admin.site.register(ObjectCode)
admin.site.register(ItemCode)
admin.site.register(Item)