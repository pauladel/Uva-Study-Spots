from django.urls import path, re_path
from django.contrib.auth.views import LogoutView

from . import views

app_name = "studyspots"
urlpatterns = [
    # path("", views.index, name="index"),
    re_path(r'^$', views.map, name="map"),
    re_path(r'^map/$', views.map_redirect, name="map_redirect"),
    re_path(r'^add/$', views.add, name="add"),
    path("load/", views.load, name="load"),
    path("confirmation/", views.confirmation, name="confirmation"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("login/", views.profile, name="login"),
    re_path(r'^spot/$', views.get_spot, name="get_spot"),
    re_path(r'^review_spot/$', views.review_studyspace, name="review_studyspace"),
    re_path(r'^process_review/$', views.process_studyspace_review, name="process_studyspace_review"),
    re_path(r'^pending/$', views.pending, name="pending"),
    re_path(r'^pending/approve/$', views.approve_pending, name='approve_pending'),
    re_path(r'^pending/reject/$', views.reject_pending, name='reject_pending'),
    re_path(r'^pending/change_location/$', views.change_location, name='change_location'),
    path("review_confirmation/", views.reviewConfirmation, name="reviewConfirmation"),
]
