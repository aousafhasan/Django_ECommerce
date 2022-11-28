from django import forms
from myapp.models import Order, Client, Product
from django.contrib.auth.forms import UserCreationForm


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order   #models we want to represent
        fields = ['client', 'product', 'num_units']      #fields we want to output

    client = forms.ModelChoiceField(widget=forms.RadioSelect, queryset=Client.objects.all(), to_field_name="username", label='Client name')
    product = forms.ModelChoiceField(queryset=Product.objects.all().order_by('id'), to_field_name="name")
    num_units = forms.IntegerField(label='Quantity')


class InterestForm(forms.Form):
    INT_CHOICES = [('Yes', 'Yes'), ('No', 'No')]
    interested = forms.ChoiceField(widget=forms.RadioSelect, choices=INT_CHOICES)
    quantity = forms.IntegerField(initial=1)
    comments = forms.CharField(widget=forms.Textarea, label='Additional Comments', required=False)

class RegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=100, required=True,)
    last_name = forms.CharField(max_length=100, required=True)
    username = forms.CharField(max_length=100, required=True)
    password = forms.CharField(max_length=50, required=True, widget=forms.PasswordInput())
    # confirm_password = forms.CharField(max_length=50, required=True, widget=forms.PasswordInput())
    email = forms.EmailField(required=True)

    class Meta:
        model = Client
        fields = ("username", "first_name", "last_name", "email", "password1", "password2")


class ForgotPasswordForm(forms.Form):
    Email = forms.EmailField()

    def __str__(self):
        return self.Email