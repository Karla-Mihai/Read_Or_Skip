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
        
        self.assertEqual(response.status_code, 302)  # Redirect to book detail page
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
        
        # Go to the TBR list page
        response = self.client.get(reverse('tbr_list'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.book.title)  # Check if the book is displayed in the TBR list

    def test_add_to_tbr_authenticated(self):
        """Test if the authenticated user can add a book to the TBR list"""
        self.client.login(username="testuser", password="12345")
        response = self.client.post(f"/book/{self.book.id}/add_to_tbr/")
        self.assertEqual(response.status_code, 200)
        tbr_entry = TBR.objects.filter(user=self.user, book=self.book)
        self.assertTrue(tbr_entry.exists())

    def test_logout_view(self):
        # Log in the user first
        self.client.login(username='testuser', password='12345')

        # Make a GET request to the logout view
        response = self.client.get(reverse('logout'))

        # Check that the response is successful and if it renders the logout page
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ROS_App/logout.html')

        # Check that the user is logged out
        user = self.client.session.get('_auth_user_id')
        self.assertIsNone(user)  # User ID is supposed to be None after logout

    def test_add_to_tbr_with_ajax(self):
        """Test that a logged-in user can add a book to their TBR list via AJAX."""
        self.client.login(username="testuser", password="12345")
        
        # Send AJAX POST request to add to TBR
        response = self.client.post(
            f"/book/{self.book.id}/add_to_tbr/",
            HTTP_X_REQUESTED_WITH='XMLHttpRequest' 
        )

        # Check if the response is JSON ans successful
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(str(response.content, encoding='utf8'), {'success': True})

        # Verify that the book is added to the user's TBR list
        tbr_entry = TBR.objects.filter(user=self.user, book=self.book)
        self.assertTrue(tbr_entry.exists())

    def test_add_duplicate_to_tbr_with_ajax(self):
        """Test that a book can't be added twice to the TBR list via AJAX."""
        self.client.login(username="testuser", password="12345")
        
        # Add the book to TBR
        self.client.post(
            f"/book/{self.book.id}/add_to_tbr/",
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        # Trying to add the same book again
        response = self.client.post(
            f"/book/{self.book.id}/add_to_tbr/",
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        # Check if the response is JSON and is a failure
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(str(response.content, encoding='utf8'), {'success': False, 'message': 'This book is already in your TBR list.'})

        # Checking if there is only one entry in the TBR list
        tbr_entry = TBR.objects.filter(user=self.user, book=self.book)
        self.assertEqual(tbr_entry.count(), 1)

    def test_edit_review(self):
        """Test that the user can edit their own review."""
        self.client.login(username="testuser", password="12345")
        review_data = {
            'review': 'Updated review text',
            'summary': 'Updated summary text',
            'rating': 4
        }
        response = self.client.post(reverse('edit_review', args=[self.review.id]), review_data)
        self.assertEqual(response.status_code, 302)  # Redirect to the book detail page
        self.review.refresh_from_db()
        self.assertEqual(self.review.review, 'Updated review text')
        self.assertEqual(self.review.summary, 'Updated summary text')
        self.assertEqual(self.review.rating, 4)

    def test_remove_from_tbr(self):
        """Test that a logged-in user can remove a book from their TBR list."""
        # Add book to TBR list
        TBR.objects.create(user=self.user, book=self.book)
        
        self.client.login(username="testuser", password="12345")
        response = self.client.post(reverse('delete_from_tbr', kwargs={'book_id': self.book.id}))
        self.assertEqual(response.status_code, 302)  # Redirects after successful deletion

        # Check if the book is removed from the user's TBR list
        tbr_entry = TBR.objects.filter(user=self.user, book=self.book)
        self.assertFalse(tbr_entry.exists())
