# Generated by Django 2.1.1 on 2019-07-29 06:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Buyer', '0003_order_orderdetail'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='order_address',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='Buyer.Address', verbose_name='订单地址'),
        ),
    ]
