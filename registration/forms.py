# forms.py
from django import forms
from .models import Registration
from .models import Contact


class RegistrationForm(forms.ModelForm):
    class Meta:
        model = Registration
        fields = ['user', 'event']  # You can add more fields as needed
        widgets = {
            'user': forms.HiddenInput(),  # Auto-fill current user
            'event': forms.HiddenInput(),  # Auto-fill event being registered
        }
        
class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, required=True, label="Name")
    email = forms.EmailField(required=True, label="Email")
    message = forms.CharField(widget=forms.Textarea, required=True, label="Message")
    mobile_number = forms.CharField(max_length=15, required=True, label="Mobile Number")  # Add this line