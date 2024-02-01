from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.conf import settings
from studyspots.models import *
from studyspots.forms import *
from django.http import Http404


class LocationModelTests(TestCase):
    def test_attributes(self):
        new_location = Location(
            name="Clem",
            location_type="LIBRARY",
            address="Clem Road",
            lat=12.345,
            lng=-54.321,
            on_grounds=True
        )
        self.assertEqual(new_location.location_id, new_location.pk)
        self.assertEqual(new_location.name, "Clem")
        self.assertEqual(new_location.location_type, "LIBRARY")
        self.assertEqual(new_location.address, "Clem Road")
        self.assertEqual(new_location.lat, 12.345)
        self.assertEqual(new_location.lng, -54.321)
        self.assertTrue(new_location.on_grounds)

    def test_coordinates(self):
        new_location = Location(lat=34.1094, lng=98.34568)
        self.assertEqual(new_location.coordinates, {'lat': 34.1094, 'lng': 98.34568})

    def test_str(self):
        new_location = Location(name='Clem')
        self.assertEqual(str(new_location), 'Clem')


class PendingLocationModelTests(TestCase):
    def test_attributes(self):
        new_pendinglocation = PendingLocation(
            name='Clark',
            location_type='Outdoor',
            address='Clark Court',
            lat=-24.680,
            lng=98.76500,
            on_grounds=False,
        )
        self.assertEqual(new_pendinglocation.location_id, new_pendinglocation.pk)
        self.assertEqual(new_pendinglocation.name, "Clark")
        self.assertEqual(new_pendinglocation.location_type, "Outdoor")
        self.assertEqual(new_pendinglocation.address, "Clark Court")
        self.assertEqual(new_pendinglocation.lat, -24.680)
        self.assertEqual(new_pendinglocation.lng, 98.76500)
        self.assertFalse(new_pendinglocation.on_grounds)

    def test_coordinates(self):
        location = Location(lat=22.223, lng=55.667)
        self.assertEqual(location.coordinates, {'lat': 22.223, 'lng': 55.667})

    def test_str(self):
        new_pendinglocation = PendingLocation(name='Clark Hall')
        self.assertEqual(str(new_pendinglocation), 'Clark Hall')


class StudySpaceModelTests(TestCase):
    def test_attributes(self):
        new_location = Location(name="Library")
        new_studyspace = StudySpace(
            location_id=new_location,
            name='Clem 22',
            space_type='Classroom',
            capacity=30,
            comments='nice classroom',
            overall_ratings='★ Would Not Recommend',
            comfort_ratings='Very Uncomfortable',
            noise_level_ratings='Extremely Noisy',
            crowdedness_ratings='Overcrowded',
            reservable=True,
        )
        self.assertEqual(new_studyspace.studyspace_id, new_studyspace.pk)
        self.assertEqual(new_studyspace.location_id, new_location)
        self.assertEqual(new_studyspace.name, 'Clem 22')
        self.assertEqual(new_studyspace.space_type, 'Classroom')
        self.assertEqual(new_studyspace.capacity, 30)
        self.assertEqual(new_studyspace.comments, 'nice classroom')
        self.assertEqual(new_studyspace.overall_ratings, '★ Would Not Recommend')
        self.assertEqual(new_studyspace.comfort_ratings, 'Very Uncomfortable')
        self.assertEqual(new_studyspace.noise_level_ratings, 'Extremely Noisy')
        self.assertEqual(new_studyspace.crowdedness_ratings, 'Overcrowded')
        self.assertTrue(new_studyspace.reservable)

    def test_str(self):
        new_studyspace = StudySpace(name='Clem 10')
        self.assertEqual(str(new_studyspace), 'Clem 10')

    def test_calculate(self):
        new_studyspace = StudySpace(overall_ratings=[1, 2, 3])
        overall_rating = new_studyspace.calculate_overall_rating()
        self.assertEqual(overall_rating, 2.0)
        self.assertNotEqual(overall_rating, 3.0)


class PendingStudySpaceModelTests(TestCase):
    def test_attributes(self):
        new_location = PendingLocation(name="Lib")
        new_pendingstudyspace = PendingStudySpace(
            object_id=new_location.pk,
            name='Clark 24',
            capacity=55,
            comments='big room',
            overall_ratings=4,
            comfort_ratings=3,
            noise_level_ratings=2,
            crowdedness_ratings=1,
            space_type='Group Study Room',
            reservable=False
        )
        self.assertEqual(new_pendingstudyspace.studyspace_id, new_pendingstudyspace.pk)
        self.assertEqual(new_pendingstudyspace.object_id, new_location.pk)
        self.assertEqual(new_pendingstudyspace.name, 'Clark 24')
        self.assertEqual(new_pendingstudyspace.space_type, 'Group Study Room')
        self.assertEqual(new_pendingstudyspace.capacity, 55)
        self.assertEqual(new_pendingstudyspace.comments, 'big room')
        self.assertEqual(new_pendingstudyspace.overall_ratings, 4)
        self.assertEqual(new_pendingstudyspace.comfort_ratings, 3)
        self.assertEqual(new_pendingstudyspace.noise_level_ratings, 2)
        self.assertEqual(new_pendingstudyspace.crowdedness_ratings, 1)
        self.assertFalse(new_pendingstudyspace.reservable)


class AdminModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='jane', password='hello123', email='jane@gmail.com')

    def test_create_user(self):
        self.assertTrue(Admin.objects.filter(user=self.user).exists())

    def test_username(self):
        admin = Admin.objects.get(user=self.user)
        self.assertEqual(admin.username, 'jane')

    def test_email(self):
        admin = Admin.objects.get(user=self.user)
        self.assertEqual(admin.user.email, 'jane@gmail.com')

    def test_is_admin(self):
        admin = Admin.objects.get(user=self.user)
        admin.is_admin = True
        self.assertTrue(admin.is_admin)


class ProfileViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='username', password='password123')

    def test_redirect_no_login(self):
        response = self.client.get(reverse('studyspots:login'))
        self.assertRedirects(response, '/accounts/login/?next=/login/')

    def test_wrong_login(self):
        self.assertTrue(isinstance(self.user, User))
        login = self.client.login(username="john", password='bluesky321')
        self.assertEqual(login, False)

    def test_correct_login(self):
        self.assertTrue(isinstance(self.user, User))
        login = self.client.login(username='username', password='password123')
        self.assertEqual(login, True)

    def test_logout(self):
        response = self.client.get(reverse('studyspots:logout'))
        self.assertRedirects(response, '/')


class MapViewTests(TestCase):
    def test_load_map(self):
        response = self.client.get(reverse('studyspots:map'))
        self.assertTemplateUsed(response, 'studyspots/map.html')
        self.assertEqual(response.context['key'], settings.GOOGLE_API_KEY)


class AddViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='username', password='password123')
        login = self.client.login(username='username', password='password123')
        self.assertEqual(login, True)

    def test_add_exisiting_location(self):
        new_location = Location(name="Clem")
        new_pendingstudyspace = PendingStudySpace(
            object_id=new_location.pk,
            name='Clark 24',
            capacity=55,
            comments='big room',
            overall_ratings=4,
            comfort_ratings=3,
            noise_level_ratings=2,
            crowdedness_ratings=1,
            space_type='Group Study Room',
            reservable=False
        )
        self.assertEqual(new_pendingstudyspace.studyspace_id, new_pendingstudyspace.pk)

    def test_add_new_location(self):
        new_location = PendingLocation(name='Brown')
        new_pendingstudyspace = PendingStudySpace(
            object_id=new_location.pk,
            name='Clark 24',
            capacity=55,
            comments='big room',
            overall_ratings=4,
            comfort_ratings=3,
            noise_level_ratings=2,
            crowdedness_ratings=1,
            space_type='Group Study Room',
            reservable=False
        )
        self.assertEqual(new_pendingstudyspace.studyspace_id, new_pendingstudyspace.pk)


class GetSpotViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='username', password='password123')
        login = self.client.login(username='username', password='password123')
        self.assertEqual(login, True)
        self.getspot_url = reverse('studyspots:get_spot')

    def test_get_no_location_and_ordinal(self):
        response = self.client.get(self.getspot_url)
        self.assertEqual(response.status_code, 404)

    def test_get_invalid_location_and_ordinal(self):
        response = self.client.get(self.getspot_url, {'location': 9999, 'space': 9999})
        self.assertEqual(response.status_code, 404)


class ReviewStudyspaceViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='username', password='password123')
        login = self.client.login(username='username', password='password123')
        self.assertEqual(login, True)
        self.review_url = reverse('studyspots:review_studyspace')

    def test_review_success(self):
        self.location = Location(
            location_id=2
        )
        self.studyspace = StudySpace(
            studyspace_id=2
        )
        response = self.client.get(self.review_url, {'location': self.location.location_id, 'space': self.studyspace.studyspace_id})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'studyspots/studyspace_form.html')

    def test_review_raises_404(self):
        response = self.client.get(self.review_url)
        self.assertEqual(response.status_code, 404)


class ProcessStudyspaceViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='username', password='password123')
        login = self.client.login(username='username', password='password123')
        self.assertEqual(login, True)
        self.process_review_url = reverse('studyspots:process_studyspace_review')

    def test_process_success(self):
        self.location = Location(
            location_id=3
        )
        self.studyspace = StudySpace(
            studyspace_id=3,
            comments='Great study room'
        )
        response = self.client.post(self.process_review_url, {'location': self.location.location_id, 'space': self.studyspace.studyspace_id})
        self.assertTrue(self.studyspace.comments, 'Great study room')

    def test_process_invalid_params(self):
        response = self.client.post(self.process_review_url, {'location': -1, 'space': -2})
        self.assertEqual(response.status_code, 404)

    def test_process_no_params(self):
        response = self.client.get(self.process_review_url)
        self.assertEqual(response.status_code, 404)


class PendingViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='username', password='password123')
        login = self.client.login(username='username', password='password123')
        self.assertEqual(login, True)
        self.pending_url = reverse('studyspots:pending')
        self.pending_studyspace = PendingStudySpace(
            studyspace_id=1,
            name='room 1'
        )
        self.pending_location = PendingLocation(
            location_id=1,
            name='alderman library'
        )

    def test_pending_valid_id(self):
        response = self.client.get(self.pending_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'studyspots/pending.html')
        self.assertIn('pending_studyspaces', response.context)
        self.assertEqual(self.pending_studyspace.name, 'room 1')

    def test_pending_invalid_id(self):
        response = self.client.get(self.pending_url, {'studyspot': '-2'})
        self.assertEqual(response.status_code, 404)


class ApprovePendingTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='username', password='password123')
        login = self.client.login(username='username', password='password123')
        self.assertEqual(login, True)
        self.pending_studyspace = PendingStudySpace(
            studyspace_id=1,
            name='room 1'
        )
        self.pending_location = PendingLocation(
            location_id=1,
            name='alderman library'
        )
        self.approve_url = reverse('studyspots:approve_pending')

    def test_approve_success(self):
        response = self.client.get(self.approve_url, {'studyspot': '1'})
        self.assertFalse(PendingStudySpace.objects.filter(studyspace_id=self.pending_studyspace.studyspace_id).exists())
        self.assertFalse(StudySpace.objects.filter(name=self.pending_studyspace.name).exists())

    def test_approve_fail(self):
        response = self.client.get(self.approve_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('studyspots:pending'))


class RejectPendingTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='username', password='password123')
        login = self.client.login(username='username', password='password123')
        self.assertEqual(login, True)
        self.pending_studyspace = PendingStudySpace(
            studyspace_id=1,
            name='room 1'
        )
        self.pending_location = PendingLocation(
            location_id=1,
            name='alderman library'
        )
        self.reject_url = reverse('studyspots:reject_pending')

    def test_reject_success(self):
        response = self.client.get(self.reject_url, {'studyspot': self.pending_studyspace.studyspace_id})
        self.assertFalse(PendingStudySpace.objects.filter(studyspace_id=self.pending_studyspace.studyspace_id).exists())

    def test_reject_fail(self):
        response = self.client.get(self.reject_url)
        self.assertEqual(response.status_code, 404)

    def test_reject_pendinglocation_success(self):
        response = self.client.get(self.reject_url, {'studyspot': self.pending_studyspace.studyspace_id})
        self.assertFalse(PendingLocation.objects.filter(location_id=self.pending_location.location_id).exists())
        self.assertFalse(PendingStudySpace.objects.filter(studyspace_id=self.pending_studyspace.studyspace_id).exists())