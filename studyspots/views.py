from enum import IntEnum
from json import JSONDecodeError

from django.db import transaction
from django.shortcuts import redirect, get_object_or_404
from django.http import *
from django.contrib.auth.decorators import login_required
from django.conf import settings
import json
import geopy.distance

from .forms import *

from django.urls import reverse

from studyspots.models import *
from .settings import STARTING_POS


def is_ajax(request):
    return 'HTTP_X_REQUESTED_WITH' in request.META and request.META['HTTP_X_REQUESTED_WITH'] == "XMLHttpRequest"


def get_studyspace_by_ordinal(location_id, location_ordinal):
    obj = StudySpace.objects.filter(location_id=location_id, location_ordinal=location_ordinal)
    if obj:
        return obj.get()
    else:
        return None


def get_variable(request, name):
    return request.GET.get(name, None)


@login_required
def profile(request):
    return redirect(reverse('studyspots:map'), False)


def confirmation(request):
    return render(request, 'studyspots/confirmation.html')


def map(request):
    starting_location_id = request.GET.get('location', "null")
    key = settings.GOOGLE_API_KEY
    location_objs_dict = {}
    objs_first = True
    location_objs = Location.objects.all().distinct().order_by("name")
    for location in location_objs:
        location_dict = LocationSerializer(location).data
        studyspace_objs = {}
        for studyspace in location.studyspace_set.all().order_by("name"):
            studyspace_objs.update({studyspace.name: StudySpaceSerializer(studyspace).data})
        location_dict.update({"set": studyspace_objs})
        location_objs_dict.update({location.location_id: location_dict})
    print(location_objs_dict)
    locations = LocationSerializer(Location.objects.all(), many=True).data
    locations_json = json.dumps(locations)
    context = {
        'key': key, 'locations': locations_json, 'starting_location_id': starting_location_id,
        'location_objs': location_objs_dict.values(), 'latlng': json.dumps(STARTING_POS)
    }
    return render(request, 'studyspots/map.html', context)


def map_redirect(request):
    location_id = get_variable(request, 'location')
    if location_id:
        return redirect(reverse("studyspots:map") + "?location=" + location_id, permanent=True)
    return redirect(reverse("studyspots:map"), permanent=True)


@login_required()
def add(request):
    locations = LocationSerializer(Location.objects.all(), many=True).data
    new_location_label = "-- Add new location --"
    locations_json = json.dumps(locations)
    key = settings.GOOGLE_API_KEY
    error_message = None
    if request.method == 'POST':
        location_id = None
        selected_location_form = LocationSelection(request.POST, prefix="selector")
        new_location_form = NewLocationForm(request.POST, prefix="new_location")
        new_studyspace_form = NewStudySpaceForm(request.POST, prefix="new_studyspace")
        if selected_location_form.is_valid():
            location_id = int(selected_location_form.cleaned_data['selected_location'])
        else:
            error_message = "Select a location"
        pending_location = None
        if error_message is None:
            if location_id == -1:
                if new_location_form.is_valid():
                    # Get the coordinates from the form
                    lat = new_location_form.cleaned_data['lat']
                    lng = new_location_form.cleaned_data['lng']
                    # Check if the location is within a 10-mile radius of the University of Virginia
                    location_point = (lat, lng)
                    uva_point = (STARTING_POS['lat'], STARTING_POS['lng'])
                    distance = geopy.distance.distance(uva_point, location_point).miles

                    if distance <= 10:
                        # Location is within the 10-mile radius, proceed to save
                        pending_location = PendingLocation(
                            name=new_location_form.cleaned_data['locationName'],
                            location_type=new_location_form.cleaned_data['location_type'],
                            on_grounds=new_location_form.cleaned_data['on_grounds'],
                            lat=lat,
                            lng=lng
                        )
                    else:
                        # Location is outside the 10-mile radius
                        error_message = "Location must be closer to the University of Virginia."
                else:
                    error_message = "Invalid form data: you must move the pin from its original position"
            else:
                pending_location = Location.objects.get(pk=location_id)
        if error_message is None:
            if new_studyspace_form.is_valid():
                pending_space = PendingStudySpace(
                    name=new_studyspace_form.cleaned_data['studySpaceName'],
                    capacity=new_studyspace_form.cleaned_data['capacity'],
                    comments=[new_studyspace_form.cleaned_data['comment']],
                    overall_ratings=[int(new_studyspace_form.cleaned_data['overall_rating'])],
                    comfort_ratings=[int(new_studyspace_form.cleaned_data['comfort_rating'])],
                    noise_level_ratings=[int(new_studyspace_form.cleaned_data['noise_level_rating'])],
                    crowdedness_ratings=[int(new_studyspace_form.cleaned_data['crowdedness_rating'])],
                )
                if location_id != -1:
                    pending_space.content_type = ContentType.objects.get(model="location")
                    pending_space.object_id = location_id
                else:
                    pending_space.content_type = ContentType.objects.get(model="pendinglocation")
                    pending_location.save()
                    pending_space.object_id = pending_location.location_id
                pending_space.save()
                return redirect(reverse("studyspots:confirmation"))
            else:
                error_message = "Invalid Study Spot data"
            # error messages fall through to here
            context = {
                'selected_location_form': selected_location_form,
                'starting_location': location_id,
                'locations': locations_json,
                'make_new_location_label': new_location_label,
                'key': key,
                'new_studyspace_form': new_studyspace_form,
                'error_message': error_message,
            }
            return HttpResponseRedirect(reverse('studyspots:add')+'?location='+location_id, context)
        else:
            if not new_location_form:
                new_location_form = NewLocationForm(prefix="new_location")
            if not new_studyspace_form:
                new_studyspace_form = NewStudySpaceForm(prefix="new_studyspace")
            location_id = request.GET.get('location', None)
        context = {
            'selected_location_form': selected_location_form,
            'starting_location': location_id,
            'locations': locations_json,
            'make_new_location_label': new_location_label,
            'key': key,
            'new_location_form': new_location_form,
            'new_studyspace_form': new_studyspace_form,
            'latlng': json.dumps(STARTING_POS),
            'error_message': error_message,
        }
        return render(request, 'studyspots/add.html', context)
    else:
        selected_location_form = LocationSelection(prefix='selector')
        new_location_form = NewLocationForm(prefix="new_location")
        new_studyspace_form = NewStudySpaceForm(prefix="new_studyspace")
        location_id = request.GET.get('location', None)
    context = {
        'selected_location_form': selected_location_form,
        'starting_location': location_id,
        'locations': locations_json,
        'make_new_location_label': new_location_label,
        'key': key,
        'new_location_form': new_location_form,
        'new_studyspace_form': new_studyspace_form,
        'latlng': json.dumps(STARTING_POS),
        'error_message': error_message,
    }
    return render(request, 'studyspots/add.html', context)


# Add all the locations from the file to database. Do not use.
def load(request):
    if settings.DEBUG:
        json_response = {}
        json_response.update(__load_subprocess_location('locations.json', name="location"))
        json_response.update(__load_subprocess_studyspace('studyspaces.json', name="studyspace"))
        return JsonResponse(json_response, safe=True)
    else:
        return HttpResponseNotFound()


def __load_subprocess_location(filename, name="object", name_plural=None):
    if name_plural is None:
        name_plural = name + "s"
    with open(filename) as json_file:
        try:
            objects = json.load(json_file)
        except JSONDecodeError as e:
            e.msg += "Formatting error with json file"
            raise e

    added_objects = []
    for object_dict in objects:
        if Location.objects.filter(name=object_dict["name"]).count() == 0:
            obj = Location(name=object_dict['name'], location_type=object_dict['location_type'],
                           address=object_dict['address'], lat=object_dict['lat'], lng=object_dict['lng'],
                           on_grounds=object_dict['on_grounds'])
            obj.save()
            added_objects.append(object_dict['location_id'])
    if len(added_objects) == 0:
        json_response = dict({"Warning": f"No {name_plural} added. Already in database"})
    elif len(added_objects) == 1:
        json_response = dict({"Success": f"Added {name} {added_objects[0]}"})
    else:
        json_response = dict({"Success": f"Added {name_plural} {str(added_objects).replace('[', '').replace(']', '')}"})
    json_response = {f'{name.title()}': f'{json_response}'}
    return json_response


def __load_subprocess_studyspace(filename, name="object", name_plural=None):
    if name_plural is None:
        name_plural = name + "s"
    with open(filename) as json_file:
        try:
            objects = json.load(json_file)
        except JSONDecodeError as e:
            e.msg += "Formatting error with json file"
            raise e

    added_objects = []
    for object_dict in objects:
        if StudySpace.objects.all().filter(name=object_dict["name"]).count() == 0:
            a = int(object_dict['location_id_id'])
            location = Location.objects.all().get(location_id__exact=a)
            if not location:
                return ""
            obj = StudySpace(name=object_dict['name'],
                             location_id=location,
                             space_type=object_dict['space_type'], capacity=object_dict['capacity'],
                             link=object_dict['link'], reservable=object_dict['reservable'],
                             comments=object_dict['comments'], overall_ratings=object_dict['overall_ratings'],
                             comfort_ratings=object_dict['comfort_ratings'],
                             crowdedness_ratings=object_dict['crowdedness_ratings'],
                             noise_level_ratings=object_dict['noise_level_ratings'],
                             )
            obj.save()
            added_objects.append(object_dict['studyspace_id'])
    if len(added_objects) == 0:
        json_response = dict({"Warning": f"No {name_plural} added. Already in database"})
    elif len(added_objects) == 1:
        json_response = dict({"Success": f"Added {name} {added_objects[0]}"})
    else:
        json_response = dict({"Success": f"Added {name_plural} {str(added_objects).replace('[', '').replace(']', '')}"})
    json_response = {f'{name.title()}': f'{json_response}'}
    return json_response


def get_spot(request):
    location_id = get_variable(request, 'location')
    location_ordinal = get_variable(request, 'space')
    if location_id:
        if location_ordinal:
            studyspace_obj = get_studyspace_by_ordinal(location_id, location_ordinal)
            if not studyspace_obj:
                raise Http404()
            if is_ajax(request):
                studyspace_data = StudySpaceSerializer(studyspace_obj, many=False).data
                return JsonResponse(studyspace_data, safe=False)
            else:
                # used to render information about a study spot
                rating = dict()
                rating['overall'] = studyspace_obj.calculate_overall_rating()
                rating['comfort'] = studyspace_obj.calculate_comfort_rating()
                rating['noise_level'] = studyspace_obj.calculate_noise_level_rating()
                rating['crowdedness'] = studyspace_obj.calculate_crowdedness_rating()
                return render(request, 'studyspots/studyspace.html',
                              {'studyspace': studyspace_obj, 'location_id': location_id, 'rating': rating})
        else:
            if is_ajax(request):
                location = Location.objects.get(location_id=location_id)
                location_data = StudySpaceSerializer(location.studyspace_set.all(), many=True).data
                return JsonResponse(location_data, safe=False)
            else:
                return redirect(reverse("studyspots:map")+"?location="+location_id)
    else:
        raise Http404()


# method to render a form to add a pending for a study spot
@login_required
def review_studyspace(request):
    """
    Render the pending form for a specific study space.

    This function retrieves the location ID and ordinal from the request, gets the corresponding study space,
    and renders the 'studyspace_form.html' template with the location ID and study space as context variables.

    If the location ID or ordinal is not provided, the function raises an Http404 error.

    Args:
        request: The HTTP request.

    Returns:
        An HttpResponse object with the rendered text of the 'studyspace_form.html' template.
    """

    location_id = get_variable(request, 'location')
    location_ordinal = get_variable(request, 'space')
    if location_id and location_ordinal:
        studyspace_obj = get_studyspace_by_ordinal(location_id, location_ordinal)
        return render(request, 'studyspots/studyspace_form.html',
                      {'location_id': location_id, 'studyspace': studyspace_obj})
    raise Http404()


# method to process a pending for a study spot and update database
def process_studyspace_review(request):
    """
    Process a pending for a study spot and update the database.

    This function retrieves the location ID and ordinal from the request, gets the corresponding study space,
    updates its ratings and comments based on the POST data, and saves the changes to the database.

    If the location ID or ordinal is not provided, or if the request method is not POST, the function raises an Http404 error.

    Args:
        request: The HTTP request.

    Returns:
        A redirect to the 'get_spot' view for the specified location and study space.
    """

    location_id = get_variable(request, 'location')
    location_ordinal = get_variable(request, 'space')
    if location_id and location_ordinal:
        if request.method == 'POST':
            studyspace = get_studyspace_by_ordinal(location_id, location_ordinal)
            studyspace.overall_ratings.append(int(request.POST['overall']))
            studyspace.comfort_ratings.append(int(request.POST['comfort']))
            studyspace.noise_level_ratings.append(int(request.POST['noise_level']))
            studyspace.crowdedness_ratings.append(int(request.POST['crowdedness']))
            if request.POST['comment'] != "":
                studyspace.comments.append(request.POST['comment'])
            studyspace.save()
        return redirect(reverse('studyspots:get_spot') + f'?location={location_id}&space={location_ordinal}')
    else:
        raise Http404()


@login_required
def pending(request):
    studyspace_id = get_variable(request, 'studyspot')
    key = settings.GOOGLE_API_KEY
    if not studyspace_id:
        pending_studyspaces = PendingStudySpace.objects.all()
        context = {
            'pending_studyspaces': pending_studyspaces,
        }
        return render(request, 'studyspots/pending.html', context)
    pending_studyspace = get_object_or_404(PendingStudySpace, pk=studyspace_id)
    pending_location = None
    pending_lat = None
    pending_lng = None
    if pending_studyspace.content_type.model == 'pendinglocation':
        pending_location_id = pending_studyspace.object_id
        pending_location = get_object_or_404(PendingLocation, pk=pending_location_id)
        pending_lat = pending_location.lat
        pending_lng = pending_location.lng
    context = {
        'pending_studyspace': pending_studyspace,
        'pending_location': pending_location,
        'pending_lat': pending_lat,
        'pending_lng': pending_lng,
        'key': key,
    }
    return render(request, 'studyspots/pendingDetail.html', context)


class PendingAction(IntEnum):
    NO_ACTION = 0
    APPROVE = 1
    REJECT = 2
    EDIT = 3


@login_required
def approve_pending(request):
    studyspace_id = get_variable(request, "studyspot")
    if not studyspace_id:
        return redirect(reverse('studyspots:pending'), False)
    pending_studyspace = get_object_or_404(PendingStudySpace, pk=studyspace_id)
    if pending_studyspace.content_type.model == 'pendinglocation':
        new_location = Location(
            name=pending_studyspace.location.name,
            location_type=pending_studyspace.location.location_type,
            on_grounds=pending_studyspace.location.on_grounds,
            lat=pending_studyspace.location.lat,
            lng=pending_studyspace.location.lng,
        )
        new_location.save()
        new_studyspace = StudySpace(
            location_id=new_location,
            name=pending_studyspace.name,
            capacity=pending_studyspace.capacity,
            comments=pending_studyspace.comments,
            overall_ratings=pending_studyspace.overall_ratings,
            comfort_ratings=pending_studyspace.comfort_ratings,
            noise_level_ratings=pending_studyspace.noise_level_ratings,
            crowdedness_ratings=pending_studyspace.crowdedness_ratings,
        )
        new_studyspace.save()
        pending_studyspace.delete()
        pending_studyspace.location.delete()
        return render(request, 'studyspots/reviewConfirmation.html', {'action': int(PendingAction.APPROVE)})
    else:
        new_studyspace = StudySpace(
            location_id=pending_studyspace.location,
            name=pending_studyspace.name,
            capacity=pending_studyspace.capacity,
            comments=pending_studyspace.comments,
            overall_ratings=pending_studyspace.overall_ratings,
            comfort_ratings=pending_studyspace.comfort_ratings,
            noise_level_ratings=pending_studyspace.noise_level_ratings,
            crowdedness_ratings=pending_studyspace.crowdedness_ratings,
        )
        new_studyspace.save()
        pending_studyspace.delete()
        return render(request, 'studyspots/reviewConfirmation.html', {'action': int(PendingAction.APPROVE)})


@login_required
def reject_pending(request):
    studyspace_id = get_variable(request, 'studyspot')
    if not studyspace_id:
        redirect(reverse('studyspots:pending'), False)
    pending_studyspace = get_object_or_404(PendingStudySpace, pk=studyspace_id)
    if pending_studyspace.content_type.model == 'pendinglocation':
        pending_location_id = pending_studyspace.object_id
        pending_location = get_object_or_404(PendingLocation, pk=pending_location_id)
        pending_location.delete()
        pending_studyspace.delete()
    else:
        pending_studyspace.delete()

    return render(request, 'studyspots/reviewConfirmation.html', {'action': int(PendingAction.REJECT)})


def reviewConfirmation(request):
    return render(request, 'studyspots/reviewConfirmation.html')


@login_required()
def change_location(request):
    key = settings.GOOGLE_API_KEY
    studyspace_id = get_variable(request, 'studyspot')
    if not studyspace_id:
        return redirect(reverse('studyspots:pending'), False)
    pending_studyspace = get_object_or_404(PendingStudySpace, pk=studyspace_id)
    if pending_studyspace.content_type.model == 'pendinglocation':
        pending_location_id = pending_studyspace.object_id
        pending_location = get_object_or_404(PendingLocation, pk=pending_location_id)
        pending_lat = pending_location.lat
        pending_lng = pending_location.lng
        if request.method == 'POST':
            new_studyspace_form = NewStudySpaceForm(request.POST, prefix='pending_studyspace')
            new_location_form = NewLocationForm(request.POST, prefix='pending_location')
            if new_studyspace_form.is_valid():
                new_location_form.is_valid()
                lat = new_location_form.cleaned_data.get('lat', pending_lat)
                lng = new_location_form.cleaned_data.get('lng', pending_lng)
                edit_pending_location = PendingLocation(
                    name=new_location_form.cleaned_data['locationName'],
                    location_type=new_location_form.cleaned_data['location_type'],
                    on_grounds=new_location_form.cleaned_data['on_grounds'],
                    lat=lat,
                    lng=lng,
                )
                edit_pending_location.save()
                pending_location.delete()
                edit_pending_space = PendingStudySpace(
                    content_type=ContentType.objects.get_for_model(edit_pending_location),
                    object_id=edit_pending_location.pk,
                    name=new_studyspace_form.cleaned_data['studySpaceName'],
                    capacity=new_studyspace_form.cleaned_data['capacity'],
                    comments=[new_studyspace_form.cleaned_data['comment']],
                    overall_ratings=[new_studyspace_form.cleaned_data['overall_rating']],
                    comfort_ratings=[new_studyspace_form.cleaned_data['comfort_rating']],
                    noise_level_ratings=[new_studyspace_form.cleaned_data['noise_level_rating']],
                    crowdedness_ratings=[new_studyspace_form.cleaned_data['crowdedness_rating']],
                )
                edit_pending_space.save()
                pending_studyspace.delete()
                return render(request, 'studyspots/reviewConfirmation.html',  {'action': int(PendingAction.EDIT)})
    else:
        pending_location = None
        pending_lat = None
        pending_lng = None
        new_location_form = None
        if request.method == 'POST':
            new_studyspace_form = NewStudySpaceForm(request.POST)
            if new_studyspace_form.is_valid():
                edit_pending_space = PendingStudySpace(
                    content_type=ContentType.objects.get_for_model(pending_studyspace.location),
                    object_id=pending_studyspace.location.pk,
                    name=new_studyspace_form.cleaned_data['studySpaceName'],
                    capacity=new_studyspace_form.cleaned_data['capacity'],
                    comments=[new_studyspace_form.cleaned_data['comment']],
                    overall_ratings=[new_studyspace_form.cleaned_data['overall_rating']],
                    comfort_ratings=[new_studyspace_form.cleaned_data['comfort_rating']],
                    noise_level_ratings=[new_studyspace_form.cleaned_data['noise_level_rating']],
                    crowdedness_ratings=[new_studyspace_form.cleaned_data['crowdedness_rating']],
                )
                edit_pending_space.save()
                pending_studyspace.delete()
                return render(request, 'studyspots/reviewConfirmation.html', {'action': int(PendingAction.EDIT)})
    context = {
        'new_studyspace_form': new_studyspace_form,
        'pending_studyspace': pending_studyspace,
        'new_location_form': new_location_form,
        'pending_location': pending_location,
        'key': key,
        'pending_lat': pending_lat,
        'pending_lng': pending_lng
               }
    return render(request, 'studyspots/change_location.html', context)

