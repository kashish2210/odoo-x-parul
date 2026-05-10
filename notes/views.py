from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse

from trips.models import Trip
from .models import Note
from .forms import NoteForm


@login_required
def notes_list(request):
    """Main notes list: search, trip filter, group-by filter."""
    trips = Trip.objects.filter(user=request.user)

    # Trip filter from query string
    trip_id = request.GET.get('trip', '').strip()
    if trip_id:
        notes = Note.objects.filter(user=request.user, trip_id=trip_id)
    else:
        notes = Note.objects.filter(user=request.user)

    # Text search
    query = request.GET.get('q', '').strip()
    if query:
        from django.db.models import Q
        notes = notes.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        )

    # Group-by tab (client-side filtering; persisted in URL for page refresh)
    group_by = request.GET.get('group', 'all')

    # Blank add-note form for the modal
    form = NoteForm(user=request.user)

    return render(request, 'notes/list.html', {
        'notes': notes,
        'trips': trips,
        'trip_id': trip_id,
        'query': query,
        'group_by': group_by,
        'form': form,
    })


@login_required
def note_create(request):
    """Handle POST to create a new note (submitted from modal form)."""
    if request.method == 'POST':
        form = NoteForm(request.user, request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.user = request.user
            note.save()
            messages.success(request, 'Note added successfully.')
            return redirect(reverse('notes:notes_list') + f'?trip={note.trip.pk}')
        else:
            messages.error(request, 'Could not save note. Please check the fields.')
    return redirect(reverse('notes:notes_list'))


@login_required
def note_edit(request, pk):
    """Full-page edit form for a note."""
    note = get_object_or_404(Note, pk=pk, user=request.user)

    if request.method == 'POST':
        form = NoteForm(request.user, request.POST, instance=note)
        if form.is_valid():
            form.save()
            messages.success(request, 'Note updated.')
            return redirect(reverse('notes:notes_list') + f'?trip={note.trip.pk}')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = NoteForm(user=request.user, instance=note)

    return render(request, 'notes/form.html', {
        'form': form,
        'note': note,
    })


@login_required
def note_delete(request, pk):
    """Delete confirmation page + POST handler."""
    note = get_object_or_404(Note, pk=pk, user=request.user)
    trip_id = note.trip.pk

    if request.method == 'POST':
        note.delete()
        messages.success(request, 'Note deleted.')
        return redirect(reverse('notes:notes_list') + f'?trip={trip_id}')

    return render(request, 'notes/confirm_delete.html', {'note': note})
