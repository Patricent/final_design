from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("agents", "0004_agent_soft_delete"),
    ]

    operations = [
        migrations.AddField(
            model_name="agent",
            name="kind",
            field=models.CharField(
                db_index=True,
                default="chat",
                max_length=20,
                verbose_name="类型",
            ),
        ),
        migrations.AddField(
            model_name="agent",
            name="image_width",
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name="文生图宽度"),
        ),
        migrations.AddField(
            model_name="agent",
            name="image_height",
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name="文生图高度"),
        ),
    ]
