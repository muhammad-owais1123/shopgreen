from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import reverse
from green_app.models import Profile, Category, Subcategory, SelectedCategory, Product, Color, ProductInfo,NewestArrivals,WishList,Items,Cart,orderDetails,Reviews,Subscription,FishNChips
from django.utils.html import format_html,format_html_join

#variables
admin.site.register(FishNChips)

# Admin for Profile model
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'contact', 'display_wishlist','display_cart')

    def display_wishlist(self, obj):
        wishlist = obj.wishlist
        if wishlist:
            items_details = "<br>".join(
                [f"Name: {item.prodInfo.product.name}, Color: {item.color}, Gloss: {item.gloss}, Drainage: {item.drainage}, Quantity: {item.quantity}, Price: {item.prodInfo.price}, SubTotal: {item.prodInfo.price * item.quantity}" 
                 for item in wishlist.items.all()]
            )
            return format_html(f"<strong>{wishlist.name}:</strong><br>{items_details}")
        return "No wishlist"

    display_wishlist.short_description = 'Wishlist'

    def display_cart(self, obj):
        cart = obj.cart
        if cart:
            cart_details = "<br>".join(
                [f"Name: {item.prodInfo.product.name}, Color: {item.color}, Gloss: {item.gloss}, Drainage: {item.drainage}, Quantity: {item.quantity}, Price: {item.prodInfo.price}, SubTotal: {item.prodInfo.price * item.quantity}" 
                 for item in cart.items.all()]
            )
            return format_html(f"<strong>{cart.name}:</strong><br>{cart_details}")
        return "No cart FOund"

    display_cart.short_description = 'cart'

# Admin for Category model
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'image')
    search_fields = ('name',)  # Allow searching by name

# Admin for Subcategory model
@admin.register(Subcategory)
class SubcategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')
    list_filter = ('category',)
    search_fields = ('name',)  # Allow searching by name

# Admin for SelectedCategory model
@admin.register(SelectedCategory)
class SelectedCategoryAdmin(admin.ModelAdmin):
    list_display = ('category',)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Redirect to the home view after saving
        return HttpResponseRedirect(reverse('green_app:home'))

# Admin for Color model
@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ('name', 'hex_code')

# Admin for Product model
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'width',"height",'drainage', 'description',)  # Add more fields if needed

@admin.register(ProductInfo)
class ProductInfoAdmin(admin.ModelAdmin):
    list_display = (
        'product',
        'subcategory',
        'width',
        'height',
        'color',
        'gloss',
        'price',
        'inventory',
        'drainage',
        'image',
    )
    list_filter = (
        'subcategory__category',  # Filter by category through the subcategory
        'subcategory',            # Filter by subcategory directly
        'color'                   # Filter by color
    )

    def width(self, obj):
        return obj.product.width
    
    def height(self, obj):
        return obj.product.height
    
    def drainage(self, obj):
        return obj.product.drainage
    def inventory(self, obj):
        return obj.inventory
    
    def subcategory(self, obj):
        return obj.subcategory.name  # Display subcategory name
    
    subcategory.short_description = 'Subcategory'  # Set a short description for the column header

#=================NEWEST ARRIVALS====================
@admin.register(NewestArrivals)
class SelectedCategoryAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'product_image', 'product_price')
    list_filter = ('product__product__name',)  # Ensure this is a tuple with a trailing comma

    def product_name(self, obj):
        return obj.product.product.name if obj.product else 'No Product'

    def product_image(self, obj):
        return obj.product.image.url if obj.product and obj.product.image else 'No Image'

    def product_price(self, obj):
        return obj.product.price if obj.product else 'No Price'

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Redirect to the home view after saving
        return HttpResponseRedirect(reverse('green_app:home'))

#==========================WISHLIST=====================
class ItemsAdmin(admin.ModelAdmin):
    list_display = ('prodInfo', 'getname','color', 'drainage', 'gloss', 'quantity')
    list_filter = ('color', 'drainage', 'gloss')
    search_fields = ('prodInfo__product__name', 'color', 'gloss')
    ordering = ('prodInfo', 'color')
    def getname(self,obj):
        return obj.prodInfo.product.name
    
class ItemsInlineForm(admin.TabularInline):
    model = WishList.items.through
    extra = 1
    can_delete = True
    fields = ('item',)

    def item(self, obj):
        return format_html(
            "Name: {}<br>Color: {}<br>Gloss: {}<br>Drainage: {}<br>Quantity: {}",
            obj.items.prodInfo.product.name,
            obj.items.color,
            obj.items.gloss,
            obj.items.drainage,
            obj.items.quantity
        )
    item.short_description = 'Item Details'

    def has_add_permission(self, request, obj=None):
        return False  # Disable adding new items directly from this inline

class ItemsAdmin(admin.ModelAdmin):
    list_display = ('prodInfo', 'getname', 'color', 'drainage', 'gloss', 'quantity')
    list_filter = ('color', 'drainage', 'gloss')
    search_fields = ('prodInfo__product__name', 'color', 'gloss')
    ordering = ('prodInfo', 'color')

    def getname(self, obj):
        return obj.prodInfo.product.name
    getname.short_description = 'Product Name'

class WishListAdmin(admin.ModelAdmin):
    list_display = ('name', 'display_items', 'total_price')
    inlines = [ItemsInlineForm]

    def display_items(self, obj):
        return format_html("<br>".join(
            [
                f"Name: {item.prodInfo.product.name}, Color: {item.color}, "
                f"Gloss: {item.gloss}, Drainage: {item.drainage}, "
                f"Quantity: {item.quantity}, Price: {item.prodInfo.price}"
                for item in obj.items.all()
            ]
        ))
    display_items.short_description = 'Items'

    def total_price(self, obj):
        total = sum(item.prodInfo.price * item.quantity for item in obj.items.all())
        return f"${total:.2f}"
    total_price.short_description = 'Total Price'

admin.site.register(Items, ItemsAdmin)
admin.site.register(WishList, WishListAdmin)
#==================CART===========================
# Inline for Cart items
class CartItemsInline(admin.TabularInline):
    model = Cart.items.through
    extra = 1

class CartAdmin(admin.ModelAdmin):
    list_display = ('name', 'display_items')
    inlines = [CartItemsInline]

    def display_items(self, obj):
        return format_html("<br>".join(
            [f"Name: {item.prodInfo.product.name},   Color: {item.color},   Gloss: {item.gloss},   Drainage: {item.drainage}   , Quantity: {item.quantity}   ,Price: {item.prodInfo.price}   ,SubTotal: {item.prodInfo.price}" 
                for item in obj.items.all()]
        ))
    display_items.short_description = 'Items'

admin.site.register(Cart, CartAdmin)

#===========================ORDER DETAILS ===================

class OrderDetailsAdmin(admin.ModelAdmin):
    list_display = (
        'placedAt',
        'status',
        'grandTotal',
        'paymentMethod',
        'paymentStatus',
        'paymentProof',
        'gift',
        'get_profile_full_name',
        'get_profile_user_email',
        'get_profile_address',
        'get_profile_contact',
        'get_cart_info',
    )
    search_fields = (
        'status',
        'paymentMethod',
        'paymentStatus',
        'profile__full_name',
        'profile__user__email',
        'profile__contact',
    )
    list_filter = ('status', 'paymentMethod','paymentStatus',)

    @admin.display(description='Profile Name')
    def get_profile_full_name(self, obj):
        return obj.profile.full_name if obj.profile else 'No Profile'

    @admin.display(description='User Email')
    def get_profile_user_email(self, obj):
        return obj.profile.user.email if obj.profile and obj.profile.user else 'No Email'

    @admin.display(description='Profile Address')
    def get_profile_address(self, obj):
        return obj.profile.address if obj.profile else 'No Address'

    @admin.display(description='Contact')
    def get_profile_contact(self, obj):
        return obj.profile.contact if obj.profile else 'No Contact'

    @admin.display(description='Cart Info')
    def get_cart_info(self, obj):
        if obj.profile and obj.orderItems:
            items = obj.orderItems.items.all()
            # Format each item in the cart on a new line
            cart_items = format_html_join(
                '\n', 
                '<div style="white-space: nowrap;">{}</div>',
                ((str(item),) for item in items)
            )
            return format_html('<div style="overflow-x: auto; max-width: 200px;">{}</div>', cart_items)
        return 'No Cart'

admin.site.register(orderDetails, OrderDetailsAdmin)


from django.contrib.admin.models import LogEntry
from django.contrib import admin
class LogEntryAdmin(admin.ModelAdmin):
    list_display = ('action_time', 'user', 'content_type', 'object_repr', 'action_flag', 'change_message')
    list_filter = ('action_flag', 'content_type')
    search_fields = ('user__username', 'object_repr', 'change_message')

admin.site.register(LogEntry, LogEntryAdmin)

admin.site.register(Reviews)
admin.site.register(Subscription)

#for heading back to the homepage 
admin.site.site_header = format_html(
    '<a href="{}">Shop Green </a>',
    reverse('green_app:home')  # Replace 'green_app:home' with your correct URL name
)

