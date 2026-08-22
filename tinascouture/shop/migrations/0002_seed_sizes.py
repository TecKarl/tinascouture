from django.db import migrations


def create_sizes(apps, schema_editor):
    Size = apps.get_model("shop", "Size")
    for code, _label in [("S", "Small"), ("M", "Medium"), ("L", "Large"), ("XL", "Extra Large")]:
        Size.objects.get_or_create(code=code)


def remove_sizes(apps, schema_editor):
    Size = apps.get_model("shop", "Size")
    Size.objects.filter(code__in=["S", "M", "L", "XL"]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("shop", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_sizes, remove_sizes),
    ]
