# myapp/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.contrib.auth.decorators import login_required # Import login_required
from .models import Item

@login_required # Ensure only logged-in users can access this view
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
            # Ensure uniqueness per user
            if Item.objects.filter(user=request.user, name=item_name).exists(): # Filter by user
                messages.error(request, f'Task "{item_name}" already exists for your account.')
                return redirect('item_list_create')
            # Pass the currently logged-in user when creating the item
            Item.objects.create(user=request.user, name=item_name) # ADDED user=request.user
            messages.success(request, 'Task created successfully!')
        else:
            messages.error(request, 'Task name cannot be empty.')
        return redirect('item_list_create')

    # GET request: Display all items for the current user
    items = Item.objects.filter(user=request.user).all() # Filter by user
    return render(request, 'index.html', {'items': items})

@login_required # Ensure only logged-in users can access this view
@require_http_methods(["GET", "POST"])
def item_update(request, pk):
    """
    Handles displaying the update form (GET) and updating an existing item (POST).
    Ensures the user can only update their own items.
    """
    item = get_object_or_404(Item, pk=pk, user=request.user) # Ensure item belongs to the user

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

@login_required # Ensure only logged-in users can access this view
@require_http_methods(["GET", "POST"])
def item_delete(request, pk):
    """
    Handles displaying the delete confirmation (GET) and actually deleting an item (POST).
    Ensures the user can only delete their own items.
    """
    item = get_object_or_404(Item, pk=pk, user=request.user) # Ensure item belongs to the user

    if request.method == 'POST':
        item_name = item.name
        item.delete()
        messages.success(request, f'Task "{item_name}" deleted permanently.')
        return redirect('item_list_create')

    return render(request, 'item_confirm_delete.html', {'item': item})

@login_required # Ensure only logged-in users can access this view
@require_http_methods(["POST"])
def item_toggle_complete(request, pk):
    """
    Toggles the 'completed' status of an item.
    Ensures the user can only toggle their own items.
    """
    item = get_object_or_404(Item, pk=pk, user=request.user) # Ensure item belongs to the user
    item.completed = not item.completed
    item.save()
    if item.completed:
        messages.success(request, f'Task "{item.name}" marked as completed!')
    else:
        messages.info(request, f'Task "{item.name}" marked as incomplete.')
    return redirect('item_list_create')
