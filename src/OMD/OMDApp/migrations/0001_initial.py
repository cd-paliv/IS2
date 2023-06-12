# Generated by Django 4.1.7 on 2023-06-11 23:38

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Campana',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('state', models.CharField(default='V', max_length=1)),
                ('name', models.CharField(max_length=50)),
                ('estimated_amount', models.FloatField(blank=True, max_length=10, null=True)),
                ('colected_amount', models.FloatField(default=0, max_length=10)),
                ('date_in', models.DateField()),
                ('date_out', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='Donacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('email', models.EmailField(max_length=254, verbose_name='dirección de correo electrónico')),
                ('amount', models.FloatField(blank=True, max_length=10, null=True)),
                ('message', models.CharField(blank=True, max_length=50, null=True)),
                ('campana', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='OMDApp.campana')),
            ],
        ),
        migrations.CreateModel(
            name='Perro',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('breed', models.CharField(max_length=20)),
                ('color', models.CharField(max_length=10)),
                ('birthdate', models.DateField()),
                ('gender', models.CharField(max_length=1)),
                ('observations', models.TextField(blank=True, null=True)),
                ('photo', models.TextField(blank=True, null=True)),
                ('weight', models.FloatField(default=0.01)),
                ('castrated', models.BooleanField(blank=True, null=True)),
                ('image', models.ImageField(blank=True, default='default.png', null=True, upload_to='dogs/')),
            ],
        ),
        migrations.CreateModel(
            name='PPEA',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('breed', models.CharField(max_length=20)),
                ('color', models.CharField(max_length=10)),
                ('state', models.CharField(max_length=1)),
                ('success', models.BooleanField(default=False)),
                ('birthdate', models.DateField(blank=True, null=True)),
                ('photo', models.TextField(blank=True, null=True)),
                ('disappeared_date', models.DateField(blank=True, null=True)),
                ('zone', models.CharField(blank=True, max_length=100, null=True)),
                ('image', models.ImageField(blank=True, default='default.png', null=True, upload_to='ppea/')),
            ],
        ),
        migrations.CreateModel(
            name='Tarjeta',
            fields=[
                ('card_name', models.CharField(max_length=50)),
                ('card_number', models.IntegerField()),
                ('card_number_security', models.IntegerField()),
                ('from_donation', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='OMDApp.donacion')),
            ],
        ),
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='dirección de correo electrónico')),
                ('password', models.CharField(max_length=50)),
                ('first_name', models.CharField(max_length=20)),
                ('last_name', models.CharField(max_length=30)),
                ('dni', models.IntegerField(unique=True)),
                ('birthdate', models.DateField()),
                ('photo', models.TextField(blank=True, null=True)),
                ('email_confirmed', models.BooleanField(default=False)),
                ('image', models.ImageField(blank=True, default='default.png', null=True, upload_to='accounts/')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'permissions': [('is_client', 'Correspondiente al rol de Cliente en la documentación')],
            },
        ),
        migrations.CreateModel(
            name='Veterinario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'permissions': [('is_vet', 'Correspondiente al rol de Veterinario en la documentación')],
            },
        ),
        migrations.CreateModel(
            name='UserAdoption',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('dog', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='OMDApp.ppea')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Turno',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('state', models.CharField(default='S', max_length=10)),
                ('type', models.CharField(max_length=15)),
                ('hour', models.CharField(max_length=50)),
                ('date', models.DateField()),
                ('motive', models.TextField()),
                ('observations', models.TextField(blank=True, null=True)),
                ('amount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('finalized_at', models.DateField(blank=True, null=True)),
                ('urgency_turns', models.TextField(blank=True, null=True)),
                ('accepted_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='OMDApp.veterinario')),
                ('solicited_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='OMDApp.perro')),
            ],
        ),
        migrations.AddField(
            model_name='ppea',
            name='publisher',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='perro',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='Libreta',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dog', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='OMDApp.perro')),
                ('finalized', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='OMDApp.turno')),
            ],
        ),
        migrations.CreateModel(
            name='Historial',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dog', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='OMDApp.perro')),
                ('finalized', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='OMDApp.turno')),
            ],
        ),
        migrations.AddField(
            model_name='donacion',
            name='usuario',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
