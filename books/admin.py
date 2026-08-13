from django.contrib import admin
from .models import Book

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "price", "url")
    search_fields = ("title", )
    list_filter = ()
    ordering = ("title", )