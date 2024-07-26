from django import forms
from django.core.validators import EmailValidator


from .models import ContactMessage


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ["name", "email", "phone", "address", "subject", "message"]
