from django.test import TestCase
from django.contrib.auth.models import User
from .models import Book, TBR, Review
from django.urls import reverse

class TBRTest(TestCase):

    def setUp(self):
        # Creating a user
        self.user = User.objects.create_user(username="testuser", password="12345")
        # Creating a book
        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            description="Test Description",
            cover_image="books/covers/test_cover.jpg"
        )
        self.review = Review.objects.create(
            user=self.user,
            book=self.book,
            review="Great book!",
            summary="An amazing read.",
            rating=5
        )

    def test_add_to_tbr(self):
        """Test if the user can add a book to their TBR list."""
        self.client.login(username="testuser", password="12345")
        response = self.client.post(reverse('add_to_tbr', kwargs={'book_id': self.book.id}))
        
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(str(response.content, encoding='utf8'), {'success': True})
        
        # Check if the book is added to the user's TBR list
        tbr_entry = TBR.objects.filter(user=self.user, book=self.book)
        self.assertTrue(tbr_entry.exists())

    def test_add_duplicate_to_tbr(self):
        """Test that a book can't be added twice to the TBR list."""
        self.client.login(username="testuser", password="12345")
        self.client.post(reverse('add_to_tbr', kwargs={'book_id': self.book.id}))
        response = self.client.post(reverse('add_to_tbr', kwargs={'book_id': self.book.id}))
        
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(str(response.content, encoding='utf8'), 
                             {'success': False, 'message': 'This book is already in your TBR list.'})
        
        # Check that only one entry exists in the TBR list
        tbr_entry = TBR.objects.filter(user=self.user, book=self.book)
        self.assertEqual(tbr_entry.count(), 1)

    def test_book_not_found(self):
        """Test that trying to add a non-existing book to TBR results in a 404 error."""
        self.client.login(username="testuser", password="12345")
        response = self.client.post(reverse('add_to_tbr', kwargs={'book_id': 999}))  # Non-existent book ID
        self.assertEqual(response.status_code, 404)

    def test_delete_review(self):
        """Test that the user can delete their own review."""
        self.client.login(username="testuser", password="12345")
        
        # Create a review for the book
        review = Review.objects.create(
            user=self.user,
            book=self.book,
            review='Review to delete',
            summary='Summary to delete',
            rating=3
        )
        
        # Delete the review
        response = self.client.post(reverse('delete_review', kwargs={'review_id': review.id}))
        
        self.assertEqual(response.status_code, 302)  # Redirects to book detail page
        self.assertFalse(Review.objects.filter(id=review.id).exists())  # Check if the review is deleted

    def test_add_to_tbr_not_logged_in(self):
        """Test that an unauthenticated user cannot add a book to their TBR list."""
        response = self.client.post(reverse('add_to_tbr', kwargs={'book_id': self.book.id}))
        self.assertEqual(response.status_code, 302)  # Should redirect to the login page
        self.assertRedirects(response, '/login/?next=/book/1/add_to_tbr/')

    def test_add_to_tbr_logged_in(self):
        """Test if an authenticated user can add a book to their TBR list."""
        self.client.login(username="testuser", password="12345")
        response = self.client.post(reverse('add_to_tbr', kwargs={'book_id': self.book.id}))
        
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(str(response.content, encoding='utf8'), {'success': True})
        
        # Check if the book is added to the user's TBR list
        tbr_entry = TBR.objects.filter(user=self.user, book=self.book)
        self.assertTrue(tbr_entry.exists())

    def test_tbr_list_display(self):
        """Test if the TBR list page displays the books correctly."""
        self.client.login(username="testuser", password="12345")
        
        # Add the book to TBR list
        TBR.objects.create(user=self.user, book=self.book)
        
        # Visit the TBR list page
        response = self.client.get(reverse('tbr_list'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.book.title)  # Check if the book is displayed in the TBR list
