from django import forms


class demoForm(forms.Form):
    text=forms.CharField(label="", max_length=200)
