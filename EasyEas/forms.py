from django import forms
from EasyEas import models

class UploadBuildForm(forms.Form):


    note = forms.CharField(max_length=255)
    version = forms.CharField(max_length=50)
    file = forms.FileField()
    product = forms.ModelChoiceField(models.Product.objects.all())