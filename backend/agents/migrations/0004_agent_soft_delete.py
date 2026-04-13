from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("agents", "0003_agent_is_public"),
    ]

    operations = [
        migrations.AddField(
            model_name="agent",
            name="is_deleted",
            field=models.BooleanField(db_index=True, default=False, verbose_name="已软删除"),
        ),
        migrations.AddField(
            model_name="agent",
            name="deleted_at",
            field=models.DateTimeField(blank=True, null=True, verbose_name="删除时间"),
        ),
    ]
