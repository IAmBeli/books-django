from django.shortcuts import render
from .models import Book
from django.core.paginator import Paginator

def book_list(request):
    books = Book.objects.order_by("title")
    paginator = Paginator(books, 20)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(request, "books/book_list.html", {"page": page})