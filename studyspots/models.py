from django.contrib import admin
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework import serializers
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class Location(models.Model):
    # variable as identifier for each location
    location_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    # these are the location types that we have as of now, may want to change later. I added a default "Other" to
    # account for buildings/locations such as the Rotunda or a rec center that doesn't fit as nicely into a category
    TYPE_CHOICES = [
        ('LIBRARY', 'Library'),
        ('ACADEMIC_BUILDING', 'Academic Building'),
        ('OUTDOOR', 'Outdoor'),
        ('BUSINESS', 'Business'),
        ('OTHER', 'Other'),
    ]
    location_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='Other')
    # the address of the location in written form
    address = models.CharField(max_length=255)
    # coordinates is stored as a string with lat and long seperated by a comma
    lat = models.DecimalField(max_digits=10, decimal_places=7, default=0.0)
    lng = models.DecimalField(max_digits=10, decimal_places=7, default=0.0)
    # see coordinate constructor

    # want to support images if this is something we choose to add later. note: this directory does not exist yet
    # image = models.ImageField(upload_to='study_location_images/', null=True, blank=True)
    # We don't have links for any of the buildings rn. Could be nice to give option for businesses to put website.
    # could also be a link to the Google Maps location if we want to change it to that (it would be easy to generate
    # this url based on the coordinates/address)
    # this variable tells whether the building is on grounds or not. note: the prepopulated ones will all be set to true
    on_grounds = models.BooleanField(default=False)

    # link = models.URLField(max_length=200, null=True, blank=True, default=None)

    @property
    def coordinates(self):
        return {'lat': float(str(self.lat)), 'lng': float(str(self.lng))}

    def __str__(self):
        return self.name

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class LocationSerializer(serializers.ModelSerializer):
    coordinates = models.CharField()

    class Meta:
        model = Location
        fields = ['location_id', 'name', 'location_type', 'address', 'coordinates', 'on_grounds']


class PendingLocation(models.Model):
    location_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    TYPE_CHOICES = [
        ('Library', 'Library'),
        ('Academic Building', 'Academic Building'),
        ('Outdoor', 'Outdoor'),
        ('Business', 'Business'),
        ('Other', 'Other'),
    ]
    location_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='Other')
    address = models.CharField(max_length=255)
    lat = models.DecimalField(max_digits=10, decimal_places=7, default=0.0)
    lng = models.DecimalField(max_digits=10, decimal_places=7, default=0.0)
    on_grounds = models.BooleanField(default=False)

    @property
    def coordinates(self):
        return {'lat': float(str(self.lat)), 'lng': float(str(self.lng))}

    def __str__(self):
        return self.name

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class PendingLocationSerializer(serializers.ModelSerializer):
    coordinates = models.CharField()

    class Meta:
        model = PendingLocation
        fields = ['location_id', 'name', 'location_type', 'address', 'coordinates', 'on_grounds']


class StudySpace(models.Model):
    # unique identifier for each space entry
    studyspace_id = models.AutoField(primary_key=True)
    # variable to associate the space with an existing Location
    location_id = models.ForeignKey(Location, on_delete=models.CASCADE)
    # variable that shows which # the space is of its location. More information at the set_ordinal function desc.
    location_ordinal = models.IntegerField(default=-1)
    name = models.CharField(max_length=100)
    # these are all the types I could think of. Might want to add others later
    TYPE_CHOICES = [
        ('Classroom', 'Classroom'),
        ('Group Study Room', 'Group Study Room'),
        ('Conference Room', 'Conference Room'),
        ('Table', 'Table'),
        ('Public Area', 'Public Area'),
        ('Other', 'Other'),
    ]
    space_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='Other')
    # comments is where we'll have a list of comments or written reviews. can be thought of as a sort of discussion
    # space each comment will be saved in this list as a tuple in format ("userID", "user's comment here") ex (
    # "user1234", "this place is great!")
    comments = models.JSONField(default=list)
    reservable = models.BooleanField(default=False)
    capacity = models.PositiveIntegerField()
    # the overall rating for the space as a whole.
    # Each rating (the next 4 fields) will be saved in this list as a  tuple: ("userID", int(rating)) ex ("user1234", 3)
    overall_ratings = models.JSONField(default=list)
    comfort_ratings = models.JSONField(default=list)
    noise_level_ratings = models.JSONField(default=list)
    crowdedness_ratings = models.JSONField(default=list)
    # If it is reservable, the link will be to the reserving page (see spreadsheet for these links).
    # If not reservable, this field should probably just stay empty
    link = models.URLField(max_length=200, null=True, blank=True)

    # if the location has 4 items, it's nice to be able to go to each item at a time. Thus, ordinal values per location
    # location_ordinal holds which number of the location it is, and is set on save or refresh
    # the necessity to save the parent twice is due to when primary keys are generated.
    # of the options investigated, it was by far the easiest and most intuitive way to handle it
    def set_ordinal(self):
        ct = StudySpace.objects.filter(location_id=self.location_id.pk, studyspace_id__lte=self.studyspace_id).count()
        self.location_ordinal = ct

    def save(self, *args, **kwargs):
        super(StudySpace, self).save(args, kwargs)
        self.set_ordinal()
        super(StudySpace, self).save(args, kwargs)

    def refresh_from_db(self, *args, **kwargs):
        super(StudySpace, self).refresh_from_db(args, kwargs)
        self.set_ordinal()
        super(StudySpace, self).refresh_from_db(args, kwargs)

    def __str__(self):
        return self.name

    def calculate_overall_rating(self):
        return calculate_average_rating(self.overall_ratings)

    def calculate_comfort_rating(self):
        return calculate_average_rating(self.comfort_ratings)

    def calculate_noise_level_rating(self):
        return calculate_average_rating(self.noise_level_ratings)

    def calculate_crowdedness_rating(self):
        return calculate_average_rating(self.crowdedness_ratings)

    @property
    def get_owner(self):
        return Location.objects.all().get(location_id=self.location_id_id)


class StudySpaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudySpace
        fields = "__all__"


class PendingStudySpace(models.Model):
    # unique identifier for each space entry
    studyspace_id = models.AutoField(primary_key=True)
    # variable to associate the space with an existing Location
    # location_id = models.ForeignKey(PendingLocation, on_delete=models.CASCADE)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        default=None  # Default value is None, which is safe for existing entries
    )
    object_id = models.PositiveIntegerField(default=None)
    location = GenericForeignKey('content_type', 'object_id')
    name = models.CharField(max_length=100)
    # these are all the types I could think of. Might want to add others later
    TYPE_CHOICES = [
        ('Classroom', 'Classroom'),
        ('Group Study Room', 'Group Study Room'),
        ('Conference Room', 'Conference Room'),
        ('Table', 'Table'),
        ('Public Area', 'Public Area'),
        ('Other', 'Other'),
    ]
    space_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='Other')
    # comments is where we'll have a list of comments or written reviews. can be thought of as a sort of discussion
    # space each comment will be saved in this list as a tuple in format ("userID", "user's comment here") ex (
    # "user1234", "this place is great!")
    comments = models.JSONField(default=list)
    reservable = models.BooleanField(default=False)
    capacity = models.PositiveIntegerField()
    # the overall rating for the space as a whole.
    # Each rating (the next 4 fields) will be saved in this list as a  tuple: ("userID", int(rating)) ex ("user1234", 3)
    overall_ratings = models.JSONField(default=list)
    comfort_ratings = models.JSONField(default=list)
    noise_level_ratings = models.JSONField(default=list)
    crowdedness_ratings = models.JSONField(default=list)
    # If it is reservable, the link will be to the reserving page (see spreadsheet for these links).
    # If not reservable, this field should probably just stay empty
    link = models.URLField(max_length=200, null=True, blank=True)


class PendingStudySpaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = PendingStudySpace
        fields = "__all__"


def calculate_average_rating(ratings_list):
    if any([True for rating in ratings_list if type(rating) is not int]):
        ratings_list = [int(rating) for rating in ratings_list]
    total_ratings = sum(ratings_list)
    num_ratings = len(ratings_list)
    if num_ratings == 0:
        return "Not yet rated. Be the first to rate!"
    return round(total_ratings / num_ratings, 1)


class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_admin = models.BooleanField(default=False)

    @receiver(post_save, sender=User)
    def create_user_model(sender, instance, created, **kwargs):
        if created:
            Admin.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_model(sender, instance, **kwargs):
        print(instance)
        instance.admin.save()

    @property
    @admin.display(
        description="Username",
    )
    def username(obj):
        return obj.user.username

    def email(obj):
        return obj.user.email
