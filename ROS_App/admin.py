import csv
from django.contrib import admin
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import path
from django.contrib import messages
from .models import Book

class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category')
    search_fields = ('title', 'author', 'category')
    actions = ['export_books_to_csv']
    
    fieldsets = [
        (None, {'fields': ['title', 'author', 'description']}),
        ('Media', {'fields': ['cover_image']}),
        ('Details', {'fields': ['category', 'popularity_score']}),
    ]
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('upload-csv/', self.upload_csv, name='upload_csv'),
        ]
        return custom_urls + urls

    def upload_csv(self, request):
        """Allows the superuser to upload a CSV file and add/delete books one by one."""
        if request.method == "POST":
            csv_file = request.FILES.get("csv_file")
            if not csv_file or not csv_file.name.endswith('.csv'):
                messages.error(request, "Please upload a valid CSV file.")
                return HttpResponseRedirect(request.path_info)

            decoded_file = csv_file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)

            for row in reader:
                book, created = Book.objects.get_or_create(
                    id=row["id"],
                    defaults={
                        "title": row["title"],
                        "author": row["author"],
                        "cover_image": row["cover"],
                        "category": row["category"],
                        "description": row["description"],
                    },
                )

                if created:
                    messages.success(request, f'Added: {row["title"]}')
                else:
                    book.title = row["title"]
                    book.author = row["author"]
                    book.cover_image = row["cover"]
                    book.category = row["category"]
                    book.description = row["description"]
                    book.save()
                    messages.info(request, f'Updated: {row["title"]}')

            return HttpResponseRedirect(request.path_info)

        return render(request, "admin/csv_upload.html")

    def export_books_to_csv(self, request, queryset):
        """Exports selected books to a CSV file."""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=books.csv'
        writer = csv.writer(response)
        writer.writerow(['id', 'title', 'author', 'cover', 'category', 'description'])

        for book in queryset:
            writer.writerow([book.id, book.title, book.author, book.cover_image, book.category, book.description])

        return response

    export_books_to_csv.short_description = "Export selected books as CSV"

admin.site.register(Book, BookAdmin)