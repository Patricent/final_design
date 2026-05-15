import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0003_userprofile_llm_api_keys"),
    ]

    operations = [
        migrations.AlterField(
            model_name="userprofile",
            name="avatar",
            field=models.FileField(
                blank=True,
                null=True,
                upload_to="avatars/",
                validators=[
                    django.core.validators.FileExtensionValidator(
                        allowed_extensions=["jpg", "jpeg", "png", "gif", "webp", "jfif", "bmp"]
                    )
                ],
                verbose_name="头像",
            ),
        ),
    ]
