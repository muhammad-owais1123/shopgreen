
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from green_app.models import Profile,Reviews,orderDetails

class update(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['email', 'address', 'contact']
        widgets = {
            'address': forms.TextInput(attrs={'placeholder': 'Enter your address'}),
            'contact': forms.TextInput(attrs={'placeholder': 'Enter contact number'})
        }

    def __init__(self, *args, **kwargs):
        # Set the initial value for address if provided
        initial_address = kwargs.get('instance').address if 'instance' in kwargs else ''
        super().__init__(*args, **kwargs)
        self.fields['address'].initial = initial_address
class SignUpForm(UserCreationForm):
    full_name = forms.CharField(required=True, max_length=30)
    email = forms.EmailField(required=False)
    address = forms.CharField(max_length=30, required=True)
    contact = forms.CharField(help_text="03XXXXXXXXX", required=True,max_length=11)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1','password2', 'full_name', 'address', 'contact']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.full_name = self.cleaned_data['full_name']
        if commit:
            user.save()
            profile = Profile.objects.create(
                user=user,
                full_name=self.cleaned_data['full_name'],
                address=self.cleaned_data['address'],
                contact=self.cleaned_data['contact'],
                email=self.cleaned_data['email'],
            )
            profile.save()
        return user

class LoginForm(AuthenticationForm):
    pass


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Reviews
        fields = ['ratings', 'description', 'image']  # Include the image field

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ratings'].widget = forms.RadioSelect(choices=[(i, f"{i} star{'s' if i > 1 else ''}") for i in range(1, 6)])
        self.fields['description'].widget = forms.Textarea(attrs={'placeholder': 'Enter your review here...', 'rows': 4})
        self.fields['image'].widget =forms.FileInput()
        self.fields['image'].required = False 
        self.fields['description'].required = False 


class SearchForm(forms.Form):
    term = forms.CharField(max_length=100, required=False)


class OrderForm(forms.ModelForm):
    class Meta:
        model = orderDetails
        fields = ['grandTotal', 'paymentProof', 'paymentMethod']
        widgets = {
            'paymentMethod': forms.RadioSelect(choices=[('online','Online'),('COD','cod')]),
        }
#PAYMENT
class PaymentForm(forms.Form):
    amount = forms.DecimalField(max_digits=10, decimal_places=2)
    phone_number = forms.CharField(max_length=15)
    email = forms.EmailField()