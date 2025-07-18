# myapp/auth/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.urls import reverse_lazy
from django.template.loader import render_to_string # Import render_to_string
from django.utils.html import strip_tags # For plain text version of email

from .forms import CustomUserCreationForm, CustomAuthenticationForm, PasswordResetRequestForm, PasswordResetConfirmForm
from myapp.models import Item, CustomUser
import uuid
from django.core.mail import send_mail # For actual email sending
from django.conf import settings

# Temporary storage for reset codes (In a real app, use a database or cache!)
# This is NOT secure for production, purely for demonstration.
password_reset_codes = {}

@require_http_methods(["GET", "POST"])
def register_view(request):
    """
    Handles user registration (signup).
    Displays the registration form (GET) or processes form submission (POST).
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Account created for {user.email} and you are logged in!")
            return redirect('item_list_create')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")
            if not form.errors and not form.non_field_errors():
                messages.error(request, "Please correct the errors below.")
    else:
        form = CustomUserCreationForm()
    return render(request, 'auth/register.html', {'form': form}) # Template path: auth/register.html

@require_http_methods(["GET", "POST"])
def login_view(request):
    """
    Handles user login.
    Displays the login form (GET) or processes form submission (POST).
    """
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('item_list_create')
        else:
            messages.error(request, "Invalid email or password.")
    else:
        form = CustomAuthenticationForm()
    return render(request, 'auth/login.html', {'form': form}) # Template path: auth/login.html

@login_required
@require_http_methods(["POST", "GET"])
def logout_view(request):
    """
    Handles user logout.
    Logs out the user and redirects.
    """
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')

# --- Password Reset Views ---

def _send_password_reset_email(request, user, reset_code):
    """Helper function to send the password reset email."""
    reset_link = request.build_absolute_uri(
        reverse_lazy('password_reset_confirm') + f'?email={user.email}'
    )
    resend_link = request.build_absolute_uri(
        reverse_lazy('password_reset_resend') + f'?email={user.email}'
    )

    html_message = render_to_string(
        'emails/password_reset_email.html',
        {
            'user': user,
            'reset_code': reset_code,
            'reset_link': reset_link,
            'resend_link': resend_link, # Pass resend link to template
            'domain': request.get_host(),
        }
    )
    plain_message = strip_tags(html_message)

    try:
        send_mail(
            'Your Password Reset Code',
            plain_message, # Plain text content
            settings.DEFAULT_FROM_EMAIL, # Sender email from settings
            [user.email], # Recipient email
            html_message=html_message, # HTML content
            fail_silently=False, # Raise exception if email fails
        )
        return True
    except Exception as e:
        print(f"ERROR SENDING EMAIL: {e}")
        return False


@require_http_methods(["GET", "POST"])
def forgot_password_request_view(request):
    """
    Allows a user to request a password reset by entering their email.
    A verification code is sent to the email.
    """
    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = CustomUser.objects.get(email=email)

            reset_code = str(uuid.uuid4())[:6].upper()
            password_reset_codes[email] = reset_code

            if _send_password_reset_email(request, user, reset_code):
                messages.success(request, "A verification code has been sent to your email address.")
            else:
                messages.error(request, "Failed to send verification email. Please try again later.")
            
            return redirect(reverse_lazy('password_reset_confirm') + f'?email={email}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")
            if not form.errors and not form.non_field_errors():
                messages.error(request, "Please correct the errors below.")
    else:
        form = PasswordResetRequestForm()
    return render(request, 'auth/forgot_password_request.html', {'form': form})


@require_http_methods(["GET", "POST"])
def forgot_password_confirm_view(request):
    """
    Allows a user to enter the verification code and set a new password.
    """
    email = request.GET.get('email') # Get email from query parameter
    user = None
    if email:
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            messages.error(request, "Invalid email provided for password reset.")
            return redirect('password_reset_request') # Redirect back if email is invalid

    if not user:
        messages.error(request, "Please request a password reset first.")
        return redirect('password_reset_request')

    if request.method == 'POST':
        form = PasswordResetConfirmForm(user, request.POST)
        if form.is_valid():
            entered_code = form.cleaned_data['code']
            stored_code = password_reset_codes.get(email)

            if stored_code and entered_code == stored_code:
                form.save()
                
                if email in password_reset_codes:
                    del password_reset_codes[email]

                messages.success(request, "Your password has been successfully reset! You can now log in.")
                return redirect('login')
            else:
                messages.error(request, "Invalid or expired verification code.")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")
            if not form.errors and not form.non_field_errors():
                messages.error(request, "Please correct the errors below.")
    else:
        form = PasswordResetConfirmForm(user) # Pass the user instance to the form
    
    # Pass resend link to the template
    resend_link = reverse_lazy('password_reset_resend') + f'?email={email}'
    return render(request, 'auth/forgot_password_confirm.html', {'form': form, 'email': email, 'resend_link': resend_link})


@require_http_methods(["GET"]) # Only GET requests for resending
def resend_password_reset_code_view(request):
    """
    Handles resending the password reset code to the user's email.
    """
    email = request.GET.get('email')
    if not email:
        messages.error(request, "Email address is missing for resend request.")
        return redirect('password_reset_request')

    try:
        user = CustomUser.objects.get(email=email)
    except CustomUser.DoesNotExist:
        messages.error(request, "No user found with that email address.")
        return redirect('password_reset_request')

    # Generate a new code and send email
    new_reset_code = str(uuid.uuid4())[:6].upper()
    password_reset_codes[email] = new_reset_code # Update the code

    if _send_password_reset_email(request, user, new_reset_code):
        messages.success(request, "A new verification code has been sent to your email address.")
    else:
        messages.error(request, "Failed to resend verification email. Please try again later.")
    
    return redirect(reverse_lazy('password_reset_confirm') + f'?email={email}')


# --- Existing To-Do List Views (from myapp/views.py) ---
@login_required
@require_http_methods(["GET", "POST"])
def item_list_create(request):
    """
    Handles listing all items (GET) and creating a new item (POST).
    Items are filtered by the logged-in user.
    """
    if request.method == 'POST':
        item_name = request.POST.get('name')
        if item_name:
            item_name = item_name.strip()
            if Item.objects.filter(user=request.user, name=item_name).exists():
                messages.error(request, f'Task "{item_name}" already exists for your account.')
                return redirect('item_list_create')
            Item.objects.create(user=request.user, name=item_name)
            messages.success(request, 'Task created successfully!')
        else:
            messages.error(request, 'Task name cannot be empty.')
        return redirect('item_list_create')

    items = Item.objects.filter(user=request.user).all()
    return render(request, 'index.html', {'items': items})

@login_required
@require_http_methods(["GET", "POST"])
def item_update(request, pk):
    """
    Handles displaying the update form (GET) and updating an existing item (POST).
    Ensures the user can only update their own items.
    """
    item = get_object_or_404(Item, pk=pk, user=request.user)

    if request.method == 'POST':
        new_name = request.POST.get('name')
        if new_name:
            item.name = new_name
            item.save()
            messages.success(request, f'Task "{item.name}" updated successfully!')
            return redirect('item_list_create')
        else:
            messages.error(request, 'Task name cannot be empty.')

    return render(request, 'item_update.html', {'item': item})

@login_required
@require_http_methods(["GET", "POST"])
def item_delete(request, pk):
    """
    Handles displaying the delete confirmation (GET) and actually deleting an item (POST).
    Ensures the user can only delete their own items.
    """
    item = get_object_or_404(Item, pk=pk, user=request.user)

    if request.method == 'POST':
        item_name = item.name
        item.delete()
        messages.success(request, f'Task "{item_name}" deleted permanently.')
        return redirect('item_list_create')

    return render(request, 'item_confirm_delete.html', {'item': item})

@login_required
@require_http_methods(["POST"])
def item_toggle_complete(request, pk):
    """
    Toggles the 'completed' status of an item.
    Ensures the user can only toggle their own items.
    """
    item = get_object_or_404(Item, pk=pk, user=request.user)
    item.completed = not item.completed
    item.save()
    if item.completed:
        messages.success(request, f'Task "{item.name}" marked as completed!')
    else:
        messages.info(request, f'Task "{item.name}" marked as incomplete.')
    return redirect('item_list_create')

@require_http_methods(["GET"])
def terms_of_service_view(request):
    """
    Renders the Terms of Service page.
    """
    return render(request, 'terms_of_service.html')

@require_http_methods(["GET"])
def privacy_policy_view(request):
    """
    Renders the Privacy Policy page.
    """
    return render(request, 'privacy_policy.html')
