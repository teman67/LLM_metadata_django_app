# Generated by Django 4.2.16 on 2024-11-08 14:08

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('LLM_Metadata', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='conversation',
            name='conversation_id',
            field=models.UUIDField(default=uuid.uuid4, editable=False),
        ),
    ]
