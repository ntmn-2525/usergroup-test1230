from django.contrib import admin
from .models import (
    Category,
    LineFriend,
    LineSession,
)

admin.site.register(Category)
admin.site.register(LineFriend)
admin.site.register(LineSession)
