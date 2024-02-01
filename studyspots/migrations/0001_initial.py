# Generated by Django 4.2.6 on 2023-12-03 22:50

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Location',
            fields=[
                ('location_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('location_type', models.CharField(choices=[('LIBRARY', 'Library'), ('ACADEMIC_BUILDING', 'Academic Building'), ('OUTDOOR', 'Outdoor'), ('BUSINESS', 'Business'), ('OTHER', 'Other')], default='Other', max_length=20)),
                ('address', models.CharField(max_length=255)),
                ('lat', models.DecimalField(decimal_places=7, default=0.0, max_digits=10)),
                ('lng', models.DecimalField(decimal_places=7, default=0.0, max_digits=10)),
                ('on_grounds', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='PendingLocation',
            fields=[
                ('location_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('location_type', models.CharField(choices=[('Library', 'Library'), ('Academic Building', 'Academic Building'), ('Outdoor', 'Outdoor'), ('Business', 'Business'), ('Other', 'Other')], default='Other', max_length=20)),
                ('address', models.CharField(max_length=255)),
                ('lat', models.DecimalField(decimal_places=7, default=0.0, max_digits=10)),
                ('lng', models.DecimalField(decimal_places=7, default=0.0, max_digits=10)),
                ('on_grounds', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='StudySpace',
            fields=[
                ('studyspace_id', models.AutoField(primary_key=True, serialize=False)),
                ('location_ordinal', models.IntegerField(default=-1)),
                ('name', models.CharField(max_length=100)),
                ('space_type', models.CharField(choices=[('Classroom', 'Classroom'), ('Group Study Room', 'Group Study Room'), ('Conference Room', 'Conference Room'), ('Table', 'Table'), ('Public Area', 'Public Area'), ('Other', 'Other')], default='Other', max_length=20)),
                ('comments', models.JSONField(default=list)),
                ('reservable', models.BooleanField(default=False)),
                ('capacity', models.PositiveIntegerField()),
                ('overall_ratings', models.JSONField(default=list)),
                ('comfort_ratings', models.JSONField(default=list)),
                ('noise_level_ratings', models.JSONField(default=list)),
                ('crowdedness_ratings', models.JSONField(default=list)),
                ('link', models.URLField(blank=True, null=True)),
                ('location_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='studyspots.location')),
            ],
        ),
        migrations.CreateModel(
            name='PendingStudySpace',
            fields=[
                ('studyspace_id', models.AutoField(primary_key=True, serialize=False)),
                ('object_id', models.PositiveIntegerField(default=None)),
                ('name', models.CharField(max_length=100)),
                ('space_type', models.CharField(choices=[('Classroom', 'Classroom'), ('Group Study Room', 'Group Study Room'), ('Conference Room', 'Conference Room'), ('Table', 'Table'), ('Public Area', 'Public Area'), ('Other', 'Other')], default='Other', max_length=20)),
                ('comments', models.JSONField(default=list)),
                ('reservable', models.BooleanField(default=False)),
                ('capacity', models.PositiveIntegerField()),
                ('overall_ratings', models.JSONField(default=list)),
                ('comfort_ratings', models.JSONField(default=list)),
                ('noise_level_ratings', models.JSONField(default=list)),
                ('crowdedness_ratings', models.JSONField(default=list)),
                ('link', models.URLField(blank=True, null=True)),
                ('content_type', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
            ],
        ),
        migrations.CreateModel(
            name='Admin',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_admin', models.BooleanField(default=False)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
