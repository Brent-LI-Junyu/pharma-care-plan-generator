from django.urls import path

from orders import views


urlpatterns = [
    path("api/orders/", views.create_order, name="create_order"),
    path("api/orders/<str:order_id>/", views.get_order, name="get_order"),
    path("api/orders/<str:order_id>/download/", views.download_care_plan, name="download_care_plan"),
]
