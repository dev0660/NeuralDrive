from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Dealership
from django.middleware.csrf import get_token

def form_signin(request):
    print("🔑 Expected token:", get_token(request))
    print("📦 POST token:", request.POST.get("csrfmiddlewaretoken"))
    print("🍪 Cookies:", request.COOKIES)

class InputSignIn(forms.Form):
    username = forms.CharField(max_length=30)
    password = forms.CharField(max_length=30, widget=forms.PasswordInput)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400'
            })

class LogSignUpForm(UserCreationForm):
    dealership = forms.ModelChoiceField(
        queryset=Dealership.objects.all(),
        empty_label="Select a Dealership",
        required=True
    )
    
    class Meta:
        model = CustomUser
        fields = ['username', 'password1', 'password2', 'phone_number', 'dealership']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400'
            })
