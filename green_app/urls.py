
from django.urls import path,include
from green_app import views
from django.contrib import admin
app_name="green_app"

urlpatterns = [
    
    #path("", views.homepage,name="home"),
    path("", views.category_display,name="home"),
    
    path("wishlistparam", views.wishlistpage,name="wishlistparam"),
    path("addtowishlist/<str:product_name>", views.addtowishlistpage,name="addtowishlist"),
    #addto wishlist VIA CART
    path("addtowishlist_viacart/<str:product_name>", views.addtowishlistpage_viacart,name="addtowishlist_viacart"),
    
    path("cart", views.cartpage,name="cart"),
    path("addtocart/<str:product_name>", views.addtocartpage,name="addtocart"),
    path("cartpage", views.cartpages,name="cartpage"),
    path("dashboard", views.userdashboard,name="dashboard"),
    
    path("login", views.login,name="login"),
    path("signup", views.signup,name="signup"),
    path("logout", views.logout,name="logout"),
    path("allproducts", views.allprodpage,name="allproducts"),
    path('subcategory/<str:category_name>/', views.subcategorypage, name='subcategory'),
    #path("subcategory", views.subcategorypage,name="subcategory"),
    #path("aboutus", views.aboutuspage,name="aboutus"),
    path("checkout", views.checkout,name="checkout"),
    #path('category/', views.category_display, name='category_display'),
    path('productdetails/<str:product_name>/', views.productpage, name='productdetails'),
    path('place_order', views.place_order, name='place_order'),
    path('submit_review/<str:product_name>/', views.submit_review, name='submit_review'),
    path('subscribe', views.subscribe, name='subscribe'),
    path('suggestions/', views.product_suggestions, name='product_suggestions'),
    path('search/', views.search_product, name='search_product'),
    #path('getGlossOptions', views.get_gloss_options, name='get_gloss_options'),
    #path('', views.product_list, name='product_list'),
    path('getGlossOptions/<str:product_name>/', views.get_gloss_options, name='get_gloss_options'),
    path('getPrice/<str:product_name>/', views.get_price, name='get_price'),
    #remove from cart VIA CART
    path('remove-from-cart/', views.remove_from_cart, name='remove_from_cart'),
    path('add_to_cart_viawishlist/<str:product_name>/',views.add_to_cart_viawishlist,name="add_to_cart_viawishlist"),
    #VIA WISHLIST
    path('removefromwishlist/', views.remove_from_wishlist, name='remove_from_wishlist'),
    #path('addtocart_viawishlist/<str:product_name>/', views.add_to_cart, name='add_to_cart'),
    path('update_profile/', views.update_profile, name='update_profile'),
    path('update_order/', views.update_order, name='update_order'),
    
    #PAYMENT METHODS
    path('initiate-payment/', views.initiate_payment, name='initiate_payment'),
    path('payment-callback/', views.payment_callback, name='payment_callback'),
    path('payment-callback/', views.payment_callback, name='payment_callback'),
    path('payment-cancel/', views.payment_cancel, name='payment_cancel'),
    
    
    path('chck', views.checkoutTime, name="checkoutTime"),
    
    path('success', views.success, name="success"),
    path('update_qty',views.update_qty, name="update_qty"),
    
    #GOOGLE
    
    #path('social-auth',include('social_django.urls',namespace='social'))
]
