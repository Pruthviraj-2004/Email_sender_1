# Generated by Django 4.2.15 on 2024-08-28 18:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("sender_app", "0005_event_employee_created_at_employee_updated_at_and_more"),
    ]

    operations = [
        migrations.RenameModel(old_name="Event", new_name="OrganizationEvent",),
    ]
