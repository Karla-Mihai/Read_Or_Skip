from django.shortcuts import render, redirect, get_object_or_404
from .models import Book, Review, TBR, SkippedBooks
from .forms import ReviewForm, UpdateAccountForm
from django.db import models 
from django.contrib.auth.models import User  
from django.contrib import messages  
from django.contrib.auth import authenticate, login, update_session_auth_hash, logout
from django.contrib.auth.decorators import login_required
from .models import Category
from django.http import JsonResponse
import os
import csv
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render
from django.http import Http404


@login_required
def home_view(request):
    trending_books = [
        {'title': 'Dracula', 'author': 'Bram Stoker', 'cover': 'dracula.jpg', 'id': 1},
        {'title': 'The Midnight Library', 'author': 'Matt Haig', 'cover': '49Mid.jpg', 'id': 2},
        {'title': 'Lord of the Rings', 'author': 'J.R.R. Tolkien', 'cover': '58LOTR1.jpg', 'id': 3},
        {'title': 'It Ends With Us', 'author': 'Collen Hoover', 'cover':'11EndsUs.jpg','id': 4},
    ]
    categories = ['Fantasy', 'Classics', 'Thriller', 'Romance']

    context = {
        'trending_books': trending_books,
        'categories': categories,
    }
    return render(request, 'ROS_App/home.html', context)


def categories_view(request):
    categories = Category.objects.all()  
    return render(request, 'ROS_App/categories.html', {'categories': categories})

def book_detail(request, book_id):
    all_books_by_category = load_books_from_csv()
    all_books = sum(all_books_by_category.values(), [])

# search for book in csv    
    book = next((b for b in all_books if int(b['id']) == book_id), None)
    if not book:
        raise Http404("Book not found")
    
# default
    book_description = book.get('description', 'No description available')

    # Get or create a database Book instance for reviews
    db_book, created = Book.objects.get_or_create(
        id=book_id,
        defaults={
            'title': book['title'],
            'author': book['author'],
            'description': book_description,
            'cover_image': f"books/covers/{book['cover']}"
        }
    )

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.book = db_book
            review.save()
            return redirect('book_detail', book_id=book_id)
    else:
        form = ReviewForm()

    reviews = Review.objects.filter(book=db_book)
    average_rating = reviews.aggregate(models.Avg('rating'))['rating__avg'] or 0

    return render(request, 'books/book_detail.html', {
        'book': {**book, 'id': db_book.id, 'description': book_description},
        'reviews': reviews,
        'form': form,
        'average_rating': average_rating
    })

    

def tbr_list(request):
    if request.user.is_authenticated:
        # Fetch all books in the user's TBR list
        tbr_books = TBR.objects.filter(user=request.user)  # Fetch TBR entries for the logged-in user
        books_in_tbr = [entry.book for entry in tbr_books]  # Get the actual Book instances from TBR

        return render(request, 'ROS_App/tbr_list.html', {'books': books_in_tbr})  # Render the TBR list page
    else:
        return redirect('login') 

@login_required
def add_to_tbr(request, book_id):
    # Ensure the request is POST and the user is authenticated
    if request.method == 'POST' and request.user.is_authenticated:
        book = get_object_or_404(Book, id=book_id)

        # Check if the book is already in the TBR list
        if not TBR.objects.filter(user=request.user, book=book).exists():
            # Add the book to the TBR list if it's not already there
            TBR.objects.create(user=request.user, book=book)
            return JsonResponse({'success': True})  # Respond with success
        
        # If the book is already in the TBR list, return failure
        return JsonResponse({'success': False, 'message': 'This book is already in your TBR list.'})

    # If the user is not authenticated, return failure
    return JsonResponse({'success': False, 'message': 'You need to be logged in to add a book to TBR.'})


def delete_from_tbr(request, book_id):
    # Get the book object by its ID
    book = get_object_or_404(Book, id=book_id)
    
    # Check if the user is authenticated before removing the book from TBR
    if request.user.is_authenticated:
        # Get the TBR entry for the logged-in user and the selected book
        tbr_entry = TBR.objects.filter(user=request.user, book=book).first()
        
        if tbr_entry:
            tbr_entry.delete()  # Delete the TBR entry
        
        # Redirect to the user's TBR list after deletion
        return redirect('tbr_list')
    
    # Redirect to the login page if the user is not logged in
    return redirect('login')

def SkippedBooks_list(request):
    if request.user.is_authenticated:
        Skipped_books = SkippedBooks.objects.filter(user=request.user)  
        books_in_Skipped = [entry.book for entry in Skipped_books]  
        return render(request, 'ROS_App/skipped_books_list.html', {'books': books_in_Skipped})  
    else:
        return redirect('login') 
    
@login_required
def add_to_Skipped(request, book_id):
    # Ensure the request is POST and the user is authenticated
    if request.method == 'POST' and request.user.is_authenticated:
        book = get_object_or_404(Book, id=book_id)

        # Check if the book is already in the skipped list
        if not SkippedBooks.objects.filter(user=request.user, book=book).exists():
            # Add the book to the skipped list if it's not already there
            SkippedBooks.objects.create(user=request.user, book=book)
            return JsonResponse({'success': True})  # Respond with success
        
        # If the book is already in the skipped list, return failure
        return JsonResponse({'success': False, 'message': 'This book is already in your skipped list.'})

    # If the user is not authenticated, return failure
    return JsonResponse({'success': False, 'message': 'You need to be logged in to add a book to Skipped books.'})


def delete_from_Skipped(request, book_id):
    # Get the book object by its ID
    book = get_object_or_404(Book, id=book_id)
    
    # Check if the user is authenticated before removing the book from skipped book list
    if request.user.is_authenticated:
        # Get the TBR entry for the logged-in user and the selected book
        skippedBook_entry = SkippedBooks.objects.filter(user=request.user, book=book).first()
        
        if skippedBook_entry:
            skippedBook_entry.delete()  # Delete the skipped book entry
        
        # Redirect to the user's skipped book list after deletion
        return redirect('skipped_book_list')
    
    # Redirect to the login page if the user is not logged in
    return redirect('login')

def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)

    # Ensure that the logged-in user is the author of the review
    if review.user == request.user:
        review.delete()  # Delete the review

    return redirect('book_detail', book_id=review.book.id)  

@login_required
def edit_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    
    # Ensure that the logged-in user is the author of the review
    if review.user != request.user:
        return redirect('book_detail', book_id=review.book.id)  # Redirect if not the author

    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)  # Bind the form to the existing review
        if form.is_valid():
            form.save()  # Save the updated review
            return redirect('book_detail', book_id=review.book.id)  # Redirect to book detail page
    else:
        form = ReviewForm(instance=review)  # Pre-fill the form with existing review data

    return render(request, 'ROS_App/edit_review.html', {'form': form, 'review': review})

def book_review(request, review_id):
    book = get_object_or_404(Book, id=review_id)  # Fetch the book being reviewed
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user  # Assign the logged-in user to the review
            review.book = book  
            review.save()
            return redirect('book_detail', book_id=review.book.id) 
    else:
        form = ReviewForm()

    reviews = Review.objects.filter(book=book).order_by('-created_at')
    return render(request, 'ROS_App/book_review.html', {'form': form, 'reviews': reviews, 'book': book})

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect('register') 

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect('register')

        user = User.objects.create_user(username=username, email=email, password=password1)
        user.save()

        messages.success(request, "Registration successful! Please log in.")
        return redirect('login') 
    return render(request, 'ROS_App/register.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "You have been logged in successfully.")
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'ROS_App/login.html') 

def aboutUs_view(request):
    return render(request, 'ROS_App/about_us.html') 

def faq_view(request):
    return render(request, 'ROS_App/faq.html')  

def contactUs_view(request):
    return render(request, 'ROS_App/contact_us.html')

@login_required
def myAccount_view(request):
    return render(request, 'ROS_App/my_account.html')

@login_required
def update_account_view(request):
    if request.method == "POST":
        form = UpdateAccountForm(request.POST, instance=request.user)
        if form.is_valid():
            user = form.save()

          
            old_password = form.cleaned_data.get("old_password")
            new_password1 = form.cleaned_data.get("new_password1")
            if old_password and new_password1:
                user.set_password(new_password1)
                user.save()
                update_session_auth_hash(request, user)  

            messages.success(request, "Your account details have been updated successfully!")
            return redirect("myAccount")  
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UpdateAccountForm(instance=request.user)
    return render(request, "ROS_App/update_account.html", {"form": form})

@login_required
def confirm_delete_account(request):
    """GET request shows confirmation form"""
    return render(request, 'ROS_App/delete_account.html')

@login_required
def delete_account(request):
    """POST request processes deletion after password check"""
    if request.method == 'POST':
        password = request.POST.get('password', '')
        
        if not request.user.check_password(password):
            messages.error(request, "Incorrect password. Account not deleted.")
            return redirect('confirm_delete')
            
        request.user.delete()
        logout(request)
        messages.success(request, "Your account has been permanently deleted.")
        return redirect('home')
    

    return redirect('confirm_delete')


def load_books_from_csv():
    books = {
        'Fantasy': [],
        'Thriller': [],
        'Romance': [],
        'Classics': [],
    }

    csv_file_path = os.path.join(settings.MEDIA_ROOT, 'books.csv')

    with open(csv_file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            book_data = {
                'id': row['id'],
                'title': row['title'],
                'author': row['author'],
                'cover': row['cover'],
            }
            category = row['category']
            if category in books:
                books[category].append(book_data)
    
    return books


def fantasy_view(request):
    books = load_books_from_csv() 
    fantasy_books = books.get('Fantasy', []) 
    return render(request, 'ROS_App/fantasy.html', {'fantasy_books': fantasy_books})

def thriller_view(request):
    books = load_books_from_csv()  
    thriller_books = books.get('Thriller', [])  
    return render(request, 'ROS_App/thriller.html', {'thriller_books': thriller_books})


def romance_view(request):
    books = load_books_from_csv() 
    romance_books = books.get('Romance', [])  
    return render(request, 'ROS_App/romance.html', {'romance_books': romance_books})

def classics_view(request):
    books = load_books_from_csv()
    classics_books = books.get('Classics', [])  
    return render(request, 'ROS_App/classics.html', {'classics_books': classics_books})
def search_books(request):
    query = request.GET.get('q', '').strip().lower()
    print(f"Search query: {query}")  # Debugging
    
    category_redirects = {
        'fantasy': 'fantasy',
        'thriller': 'thriller',
        'romance': 'romance',
        'classics': 'classics',
    }
    
    print(f"Checking if '{query}' is in {category_redirects.keys()}")  # Debugging
    if query in category_redirects:
        print(f"Redirecting to {category_redirects[query]}")  # Debugging
        return redirect(category_redirects[query])
    
    return redirect('home')


def logout_view(request):
    logout(request)
    return render(request, 'ROS_App/logout.html')

def user_register(request):
    return render(request, 'ROS_App/register.html')

def user_login(request):
    return render(request, "ROS_App/login.html")

def user_logout(request):
    return render(request, "ROS_App/logout.html")
