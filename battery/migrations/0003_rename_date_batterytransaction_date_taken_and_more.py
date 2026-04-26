from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('battery', '0002_batterytransaction_hire_fee'),
    ]

    operations = [
        migrations.AddField(
            model_name='batteryitem',
            name='daily_rate',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='batterytransaction',
            name='status',
            field=models.CharField(blank=True, choices=[('out', 'Out'), ('returned', 'Returned')], max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='batterytransaction',
            name='date_returned',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='batterytransaction',
            name='total_charged',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.RenameField(
            model_name='batterytransaction',
            old_name='date',
            new_name='date_taken',
        ),
        migrations.RemoveField(
            model_name='batterytransaction',
            name='hire_fee',
        ),
    ]