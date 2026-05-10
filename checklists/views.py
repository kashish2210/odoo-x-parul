from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import PackingItem
from trips.models import Trip

@login_required
def checklist_view(request):
    trips = Trip.objects.filter(user=request.user)
    
    trip_id = request.GET.get('trip')
    selected_trip = None
    items = []
    
    if trip_id:
        selected_trip = get_object_or_404(Trip, pk=trip_id, user=request.user)
    elif trips.exists():
        selected_trip = trips.first()
        trip_id = str(selected_trip.pk)
        
    if selected_trip:
        items = PackingItem.objects.filter(trip=selected_trip)
    else:
        items = PackingItem.objects.none()
        
    # Calculate progress
    total_items = items.count()
    packed_items = items.filter(is_packed=True).count()
    progress_percent = (packed_items / total_items * 100) if total_items > 0 else 0
    
    # Group items by category
    grouped_items = {}
    for category_code, category_label in PackingItem.CATEGORY_CHOICES:
        category_items = items.filter(category=category_code)
        if category_items.exists():
            packed_in_cat = category_items.filter(is_packed=True).count()
            total_in_cat = category_items.count()
            grouped_items[category_label] = {
                'items': category_items,
                'packed': packed_in_cat,
                'total': total_in_cat,
                'code': category_code
            }
            
    context = {
        'trips': trips,
        'selected_trip': selected_trip,
        'trip_id': trip_id,
        'grouped_items': grouped_items,
        'total_items': total_items,
        'packed_items': packed_items,
        'progress_percent': progress_percent,
        'categories': PackingItem.CATEGORY_CHOICES,
    }
    return render(request, 'checklists/checklist.html', context)

@login_required
def add_item(request):
    if request.method == 'POST':
        trip_id = request.POST.get('trip_id')
        name = request.POST.get('name')
        category = request.POST.get('category', PackingItem.CATEGORY_OTHER)
        
        if trip_id and name:
            trip = get_object_or_404(Trip, pk=trip_id, user=request.user)
            PackingItem.objects.create(
                trip=trip,
                name=name,
                category=category
            )
        
        return redirect(f"/checklists/?trip={trip_id}" if trip_id else 'checklists:checklist')
    return redirect('checklists:checklist')

@login_required
def toggle_item(request, item_id):
    if request.method == 'POST':
        item = get_object_or_404(PackingItem, pk=item_id, trip__user=request.user)
        item.is_packed = not item.is_packed
        item.save()
        
        # Calculate updated progress
        total_items = PackingItem.objects.filter(trip=item.trip).count()
        packed_items = PackingItem.objects.filter(trip=item.trip, is_packed=True).count()
        
        category_items = PackingItem.objects.filter(trip=item.trip, category=item.category)
        cat_total = category_items.count()
        cat_packed = category_items.filter(is_packed=True).count()
        
        return JsonResponse({
            'status': 'success', 
            'is_packed': item.is_packed,
            'total_items': total_items,
            'packed_items': packed_items,
            'cat_total': cat_total,
            'cat_packed': cat_packed,
            'category': item.category
        })
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def reset_checklist(request):
    if request.method == 'POST':
        trip_id = request.POST.get('trip_id')
        if trip_id:
            trip = get_object_or_404(Trip, pk=trip_id, user=request.user)
            PackingItem.objects.filter(trip=trip).update(is_packed=False)
            return redirect(f"/checklists/?trip={trip_id}")
    return redirect('checklists:checklist')

@login_required
def delete_item(request, item_id):
    if request.method == 'POST':
        item = get_object_or_404(PackingItem, pk=item_id, trip__user=request.user)
        trip_id = item.trip.pk
        item.delete()
        return redirect(f"/checklists/?trip={trip_id}")
    return redirect('checklists:checklist')
