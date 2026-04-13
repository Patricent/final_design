from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0002_userprofile_bio"),
    ]

    operations = [
        migrations.AddField(
            model_name="userprofile",
            name="api_key_qwen_enc",
            field=models.TextField(blank=True, default="", verbose_name="Qwen API Key（加密）"),
        ),
        migrations.AddField(
            model_name="userprofile",
            name="api_key_deepseek_enc",
            field=models.TextField(blank=True, default="", verbose_name="DeepSeek API Key（加密）"),
        ),
        migrations.AddField(
            model_name="userprofile",
            name="api_key_openai_enc",
            field=models.TextField(blank=True, default="", verbose_name="OpenAI API Key（加密）"),
        ),
    ]
