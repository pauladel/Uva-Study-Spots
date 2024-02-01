from django import forms
from django.core.validators import MinValueValidator, MinLengthValidator, MaxValueValidator
from django.shortcuts import render

from .models import Location

TYPE_CHOICES = [
    ('Library', 'Library'),
    ('Academic Building', 'Academic Building'),
    ('Outdoor', 'Outdoor'),
    ('Business', 'Business'),
    ('Other', 'Other'),
]

OVERALL_RATING_CHOICES = [
    (1, '★ Would Not Recommend'),
    (2, '★★'),
    (3, '★★★'),
    (4, '★★★★'),
    (5, '★★★★★ Highly Recommend'),
]
COMFORT_RATING_CHOICES = [
    (1, 'Very Uncomfortable'),
    (2, 'Uncomfortable'),
    (3, 'Moderate'),
    (4, 'Comfortable'),
    (5, 'Very Comfortable'),
]
NOISE_RATING_CHOICES = [
    (1, 'Extremely Noisy'),
    (2, 'Somewhat Noisy'),
    (3, 'Moderate'),
    (4, 'Quiet'),
    (5, 'Extremely Quiet'),
]
CROWDEDNESS_RATING_CHOICES = [
    (1, 'Overcrowded'),
    (2, 'Crowded'),
    (3, 'Moderately Crowded'),
    (4, 'Ample Space'),
    (5, 'Empty'),
]


class LocationSelection(forms.Form):
    selected_location = forms.IntegerField(
        widget=forms.HiddenInput,
        min_value=-1,
        validators=[MinValueValidator]
)

class NewLocationForm(forms.Form):
    # These are the fields to add a location
    locationName = forms.CharField(
        label='Name of Location',
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=True  # Mark the field as required
    )
    location_type = forms.ChoiceField(
        choices=TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True  # Mark the field as required
    )
    on_grounds = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    )
    lat = forms.DecimalField(
        widget=forms.HiddenInput(attrs={'class': 'form-control'}),
        required=True  # Mark the field as required

    )
    lng = forms.DecimalField(
        widget=forms.HiddenInput(attrs={'class': 'form-control'}),
        required=True  # Mark the field as required
    )


class NewStudySpaceForm(forms.Form):

    studySpaceName = forms.CharField(
        label='Name of Spot',
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=True  # Mark the field as required
    )
    capacity = forms.IntegerField(
        label='Capacity',
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        max_value=1000,
        min_value=1,
        validators=[MinValueValidator],
        required=True  # Mark the field as required
    )
    comment = forms.CharField(
        widget=forms.Textarea(
            attrs={'class': 'form-control', 'placeholder': 'Add a description or comment about this spot!'})
        ,
        required=False
    )
    overall_rating = forms.ChoiceField(
        choices=OVERALL_RATING_CHOICES,
        initial=3,
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True  # Mark the field as required
    )
    comfort_rating = forms.ChoiceField(
        choices=COMFORT_RATING_CHOICES,
        initial=3,
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True  # Mark the field as required
    )
    noise_level_rating = forms.ChoiceField(
        choices=NOISE_RATING_CHOICES,
        initial=3,
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True  # Mark the field as required
    )
    crowdedness_rating = forms.ChoiceField(
        choices=CROWDEDNESS_RATING_CHOICES,
        initial=3,
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True  # Mark the field as required
    )

    def __int__(self, value, *args, **kwargs):
        self.location = value
