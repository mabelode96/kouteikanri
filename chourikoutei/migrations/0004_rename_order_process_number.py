# Generated by Django 4.2.16 on 2024-10-02 03:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chourikoutei', '0003_process_batcount'),
    ]

    operations = [
        migrations.RenameField(
            model_name='process',
            old_name='order',
            new_name='number',
        ),
    ]
