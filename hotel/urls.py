from django.conf.urls import url
from . import views
from django.urls import path
from .views import FoodDeleteView, FoodUpdateView, StaffAdmin, AddStaffView, Add_DeliveryBoy, Thanks
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^cart/$', views.cart, name='cart'),
    url(r'^menu/$', views.menu, name='menu'),
    url(r'^thanks/$', Thanks.as_view(), name='thanks'),
    url(r'^myorders/$', views.my_orders, name='my_orders'),
    
    url(r'^dashboard/admin/users/$', views.users_admin, name='users_admin'),
    url(r'^dashboard/admin/staff/$', StaffAdmin.as_view(), name='staff_admin'),
    url(r'^dashboard/admin/add_staff/$', AddStaffView.as_view(), name='add_staff'),
    url(r'^dashboard/admin/orders/$', views.orders_admin, name='orders_admin'),
    url(r'^dashboard/admin/foods/$', views.foods_admin, name='foods_admin'),
    url(r'^dashboard/admin/$', views.dashboard_admin, name='dashboard_admin'),
    url(r'^dashboard/admin/sales/$', views.sales_admin, name='sales_admin'),
    
    url(r'^dashboard/admin/users/add_user/$', views.add_user, name='add_user'),
    url(r'^dashboard/admin/foods/add_food/$', views.add_food, name='add_food'),
    url(r'^dashboard/admin/sales/add_sales/$', views.add_sales, name='add_sales'),
    # url(r'^dashboard/admin/foods/editFood/(?P<foodID>\d+)/$', views.edit_food, name='edit_food'),
    url(r'^dashboard/admin/foods/foodDetails/(?P<foodID>\d+)/$', views.food_details, name='food_details'),
    url(r'^dashboard/admin/sales/editSale/(?P<saleID>\d+)/$', views.edit_sales, name='edit_sales'),
    
    url(r'^dashboard/admin/orders/confirm_order/(?P<orderID>\d+)/$', views.confirm_order, name='confirm_order'),
    url(r'^dashboard/admin/orders/confirm_delivery/(?P<orderID>\d+)/$', views.confirm_delivery, name='confirm_delivery'),
    
    url(r'^delete_item/(?P<ID>\d+)/$', views.delete_item, name='delete_item'),
    url(r'^add_deliveryBoy/(?P<orderID>\d+)/$', views.add_deliveryBoy, name='add_deliveryBoy'),
    url(r'^add_deliveryBoy/(?P<orderID>\d+)/$', Add_DeliveryBoy.as_view(), name='add_deliveryBoy2'),
    url(r'^placeOrder/$', views.placeOrder, name='placeOrder'),
    url(r'^addTocart/(?P<foodID>\d+)/(?P<userID>\d+)/$', views.addTocart, name='addTocart'),

    url(r'^dashboard/delivery_boy/$', views.delivery_boy, name='delivery_boy'),
    path('dashboard/admin/foods/<int:pk>/update', FoodUpdateView.as_view(), name="edit_food"),
    path('dashboard/admin/foods/<int:pk>/delete', FoodDeleteView.as_view(), name="food_delete"),

]
