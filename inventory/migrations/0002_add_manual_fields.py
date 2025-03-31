from django.db import migrations, models
import django.utils.timezone

class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='equipment',
            name='manual_file',
            field=models.FileField(blank=True, null=True, upload_to='manuals/'),
        ),
        migrations.AddField(
            model_name='equipment',
            name='manual_title',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='equipment',
            name='manual_last_checked',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]