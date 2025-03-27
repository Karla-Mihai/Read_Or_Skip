import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "WAD.settings")  
django.setup()

import csv
from ROS_App.models import Category, Book


with open('media/books.csv', newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)

    for row in reader:
        category_name = row['category']
        category, created = Category.objects.get_or_create(name=category_name)

        book = Book.objects.create(
            title=row['title'],
            author=row['author'],
            description=row['description'],
            popularity_score=0 
        )

        book.categories.add(category)
        book.save()

        print(f"Successfully added {book.title} by {book.author}")
