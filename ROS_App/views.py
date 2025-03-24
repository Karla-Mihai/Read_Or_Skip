from django.shortcuts import render, redirect, get_object_or_404  # Ensure this is imported
from .models import Book, Review, TBR
from .forms import ReviewForm, UpdateAccountForm
from django.db import models 
from django.contrib.auth.models import User  
from django.contrib import messages  
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from .models import Category

@login_required
def home_view(request):
    trending_books = [
        {'title': 'Dracula', 'author': 'Bram Stoker', 'cover': 'dracula.jpg', 'id': 1},
        {'title': 'The Little Prince', 'author': 'Antoine de Saint-Exupéry', 'cover': 'thelittleprince.jpg', 'id': 2},
        {'title': 'Lord of the Rings', 'author': 'J.R.R. Tolkien', 'cover': 'lordoftherings.jpg', 'id': 3},
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
    # Hardcoded books data
    books = [
        {'id': 1, 'title': 'Dracula', 'author': 'Bram Stoker', 'cover': 'dracula.jpg', 'description': 'A classic horror novel.'},
        {'id': 2, 'title': 'The Little Prince', 'author': 'Antoine de Saint-Exupéry', 'cover': 'thelittleprince.jpg', 'description': 'A philosophical tale.'},
        {'id': 3, 'title': 'Lord of the Rings', 'author': 'J.R.R. Tolkien', 'cover': 'lordoftherings.jpg', 'description': 'An epic fantasy series.'},
    ]
    
    # Find the book that matches the book_id
    book = next((b for b in books if b['id'] == book_id), None)
    
    if not book:
        return redirect('home')  # If book not found, redirecting to the home

    reviews = []  # For now, assume there are no reviews

    # Check if there are reviews in the database
    reviews = Review.objects.filter(book__title=book['title'])
    average_rating = reviews.aggregate(models.Avg('rating'))['rating__avg'] if reviews.exists() else 0

    # Handle review submission
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            new_review = form.save(commit=False)
            new_review.user = request.user  # Attach the logged-in user to the review

            # Simulate a Book instance for review association
            temp_book = Book(id=book['id'], title=book['title'], author=book['author'], description=book['description'], cover_image=book['cover'])
            new_review.book = temp_book  # Assign the temporary Book instance to the review

            new_review.save()  # Save the review
            return redirect('book_detail', book_id=book_id)  # Redirect to the same page after review submission
    else:
        form = ReviewForm()

    return render(request, 'books/book_detail.html', {'book': book, 'reviews': reviews, 'form': form, 'average_rating': average_rating})

@login_required
def add_to_tbr(request, book_id):
    # Get the book object by its ID
    book = get_object_or_404(Book, id=book_id)
    
    # Check if the user is authenticated before adding the book to TBR
    if request.user.is_authenticated:
        # Check if the book is already in the user's TBR list
        if not TBR.objects.filter(user=request.user, book=book).exists():
            # Add the book to the TBR list if it's not already there
            TBR.objects.create(user=request.user, book=book)
        
        # Redirect to the same book detail page after adding the book to TBR
        return redirect('book_detail', book_id=book.id)
    
    # Redirect to the login page if the user is not logged in
    return redirect('login')

# TBR List view
def tbr_list(request):
    if request.user.is_authenticated:
        # Fetch the user's TBR list from the TBR model
        tbr_books = TBR.objects.filter(user=request.user)  # Get all TBR entries for the user
        books_in_tbr = [tbr_entry.book for tbr_entry in tbr_books]  # Get the actual Book instances in TBR

        return render(request, 'ROS_App/tbr_list.html', {'books': books_in_tbr})
    else:
        return redirect('login')  # If the user is not logged in, redirect to login page

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
            review.book = book  # Assign the book being reviewed
            review.save()
            return redirect('book_detail', book_id=review.book.id)  # Redirect to the book detail page
    else:
        form = ReviewForm()

    # Fetch all reviews for the book
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

def myAccount_view(request):
    return render(request, 'ROS_App/my_account.html')

@login_required
def update_account_view(request):
    if request.method == "POST":
        form = UpdateAccountForm(request.POST, instance=request.user)
        if form.is_valid():
            # Update email and username
            user = form.save()

            # Update password if provided
            old_password = form.cleaned_data.get("old_password")
            new_password1 = form.cleaned_data.get("new_password1")
            if old_password and new_password1:
                user.set_password(new_password1)
                user.save()
                update_session_auth_hash(request, user)  # Keep the user logged in

            messages.success(request, "Your account details have been updated successfully!")
            return redirect("myAccount")  # Redirect to the account page
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UpdateAccountForm(instance=request.user)
    return render(request, "ROS_App/update_account.html", {"form": form})

def fantasy_view(request):
    fantasy_books = Book.objects.filter(
        categories__name="Fantasy"
    ).order_by('-popularity_score')
    return render(request, 'ROS_App/fantasy.html', {'fantasy_books': fantasy_books})

def thriller_view(request):
    thriller_books = Book.objects.filter(
        categories__name="Thriller"
    ).order_by('-popularity_score')
    return render(request, 'ROS_App/thriller.html', {'thriller_books': thriller_books})

def romance_view(request):
    romance_books = Book.objects.filter(
        categories__name="Romance"
    ).order_by('-popularity_score')
    return render(request, 'ROS_App/romance.html', {'romance_books': romance_books})

def classics_view(request):
    classics_books = Book.objects.filter(
        categories__name="Classics"
    ).order_by('-popularity_score')
    return render(request, 'ROS_App/classics.html', {'classics_books': classics_books})

def logout_view(request):
    return render(request, 'ROS_App/logout.html')

def user_register(request):
    return render(request, 'ROS_App/register.html')

def user_login(request):
    return render(request, "ROS_App/login.html")

def user_logout(request):
    return render(request, "ROS_App/logout.html")
