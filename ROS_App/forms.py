# forms.py
from django import forms
from .models import Review
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class ReviewForm(forms.ModelForm):
    RATING_CHOICES = [
        (1, '1 - Poor'),
        (2, '2 - Fair'),
        (3, '3 - Good'),
        (4, '4 - Very Good'),
        (5, '5 - Excellent'),
    ]
    rating = forms.ChoiceField(choices=RATING_CHOICES, widget=forms.RadioSelect)  # Radio buttons for rating

    class Meta:
        model = Review
        fields = ['review', 'summary', 'rating']

class UpdateAccountForm(forms.ModelForm):
    email = forms.EmailField(required=True, label="Email")
    username = forms.CharField(required=True, label="Username")
    old_password = forms.CharField(
        label="Old Password",
        widget=forms.PasswordInput(),
        required=False,  # Optional field (only required if changing password)
    )
    new_password1 = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(),
        required=False,  # Optional field (only required if changing password)
    )
    new_password2 = forms.CharField(
        label="Confirm New Password",
        widget=forms.PasswordInput(),
        required=False,  # Optional field (only required if changing password)
    )

    class Meta:
        model = User
        fields = ["username", "email"]

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if User.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
            raise ValidationError("This username is already taken.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError("This email is already in use.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        old_password = cleaned_data.get("old_password")
        new_password1 = cleaned_data.get("new_password1")
        new_password2 = cleaned_data.get("new_password2")

        # Validate password change fields
        if old_password or new_password1 or new_password2:
            if not (old_password and new_password1 and new_password2):
                raise ValidationError("All password fields are required to change your password.")
            if new_password1 != new_password2:
                raise ValidationError("The new passwords do not match.")
            if not self.instance.check_password(old_password):
                raise ValidationError("Your old password is incorrect.")
            
        if not (old_password and new_password1 and new_password2):
            raise ValidationError("If you do not wish to update any details, simply go back to my account")
        return cleaned_data