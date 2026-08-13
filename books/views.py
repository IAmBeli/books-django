from django.shortcuts import render
from .models import Book

def book_list(request):
    books = Book.objects.order_by("title")
    return render(request, "books/book_list.html", {"books": books})