from django.urls import path
from . import views
from django.shortcuts import redirect

urlpatterns = [
    path("",lambda request: redirect('login', permanent=False)),
    path('login/', views.login_view, name='login'), 
    path('home/', views.home_view, name='home'), 
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('aboutUs/',views.aboutUs_view, name='aboutUs'),
    path('faq/', views.faq_view, name='faq'),
    path('contactUs/', views.contactUs_view, name='contactUs'),
    path('myAccount/',views.myAccount_view, name="myAccount"),
    path('book/<int:book_id>/', views.book_detail, name='book_detail'),
    path('book/<int:book_id>/add_to_tbr/', views.add_to_tbr, name='add_to_tbr'),
    path('tbr/', views.tbr_list, name='tbr_list'),
    path('book/<int:review_id>/delete_review/', views.delete_review, name='delete_review'),
    path('book/<int:review_id>/edit_review/', views.edit_review, name='edit_review'),
    path('book/<int:book_id>/delete_from_tbr/', views.delete_from_tbr, name='delete_from_tbr'),
    path('book/<int:review_id>/book_review/', views.book_review, name='book_review'),
    path("update-account/", views.update_account_view, name="update_account"),
]
