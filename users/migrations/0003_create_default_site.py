from django.db import migrations
from django.conf import settings

def create_default_site(apps, schema_editor):
    Site = apps.get_model('sites', 'Site')
    Site.objects.get_or_create(
        id=settings.SITE_ID,
        defaults={
            'domain': 'localhost:8000',
            'name': 'ROKNSOUND Rental Inventory'
        }
    )

class Migration(migrations.Migration):
    dependencies = [
        ('users', '0002_create_default_site'),
        ('sites', '0002_alter_domain_unique'),
    ]

    operations = [
        migrations.RunPython(create_default_site),
    ]
