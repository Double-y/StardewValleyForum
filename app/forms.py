from dataclasses import field
from django.forms import ModelForm
from .models import Room,User
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django import forms

class MyUserCreationForm(UserCreationForm):
    class Meta:
        model=User
        fields=['name','username','email','password1','password2']

    name=forms.CharField(label='姓名',max_length=50, required=True)
    username=forms.CharField(label='用户名',max_length=50, required=True)
    email=forms.EmailField(label='邮箱',max_length=50, required=True)
    password1=forms.CharField(label='密码',widget=forms.PasswordInput, required=True)
    password2=forms.CharField(label='确认密码',widget=forms.PasswordInput, required=True)

class RoomForm(ModelForm):
    class Meta:
        model=Room
        fields='__all__'
        exclude=['host','participants']
        
class UserForm(ModelForm):
    class Meta:
        model=User
        fields=['avatar','name','username', 'email','bio']

    avatar=forms.ImageField(label='头像',required=False)
    name=forms.CharField(label='姓名',max_length=50, required=True)
    username=forms.CharField(label='用户名',max_length=50, required=True)
    email=forms.EmailField(label='邮箱',max_length=50, required=True)
    bio=forms.CharField(label='个人简介',widget=forms.Textarea, required=False)


# 新增的密码更改表单
class MyPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(label='旧密码', widget=forms.PasswordInput, required=True)
    new_password1 = forms.CharField(label='新密码', widget=forms.PasswordInput, required=True)
    new_password2 = forms.CharField(label='确认新密码', widget=forms.PasswordInput, required=True)

    class Meta:
        model = User
        fields = ['old_password', 'new_password1', 'new_password2']

    def clean_new_password2(self):
        new_password1 = self.cleaned_data.get('new_password1')
        new_password2 = self.cleaned_data.get('new_password2')
        if new_password1 and new_password2 and new_password1 != new_password2:
            raise forms.ValidationError('新密码和确认密码不匹配')
        return new_password2
    

class PasswordResetForm(forms.Form):
    new_password1 = forms.CharField(label='新密码', widget=forms.PasswordInput, required=True)
    new_password2 = forms.CharField(label='确认新密码', widget=forms.PasswordInput, required=True)

    def clean_new_password2(self):
        new_password1 = self.cleaned_data.get('new_password1')
        new_password2 = self.cleaned_data.get('new_password2')
        if new_password1 and new_password2 and new_password1 != new_password2:
            raise forms.ValidationError('新密码和确认密码不匹配')
        return new_password2