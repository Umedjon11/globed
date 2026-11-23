from django.shortcuts import render, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Book

class BookListView(LoginRequiredMixin, View):
    template_name = 'library/book_list.html'

    def get(self, request):
        books = Book.objects.filter(is_published=True)
        q = request.GET.get('q', '').strip()
        category = request.GET.get('category', '').strip()

        if q:
            books = books.filter(title__icontains=q) | books.filter(author__icontains=q)
        if category:
            books = books.filter(category=category)

        context = {
            'books': books,
            'categories': Book.CATEGORY_CHOICES,
            'selected_category': category,
            'query': q,
        }
        return render(request, self.template_name, context)


class BookDetailView(LoginRequiredMixin, View):
    template_name = 'library/book_detail.html'

    def get(self, request, pk):
        book = get_object_or_404(Book, pk=pk)
        return render(request, self.template_name, {'book': book})
