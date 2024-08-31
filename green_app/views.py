from django.shortcuts import render,redirect
from django.shortcuts import render, get_object_or_404,get_list_or_404
from django.http import HttpResponse,HttpResponseBadRequest,HttpResponseRedirect
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm
from green_app.forms import SignUpForm,LoginForm,ReviewForm,SearchForm,OrderForm,update
from green_app.models import Profile,Category,Subcategory,Product,SelectedCategory,ProductInfo,NewestArrivals,WishList,Items,Cart,orderDetails,Reviews,Subscription,FishNChips
from django.contrib import messages 
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import WishList  # Import your WishList model
from django.contrib.auth.decorators import login_required
from django.contrib.admin.models import LogEntry, ADDITION
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
# Create your views here.


#===============================================================
#===================HOME PAGE ==================================
def homepage(request):
    query = request.GET.get('term', '').strip()
    products = Product.objects.filter(name__icontains=query) if query else Product.objects.all()
    print(products.name)
    return render(request,"home.html",{'products': products})


#=====================SEARCH BAR================================
def product_suggestions(request):
    form = SearchForm(request.GET or None)
    suggestions = []

    if form.is_valid():
        query = form.cleaned_data.get('term', '').strip()
        if query:
            products = Product.objects.filter(name__icontains=query)
            suggestions = list(products.values('id', 'name'))

    return JsonResponse(suggestions, safe=False)


#==================search (submit button)====================

def search_product(request):
    query = request.GET.get('term', '').strip()
    products = Product.objects.filter(name__icontains=query) if query else Product.objects.all()
    selected_category = SelectedCategory.objects.all()  # Get the first selected category
    newest=NewestArrivals.objects.all()
    
    if request.method == 'GET':
        term = request.GET.get('term', '').strip()
        if term:
            try:
                # Assuming you want to search by product name
                product = Product.objects.get(name__iexact=term)
                return redirect('/productdetails/'+product.name, product_id=product.id)  # Redirect to product detail page
            except Product.DoesNotExist:
                messages.error(request,"No such Products. Try Again and Spell Check")
                return render(request, 'home.html', {"products":products,'selected_category': selected_category,"newest":newest})
        else:
            return render(request, 'home.html', {"products":products,'selected_category': selected_category,"newest":newest})
    return render(request, 'home.html',{"products":products,'selected_category': selected_category,"newest":newest})

#displays category and newest arrival in homepage
def category_display(request):
    selected_category = SelectedCategory.objects.all()  # Get the first selected category
    newest=NewestArrivals.objects.all()
    return render(request, 'home.html', {'selected_category': selected_category,
                                         "newest":newest})
    
#==================HOME ENDED=======================
@csrf_exempt
def addtowishlistpage(request, product_name):
    if request.method == 'POST':
        color = request.POST.get('color')
        gloss = request.POST.get('gloss')
        drainage = request.POST.get('drainage')
        if drainage == "Without Drainage":
            drainage="No"
        elif drainage == "With Drainage": 
            drainage="Yes"
        quantity = request.POST.get('quantity')

        try:
            # Get all ProductInfo instances matching the product_name
            prodInfos = get_list_or_404(ProductInfo, product__name=product_name,color__name=color,gloss=gloss )

            # Create an Items instance for each ProductInfo
            items_ids = []
            for prodInfo in prodInfos:
                item = Items.objects.create(
                    prodInfo=prodInfo,
                    color=color,
                    gloss=gloss,
                    drainage=drainage,
                    quantity=quantity
                )
                items_ids.append(item.id)

            user = request.user
            print(f"Authenticated User: {user} (ID: {user.id})")

            # Retrieve the Profile instance for the user
            p = Profile.objects.filter(user=user).first()

            # Ensure Profile instance exists
            if not p:
                return JsonResponse({'status': 'failed', 'reason': 'User profile not found'})

            print(f"Profile exists: {p}")

            # Check if the profile already has a wishlist
            if not p.wishlist:
                wishlist = WishList.objects.create(name=f"{user.username}'s Wishlist")
                p.wishlist = wishlist
                p.save()
            else:
                wishlist = p.wishlist

            # Add all items to the wishlist
            wishlist.items.add(*items_ids)

            return JsonResponse({'status': 'success', 'item_ids': items_ids})
        except Exception as e:
            return JsonResponse({'status': 'failed', 'reason': str(e)})

    return JsonResponse({'status': 'failed', 'reason': 'Invalid request method'})

#ADD TO WISHLISTPAGE VIA CART PAGE
@csrf_exempt
def addtowishlistpage_viacart(request, product_name):
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        item_id = data.get('item_id')

        try:
            # Ensure the user is authenticated
            if not request.user.is_authenticated:
                return JsonResponse({'status': 'failed', 'reason': 'User not authenticated'})

            # Verify that item_id is provided
            if not item_id:
                return JsonResponse({'status': 'failed', 'reason': 'No item ID provided'})

            # Find the item by ID
            try:
                item = Items.objects.get(id=item_id)
            except Items.DoesNotExist:
                return JsonResponse({'status': 'failed', 'reason': 'Item does not exist'})

            user = request.user
            profile = Profile.objects.get(user=user)

            # Check if the profile already has a wishlist
            if not profile.wishlist:
                wishlist = WishList.objects.create(name=f"{user.username}'s Wishlist")
                profile.wishlist = wishlist
                profile.save()
            else:
                wishlist = profile.wishlist

            # Add the item to the wishlist
            if item not in wishlist.items.all():
                wishlist.items.add(item)
                return JsonResponse({'status': 'success', 'item_id': item_id})
            else:
                return JsonResponse({'status': 'failed', 'reason': 'Item already in wishlist'})

        except Profile.DoesNotExist:
            return JsonResponse({'status': 'failed', 'reason': 'User profile does not exist'})
        except Exception as e:
            return JsonResponse({'status': 'failed', 'reason': str(e)})

    return JsonResponse({'status': 'failed', 'reason': 'Invalid request method'})

def wishlistpage(request,product_name=""):
    if request.user.is_authenticated:
        user = request.user
        print(f"Authenticated User: {user} (ID: {user.id})")
        p= Profile.objects.filter(user=user).exists()
        print(f"Profile exists: {p}")

        if p:
            profile = Profile.objects.get(user=user)
            print(f"Profile retrieved: {profile} (ID: {profile.id})")
            wish = profile.wishlist
            return render(request,"wishlist.html",{"wish":wish})
        else:
            print("Profile does not exist for this user.")
            wish = None
    else:
        print("Sign up FIRST, FROM WISHLISTPAGE")
        #return render(request,"signup.html")
        return redirect('green_app:signup')

#temporarily till we link it with all stuff
def wishlistpagewithoutparam(request):
    if request.user.is_authenticated:
        user=request.user
        return render(request,"wishlist.html",{"user":user})
    else:
        print("Sign up FIRST")
        return redirect('green_app:signup')
        #return render(request,"signup.html")

#==========================================================================
#=========================C A R T ========================================
def cartpage(request,product_name=""):
    if request.user.is_authenticated:
        user=request.user
        fishNchips=FishNChips.objects.filter().first()
        return render(request,"cart.html",{'fishNchips':fishNchips})
    else:
        print("Sign up FIRST")
        return redirect('green_app:signup')
@csrf_exempt

def addtocartpage(request, product_name):
    if request.method == 'POST':
        color = request.POST.get('color')
        gloss = request.POST.get('gloss')
        drainage = request.POST.get('drainage')
        
        # Normalize drainage value
        drainage = 'Yes' if drainage == "With Drainage" else 'No' if drainage == "Without Drainage" else drainage
        
        quantity = request.POST.get('quantity')

        try:
            # Get all ProductInfo instances matching the product_name
            prodInfos = get_list_or_404(ProductInfo, product__name=product_name, color__name=color, gloss=gloss)

            # Create an Items instance for each ProductInfo
            items_ids = []
            for prodInfo in prodInfos:
                item = Items.objects.create(
                    prodInfo=prodInfo,
                    color=color,
                    gloss=gloss,
                    drainage=drainage,
                    quantity=quantity
                )
                items_ids.append(item.id)

            user = request.user

            if user.is_authenticated:
                print(f"Authenticated User: {user} (ID: {user.id})")

                # Retrieve or create the Profile instance for the user
                p = Profile.objects.filter(user=user).first()

                if not p:
                    return JsonResponse({'status': 'failed', 'reason': 'User profile not found'})

                # Check if the profile already has a cart
                if not p.cart:
                    cart = Cart.objects.create(name=f"{user.username}'s Cart")
                    p.cart = cart
                    p.save()
                else:
                    cart = p.cart

                # Add all items to the cart
                cart.items.add(*items_ids)

            else:
                print("Unauthenticated user, saving cart in session")

            return JsonResponse({'status': 'success', 'item_ids': items_ids})

        except Exception as e:
            print(f"Something went wrong: {e}")
            return JsonResponse({'status': 'failed', 'reason': str(e)})

    return JsonResponse({'status': 'failed', 'reason': 'Invalid request method'})

@csrf_exempt
def add_to_cart_viawishlist(request, product_name):
    print('add_to_cart_viawishlist')
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        item_id = data.get('item_id')

        try:
            if not request.user.is_authenticated:
                return JsonResponse({'status': 'failed', 'reason': 'User not authenticated'})

            if not item_id:
                return JsonResponse({'status': 'failed', 'reason': 'No item ID provided'})

            item = Items.objects.get(id=item_id)
            user = request.user
            profile = Profile.objects.get(user=user)

            if profile.cart:
                cart = profile.cart
            else:
                cart = Cart.objects.create(name=f"{user.username}'s Cart")
                profile.cart = cart
                profile.save()

            if item not in cart.items.all():
                cart.items.add(item)
                cart.save()  # Ensure changes are saved to the database
                return JsonResponse({'status': 'success', 'message': 'Item successfully added to the cart'})
            else:
                return JsonResponse({'status': 'failed', 'reason': 'Item already in cart'})

        except Profile.DoesNotExist:
            return JsonResponse({'status': 'failed', 'reason': 'User profile does not exist'})
        except Items.DoesNotExist:
            return JsonResponse({'status': 'failed', 'reason': 'Item does not exist'})
        except Cart.DoesNotExist:
            return JsonResponse({'status': 'failed', 'reason': 'Cart does not exist'})
        except Exception as e:
            return JsonResponse({'status': 'failed', 'reason': str(e)})
    
    return JsonResponse({'status': 'failed', 'reason': 'Invalid request method'})




@csrf_exempt
def remove_from_cart(request):
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        item_id = data.get('item_id')
        
        try:
            # Ensure the user is authenticated
            if not request.user.is_authenticated:
                return JsonResponse({'success': False, 'error': 'User not authenticated'})
            
            # Find the cart item and delete it
            user = request.user
            profile = Profile.objects.get(user=user)
            cart = profile.cart
            item = Items.objects.get(id=item_id)
            
            if item in cart.items.all():
                cart.items.remove(item)
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'error': 'Item not in cart'})
        
        except Items.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Item does not exist'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def cartpages(request):
    fishNchips = FishNChips.objects.filter().first()

    if request.user.is_authenticated:
        user = request.user
        print(f"Authenticated User: {user} (ID: {user.id})")

        # Check if the profile exists for the authenticated user
        profile_exists = Profile.objects.filter(user=user).exists()
        print(f"Profile exists: {profile_exists}")

        if profile_exists:
            profile = Profile.objects.get(user=user)
            print(f"Profile retrieved: {profile} (ID: {profile.id})")
            cart = profile.cart
            return render(request, "cart.html", {"cart": cart, "fishNchips": fishNchips})
        else:
            print("Profile does not exist for this user.")
            # Handle the case where the profile does not exist for an authenticated user
            return render(request, "cart.html", {"cart": None, "fishNchips": fishNchips, "message": "Profile not found"})
    else:
        print("User not authenticated. Redirecting to login.")
        
        print("Sign up FIRST")
        return redirect('green_app:signup')
    
    #def loginpage(request):
#    return render(request,"login.html")

#def signuppage(request):
#    return render(request,"signup.html")

@csrf_exempt
def remove_from_wishlist(request):
    print("HELLO")
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        item_id = data.get('item_id')
        
        try:
            # Ensure the user is authenticated
            if not request.user.is_authenticated:
                return JsonResponse({'success': False, 'error': 'User not authenticated'})
            
            # Find the cart item and delete it
            user = request.user
            profile = Profile.objects.get(user=user)
            wishlist = profile.wishlist
            item = Items.objects.get(id=item_id)
            
            if item in wishlist.items.all():
                wishlist.items.remove(item)
                print("HURRAH")
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'error': 'Item not in cart'})
        
        except Items.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Item does not exist'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})


'''
import json
@csrf_exempt
def add_to_cart(request, product_name):
    print("HERE WE GO")
    try:
        data = json.loads(request.body)
        item_id = data.get('item_id')

        user_profile = Profile.objects.get(user=request.user)
        cart, created = Cart.objects.get_or_create(name=f"{user_profile.user.username}'s Cart")

        item = Items.objects.get(id=item_id)
        cart.items.add(item)
        cart.save()  # Ensure the cart is saved
        user_profile.cart=cart
        user_profile.cart.save()
        # Debug: Check cart contents
        cart_items = user_profile.cart.items.all()
        print(f"Cart items after adding: {list(cart_items)}")

        return JsonResponse({'success': True})

    except Items.DoesNotExist:
        return JsonResponse({'success': False, 'reason': 'Item not found'}, status=404)
    except Profile.DoesNotExist:
        return JsonResponse({'success': False, 'reason': 'Profile not found'}, status=404)
    except Exception as e:
        print(f'Error: {e}')
        return JsonResponse({'success': False, 'reason': str(e)}, status=500)
'''







#==================CHECKOUT======================
#   !!!! NOT USING IT (PLACE_ORDER USED INSTEAD)
def checkout(request):
    
    if request.user.is_authenticated:
        user = request.user
        print(f"Authenticated User: {user} (ID: {user.id})")
        p= Profile.objects.filter(user=user).exists()
        print(f"Profile exists: {p}")
        profile = Profile.objects.get(user=user)
        print(f"Profile retrieved: {profile} (ID: {profile.id})")    
        order_details = orderDetails.objects.filter(profile=profile).order_by('-placedAt').first()
                
        if p:
            if request.method == 'POST':
                response = request.POST.get('response')
                # Ensure that the user has a profile and order details
                
                # Store the response in the order details
                order_details.gift = response
                order_details.save()
            
            cart = profile.cart
            total_price=0
            for i in cart.items.all():
                total_price+=i.prodInfo.price*i.quantity
            fishNchips=FishNChips.objects.filter().first()
            return render(request,"checkout.html",{"cart":cart ,"prof":profile,'total_price':total_price,"fishNchips":fishNchips,"order_details":order_details})
        else:
            print("Profile does not exist for this user.")
            cart = None
            return redirect('green_app:signup')

    else:
        print("Sign up FIRST, FROM CHECKOUT")
        return redirect('green_app:signup')

#def allprodpage(request):
#    return render(request,"allprod.html")
def subcategorypage(request, category_name):
    category = get_object_or_404(Category, name=category_name)
    subcategories = category.subcategories.all()

    for subcategory in subcategories:
        # Get all ProductInfo objects for each subcategory
        product_infos = ProductInfo.objects.filter(subcategory=subcategory)
        # Use a Python set to filter out duplicate products based on product name
        seen_products = set()
        unique_product_infos = []
        for product_info in product_infos:
            if product_info.product.name not in seen_products:
                seen_products.add(product_info.product.name)
                unique_product_infos.append(product_info)
        subcategory.unique_product_infos = unique_product_infos

    return render(request, 'subcat.html', {
        'category': category,
        'subcategories': subcategories
    })

#def aboutuspage(request):


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('green_app:home')  # Replace with your home page or desired redirect page
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})

def login(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect('green_app:home')  # Redirect to a home page or any other page
        else:
            messages.error(request,"User Name or Password is incorrect.")    
    else:
        form = LoginForm()
        
    return render(request, 'login.html', {'form': form})

def logout(request):
    auth_logout(request)
    return redirect('green_app:home')  # Redirect to the login page or any other page


def allprodpage(request):
    #allprod=ProductInfo.objects.all()
    product_infos = ProductInfo.objects.all()
    seen_products = set()
    unique_product_infos = []
    for product_info in product_infos:
        if product_info.product.name not in seen_products:
            seen_products.add(product_info.product.name)
            unique_product_infos.append(product_info)
    return render(request,"allprod.html",{"allprod":unique_product_infos,})
    
    
def productpage(request, product_name):    # Filter all ProductInfo objects for the given product name
    prodInfos = ProductInfo.objects.filter(product__name=product_name)
   
    rev=Reviews.objects.all()
    
     # Calculate average rating for each product
    product_ratings =0.0
    reviews = Reviews.objects.filter(products__name=product_name)
    if reviews:
        avg_rating = sum(r.ratings for r in reviews) / len(reviews)
        avg_rating = format(avg_rating, ".1f")
        
        product = get_object_or_404(Product, name=product_name)
        product.rating = float(avg_rating)  # Convert to float for saving
        product.save()
    else:
        avg_rating = None
    return render(request, "product.html", {"prodInfos": prodInfos,"reviews":rev,"avgrating":avg_rating})


def userdashboard(request):
    if request.user.is_authenticated:
        user = request.user
        if user.is_superuser:#admin
            o=orderDetails.objects.all()
            return render(request, "dashboard.html", {"order":o})
            
        elif user:
            u = Profile.objects.get(user=user)
            o=orderDetails.objects.filter(profile=u).order_by('-placedAt')
            return render(request, "dashboard.html", {"profile": u,"order":o})
    else:
        print("Sign up FIRST")
        return redirect('green_app:signup')
    
#==============CHECKOUT======================
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.admin.models import LogEntry
from django.contrib.contenttypes.models import ContentType
from django.contrib.admin.models import ADDITION
from .models import Profile, orderDetails, Items, Cart, ProductInfo

@login_required
def place_order(request):
    if request.method == 'POST':
        try:
            # Get the profile of the logged-in user
            user_profile = Profile.objects.get(user=request.user)
            print("USER IS :" + user_profile.full_name)

            # Get the user's cart
            user_cart = user_profile.cart
            if not user_cart:
                messages.error(request, 'No cart found for this user.')
                return redirect('green_app:home')

            #check for the gift (YES OR NO)
            response = request.POST.get('response')
            # Process the response value as needed
            if response == 'yes':
                # Handle 'yes' response
                print("User responded with Yes")
            elif response == 'no':
                # Handle 'no' response
                print("User responded with No")
            
            # Create a new order instance with the current user's profile
            new_order = orderDetails(
                status='incomplete',  # Default value, can be set based on form input if needed
                gift=response,  # Default value, can be changed based on form input
                profile=user_profile,
                #orderItems=user_cart
            )
            new_cart = Cart()
            new_cart.save()
            new_cart.items.set(user_profile.cart.items.all())
            new_cart.save()
            #new_order.orderItems.items.set(user_profile.cart.items.all())
            new_order.orderItems=new_cart
            
            new_order.save()
            print("IIIIIIIIIIIIIIIIIIIIIIIIII")
            print(new_order.gift)
            print("^^^^^^^")
            for i in new_order.orderItems.items.all():
                print("*")
                print(i)
                
            print("=================")
            o=orderDetails.objects.filter(profile=user_profile)
            for order in o:
                if order.orderItems is not None:
                    for item in order.orderItems.items.all():  # Assuming 'orderItems' is a related name for the ManyToMany or ForeignKey field
                        # Do something with 'item'
                        print(item) 
                        print("/////")
            # Process items from the cart
            for cart_item in user_cart.items.all():
                # Create an order item using the details from the cart
                order_item = Items(
                    prodInfo=cart_item.prodInfo,
                    color=cart_item.color,
                    drainage=cart_item.drainage,
                    gloss=cart_item.gloss,
                    quantity=cart_item.quantity
                )
                
                order_item.save()
                # Update inventory for the ProductInfo
                product_info = cart_item.prodInfo
                if product_info.inventory >= cart_item.quantity:
                    product_info.inventory -= cart_item.quantity
                    product_info.save()
                else:
                    # Handle the case where there is insufficient inventory
                    messages.error(request, f'Insufficient inventory for product {product_info.product.name}.')
                    #return redirect('green_app:addtocart')
                    #return render(request,"cart.html",{"cart":user_cart ,"prof":user_profile,'total_price':total_price,"fishNchips":fishNchips,"order_details":new_order})
                    return redirect('green_app:cartpage')    
                    #return redirect('green_app:place_order'))
            # Print details of items in the order
            print("Order details:")
            for item in user_cart.items.all():
                print(f"Item: {item.prodInfo.product.name}, Color: {item.color}, Gloss: {item.gloss}, Drainage: {item.drainage}, Quantity: {item.quantity}")

            # Log the action in the admin log
            LogEntry.objects.log_action(
                user_id=request.user.id,
                content_type_id=ContentType.objects.get_for_model(orderDetails).pk,
                object_id=new_order.id,
                object_repr=str(new_order),
                action_flag=ADDITION,
                change_message="Order placed successfully."
            )
            #messages.success(request, user_profile.full_name + ' has placed the order successfully!')
            print("ORDER CREATED ")
            print('CHOICE IS '+new_order.gift)
            total_price=0
            for i in user_cart.items.all():
                total_price+=i.prodInfo.price*i.quantity
            fishNchips=FishNChips.objects.filter().first()
            return render(request,"checkout.html",{"cart":user_cart ,"prof":user_profile,'total_price':total_price,"fishNchips":fishNchips,"order_details":new_order})
            
            
            # Redirect to the homepage
            #return redirect('green_app:checkout')

        except Profile.DoesNotExist:
            # Handle the case where the user's profile does not exist
            messages.error(request, 'No profile associated with this account. Please update your profile information.')
            return redirect('green_app:home')

    # If it's not a POST request, redirect to the homepage
    print("NOT A POST REQUEST")
    return redirect('green_app:home')

#================HOMEPAGE (EMAIL GIFT)=====================

def subscribe(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            # Save the email to the database
            subscription, created = Subscription.objects.get_or_create(email=email)
            if created:
                messages.success(request, 'Thank you for subscribing!')
            else:
                messages.success(request, 'You are already subscribed.')
        return redirect('green_app:home')  # Redirect to a home page or any other page
    return render(request, 'home.html')
#==================REVIEWS===============================

def submit_review(request,product_name):
    if request.user.is_authenticated:
        if request.method == 'POST' :
            form = ReviewForm(request.POST, request.FILES)
            if form.is_valid():
                review = form.save(commit=False)
                review.profile = request.user.profile  # Set profile if needed
                review.products=Product.objects.get(name=product_name)
                review.save()
                r=Reviews.objects.all()
                for review in r:
                    print(review.description)
                messages.success(request, 'Review submitted successfully!')
                return redirect('green_app:home')  # Redirect to the homepage or wherever appropriate
            else:
                # Print the form errors in the console for debugging
                print(form.errors)
                messages.error(request, 'There was a problem with your submission.')
                return redirect(reverse('green_app:productdetails', args=[product_name]))
        else:
            form = ReviewForm()
        print("OOPSY")
        re=Reviews.objects.all()
        
        return render(request, 'product.html', {'form': form,"reviews":re})
    else:
        #NO ACCOUNT
        messages.error(request,"Signup or Login before reviewing")
        return redirect('green_app:login') 

def get_gloss_options(request,product_name):
    color = request.GET.get('color')
    if not color:
        return JsonResponse({'error': 'No color provided'}, status=400)

    # Retrieve distinct gloss options for the given color
    gloss_options = ProductInfo.objects.filter(color__name=color,product__name=product_name).values_list('gloss', flat=True).distinct()
    print("==========")
    print(gloss_options)
    if not gloss_options:
        return JsonResponse({'glossOptions': []})

    return JsonResponse({'glossOptions': list(gloss_options)})

def get_price(request, product_name):
    color = request.GET.get('color')
    gloss = request.GET.get('gloss')
    
    if not color or not gloss:
        return JsonResponse({'error': 'Missing parameters'}, status=400)
    
    products = ProductInfo.objects.filter(product__name=product_name, color__name=color, gloss=gloss)
    
    if products.exists():
        product = products.first()  # Get the first product from the QuerySet
        return JsonResponse({'price': product.price})
    else:
        return JsonResponse({'error': 'Product not found'}, status=404)
#======================================================
#UPDATE DASHBOARD PERSONAL INFO

@login_required
def update_profile(request):
    # Fetch the user's profile
    profile = Profile.objects.get(user=request.user)
    
    if request.method == 'POST':
        form = update(request.POST, instance=profile)  # Use ProfileForm
        if form.is_valid():
            form.save()
            print("Successful update")
            return redirect('green_app:dashboard')  # Redirect to the dashboard or any success page
        else:
            print("END")
            print(form.errors)  # Print form errors for debugging
    else:
        form = update(instance=profile)  # Use ProfileForm for the GET request

    return render(request, 'dashboard.html', {'profile': profile, 'form': form})
#===============================================================
#SAVE THE GRAND TOTAL OF ORDER
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import orderDetails
from .forms import OrderForm
def update_order(request):
    if request.method == 'POST':
        profile = request.user.profile
        
        # Fetch the most recent order for the profile
        order_details = orderDetails.objects.filter(profile=profile).order_by('-placedAt').first()
        
        if not order_details:
            return redirect('green_app:home')
        
        form = OrderForm(request.POST, request.FILES, instance=order_details)
        if form.is_valid():
            grandTotal = request.POST.get('grandTotal', '0')
            order_details.grandTotal = grandTotal
            order_details.paymentMethod = form.cleaned_data.get('paymentMethod')
            order_details.status='inprogress'
            
            if order_details.paymentMethod=="COD" or order_details.paymentMethod=="cod":
                order_details.paymentStatus="COD"
            if order_details.paymentMethod=="Online" or order_details.paymentMethod=="online":
                order_details.paymentStatus="Pending"
            # Check if payment method is 'online' and handle file upload accordingly
            if form.cleaned_data.get('paymentMethod') == 'online' and not request.FILES.get('paymentProof'):
                form.add_error('paymentProof', 'This field is required for online payments.')
                return render(request, 'checkout.html', {'form': form})
                
            # Save the order details
            order_details.save()
            messages.success(request, f"{profile.full_name} has placed the order successfully!")
            return redirect('green_app:checkout')
        else:
            # Debug form errors
            print("Form errors:", form.errors)
            return render(request, 'checkout.html', {'form': form})
    else:
        profile = request.user.profile
        order_details = orderDetails.objects.filter(profile=profile).order_by('-placedAt').first()
        
        if not order_details:
            return redirect('some_error_page')
        
        form = OrderForm(instance=order_details)
    
    return render(request, 'checkout.html', {'form': form})

def update_qty(request):
    if request.method == 'POST':
        # Get the item ID and the new quantity from the POST request
        item_id = request.POST.get('item_id')
        new_quantity = request.POST.get('quantity')
        
        try:
            # Fetch the item from the cart using the item_id
            item = get_object_or_404(Items, id=item_id)
            
            # Update the quantity of the item
            item.quantity = new_quantity
            item.save()
            
            messages.success(request, 'Quantity updated successfully!')
        except Exception as e:
            messages.error(request, f'Failed to update quantity: {str(e)}')
        
        # Redirect to the cart page or wherever appropriate
        return redirect('green_app:cartpage')
    else:
        print("NOT POST")
        return redirect('green_app:home')
#PAYMENT METHOD
# views.py
# views.py
# views.py
import hashlib
import requests
from django.conf import settings
from django.shortcuts import redirect, render
from django.http import HttpResponseBadRequest
import logging
logging.basicConfig(level=logging.DEBUG)  # Ensure logging is configured to capture debug level logs

logger = logging.getLogger(__name__)

def generate_signature(payload, integrity_salt):
    """
    Generate a signature for the request using the payload and integrity salt.
    """
    data_string = "&".join(f"{key}={value}" for key, value in sorted(payload.items()))
    signature = hashlib.sha256(f"{data_string}{integrity_salt}".encode()).hexdigest()
    return signature

def initiate_payment(request):
    if request.method == 'GET':
        amount = request.GET.get('amount')
        phone_number = request.GET.get('phone_number')
        email = request.GET.get('email')
        
        if not (amount and phone_number and email):
            return HttpResponseBadRequest("Missing payment details.")
        
        payload = {
            'amount': amount,
            'phone_number': phone_number,
            'email': email,
            'merchant_id': settings.JAZZCASH_MERCHANT_ID,
            'password': settings.JAZZCASH_PASSWORD,
            'return_url': 'http://127.0.0.1:8001/payment-callback/',  # Replace with your actual return URL
            'cancel_url': 'http://127.0.0.1:8001/payment-cancel',  # Replace with your actual cancel URL
        }
        
        # Generate the signature
        payload['signature'] = generate_signature(payload, settings.JAZZCASH_INTEGRITY_SALT)
        
        # Make the request to JazzCash Sandbox
        response = requests.post(settings.JAZZCASH_BASE_URL, data=payload)
        
        print(f'JazzCash Response Status: {response.status_code}')
        print(f'JazzCash Response Content: {response.text}')
        
        if response.status_code == 200:
            response_data = response.json()
            payment_url = response_data.get('payment_url')
            if payment_url:
                return redirect(payment_url)
            else:
                return render(request, 'home.html', {'error': 'Payment URL not received from JazzCash.'})
        else:
            return render(request, 'home.html', {'error': 'Error initiating payment with JazzCash.'})
    
    return render(request, 'initiate_payment.html')

def payment_callback(request):
    payment_status = request.GET.get('status')
    transaction_id = request.GET.get('transaction_id')
    
    # Update your payment record based on the callback data
    # e.g., Payment.objects.filter(transaction_id=transaction_id).update(status=payment_status)
    
    return render(request, 'payment_success.html', {'status': payment_status})
from django.shortcuts import render

def payment_cancel(request):
    # Handle payment cancellation
    return render(request, 'payment_cancel.html', {'message': 'Payment was cancelled'})


#========================================================


def calculate_secure_hash(data, salt):
    # Prepare data string for hash calculation
    sorted_data = sorted((k, v) for k, v in data.items() if v)
    hash_string = '|'.join(f"{k}={v}" for k, v in sorted_data)
    hash_string += f"|{salt}"

    # Calculate the hash
    secure_hash = hmac.new(salt.encode(), hash_string.encode(), hashlib.sha256).hexdigest().upper()
    
    # Log for debugging
    print("Hash String:", hash_string)
    print("Calculated Secure Hash:", secure_hash)
    
    return secure_hash
# Create your views here.
JAZZCASH_MERCHANT_ID = "MC118355"
JAZZCASH_PASSWORD = "5uzs2u4470"
JAZZCASH_RETURN_URL = "http://127.0.0.1:8001/success"
JAZZCASH_INTEGRITY_SALT = "281hw3g20c"
import hmac
import hashlib
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from datetime import datetime, timedelta

def checkoutTime(request):

    product_name = "Subscribe Webcog"
    product_price = 100

    pp_Amount = int(product_price)

    current_datetime = datetime.now()
    pp_TxnDateTime = current_datetime.strftime('%Y%m%d%H%M%S')

    expiry_datetime = current_datetime + timedelta(hours=1)
    pp_TxnExpiryDateTime = expiry_datetime.strftime('%Y%m%d%H%M%S')

    pp_TxnRefNo = "T" + pp_TxnDateTime
    post_data = {
        "pp_Version": "1.0",
        "pp_TxnType": "",
        "pp_Language": "EN",
        "pp_MerchantID": JAZZCASH_MERCHANT_ID,
        "pp_SubMerchantID": "",
        "pp_Password": JAZZCASH_PASSWORD,
        "pp_BankID": "TBANK",
        "pp_ProductID": "RETL",
        "pp_TxnRefNo": pp_TxnRefNo,
        "pp_Amount": pp_Amount,
        "pp_TxnCurrency": "PKR",
        "pp_TxnDateTime": pp_TxnDateTime,
        "pp_BillReference": "billRef",
        "pp_Description": "Description of transaction",
        "pp_TxnExpiryDateTime": pp_TxnExpiryDateTime,
        "pp_ReturnURL": JAZZCASH_RETURN_URL,
        "pp_SecureHash": "",
        "ppmpf_1": "1",
        "ppmpf_2": "2",
        "ppmpf_3": "3",
        "ppmpf_4": "4",
        "ppmpf_5": "5"
    }

    # Calculate secure hash
    pp_SecureHash = calculate_secure_hash(post_data, settings.JAZZCASH_INTEGRITY_SALT)
   
    post_data['pp_SecureHash'] = pp_SecureHash

    context = {
        'product_name':product_name,
        "product_price":product_price,
        'post_data':post_data
    }

    return render(request, 'index.html', context)

@csrf_exempt
def success(request):
    return render(request, 'success.html')