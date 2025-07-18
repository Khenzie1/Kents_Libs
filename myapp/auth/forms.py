# myapp/auth/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, SetPasswordForm
from django.contrib.auth import get_user_model, authenticate
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

CustomUser = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    """
    A custom form for user registration, using email as the primary identifier.
    """
    email = forms.EmailField(
        required=True,
        help_text='Required. Enter a valid email address.',
        widget=forms.EmailInput(attrs={'placeholder': 'your@email.com', 'class': 'auth-input', 'id': 'id_email'})
    )
    username = forms.CharField(
        label="Full Name",
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Full Name', 'class': 'auth-input', 'id': 'id_username'})
    )

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('email', 'username')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Customize password1 field (first password)
        self.fields['password1'].widget = forms.PasswordInput(attrs={
            'class': 'auth-input',
            'placeholder': 'Create a password',
            'id': 'id_password1'
        })
        
        # Customize password2 field (confirm password)
        self.fields['password2'].widget = forms.PasswordInput(attrs={
            'class': 'auth-input',
            'placeholder': 'Confirm your password',
            'id': 'id_password2'
        })
        
        # Ensure other fields also have their classes and IDs set
        self.fields['email'].widget.attrs.update({'class': 'auth-input', 'id': 'id_email'})
        self.fields['username'].widget.attrs.update({'class': 'auth-input', 'id': 'id_username'})


class CustomAuthenticationForm(AuthenticationForm):
    """
    A custom form for user login, using email instead of username.
    """
    username = forms.EmailField(
        label="Email Address",
        max_length=254,
        widget=forms.EmailInput(attrs={'placeholder': 'your@email.com', 'class': 'auth-input', 'id': 'id_username_login'})
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter your password', 'class': 'auth-input', 'id': 'id_password_login'})
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'password']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ensure unique IDs for login fields and placeholders
        if 'username' in self.fields:
            self.fields['username'].widget.attrs.update({'class': 'auth-input', 'id': 'id_username_login', 'placeholder': 'your@email.com'})
        if 'password' in self.fields:
            self.fields['password'].widget.attrs.update({'class': 'auth-input', 'id': 'id_password_login', 'placeholder': 'Enter your password'})

    def clean(self):
        email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        if email and password:
            self.request = getattr(self, 'request', None)
            self.user_cache = authenticate(self.request, email=email, password=password)
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                    params={'username': self.username_field.verbose_name},
                )
        return self.cleaned_data


class PasswordResetRequestForm(forms.Form):
    """
    Form for users to request a password reset by providing their email.
    """
    email = forms.EmailField(
        label="Email Address",
        max_length=254,
        widget=forms.EmailInput(attrs={
            'placeholder': 'Enter your email',
            'class': 'auth-input',
            'id': 'id_reset_email'
        })
    )

    def clean_email(self):
        email = self.cleaned_data['email']
        # Check if a user with this email exists
        if not CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError(
                _("No user is associated with this email address."),
                code='user_not_found'
            )
        return email


class PasswordResetConfirmForm(SetPasswordForm):
    """
    Form for users to confirm password reset with a code and set a new password.
    Extends Django's built-in SetPasswordForm.
    """
    # Adding a field for the verification code
    code = forms.CharField(
        label="Verification Code",
        max_length=6,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter the 6-digit code',
            'class': 'auth-input',
            'id': 'id_reset_code'
        }),
        help_text=_("Enter the code sent to your email address.")
    )

    # Overriding password fields to apply custom styling and placeholders
    new_password1 = forms.CharField(
        label=_("New password"),
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Enter new password',
            'class': 'auth-input',
            'id': 'id_new_password1'
        }),
    )
    new_password2 = forms.CharField(
        label=_("New password confirmation"),
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirm new password',
            'class': 'auth-input',
            'id': 'id_new_password2'
        }),
    )

    def __init__(self, user, *args, **kwargs):
        super().__init__(user, *args, **kwargs)
        # Apply classes to all fields
        for field_name in self.fields:
            if field_name not in ['new_password1', 'new_password2', 'code']:
                self.fields[field_name].widget.attrs.update({'class': 'auth-input'})