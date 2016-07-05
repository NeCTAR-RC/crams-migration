# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import django.core.validators
import datetime


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('authtoken', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AllocationHome',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('code', models.CharField(max_length=50)),
                ('description', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='ComputeProduct',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('name', models.CharField(max_length=200)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ComputeRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('instances', models.IntegerField(validators=[django.core.validators.MinValueValidator(1)], default=2)),
                ('approved_instances', models.IntegerField(validators=[django.core.validators.MinValueValidator(1)], default=2)),
                ('cores', models.IntegerField(validators=[django.core.validators.MinValueValidator(1)], default=2)),
                ('approved_cores', models.IntegerField(validators=[django.core.validators.MinValueValidator(1)], default=2)),
                ('core_hours', models.IntegerField(validators=[django.core.validators.MinValueValidator(1)], default=744)),
                ('approved_core_hours', models.IntegerField(validators=[django.core.validators.MinValueValidator(1)], default=744)),
                ('compute_product', models.ForeignKey(to='crams.ComputeProduct', related_name='compute_requests')),
            ],
        ),
        migrations.CreateModel(
            name='ComputeRequestQuestionResponse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('question_response', models.TextField(max_length=1024, blank=True)),
                ('compute_request', models.ForeignKey(to='crams.ComputeRequest', related_name='compute_question_responses')),
            ],
        ),
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('title', models.CharField(max_length=50, blank=True, null=True)),
                ('given_name', models.CharField(max_length=200, blank=True, null=True)),
                ('surname', models.CharField(max_length=200, blank=True, null=True)),
                ('email', models.EmailField(max_length=254)),
                ('phone', models.CharField(max_length=50, blank=True, null=True)),
                ('organisation', models.CharField(max_length=200, blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ContactRole',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='CramsToken',
            fields=[
                ('token_ptr', models.OneToOneField(to='authtoken.Token', auto_created=True, parent_link=True, primary_key=True, serialize=False)),
                ('ks_roles', models.TextField(blank=True, null=True)),
            ],
            bases=('authtoken.token',),
        ),
        migrations.CreateModel(
            name='Domain',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('percentage', models.FloatField(default=0.0)),
            ],
        ),
        migrations.CreateModel(
            name='Duration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('duration', models.IntegerField(validators=[django.core.validators.MinValueValidator(1)], default=1)),
                ('duration_label', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='FORCode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('code', models.CharField(max_length=50)),
                ('description', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='FundingBody',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('name', models.CharField(max_length=200)),
                ('email', models.EmailField(max_length=254)),
            ],
        ),
        migrations.CreateModel(
            name='FundingScheme',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('funding_scheme', models.CharField(max_length=200)),
                ('funding_body', models.ForeignKey(to='crams.FundingBody', related_name='funding_schemes')),
            ],
        ),
        migrations.CreateModel(
            name='Grant',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('funding_body_and_scheme', models.CharField(max_length=200)),
                ('grant_id', models.CharField(max_length=200, blank=True)),
                ('start_year', models.IntegerField(validators=[django.core.validators.MinValueValidator(1970), django.core.validators.MaxValueValidator(3000)], error_messages={'min_value': 'Please input a year between 1970 ~ 3000', 'max_value': 'Please input a year between 1970 ~ 3000'}, default=2016)),
                ('total_funding', models.FloatField(blank=True, default=0.0)),
            ],
        ),
        migrations.CreateModel(
            name='GrantType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('description', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='InternalMigrationData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('data', models.TextField()),
                ('contact', models.ForeignKey(blank=True, to='crams.Contact', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('creation_ts', models.DateTimeField(auto_now_add=True)),
                ('last_modified_ts', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('notes', models.TextField(max_length=1024, blank=True, null=True)),
                ('created_by', models.ForeignKey(blank=True, related_name='project_created_by', to=settings.AUTH_USER_MODEL, null=True)),
                ('parent_project', models.ForeignKey(blank=True, to='crams.Project', null=True)),
                ('updated_by', models.ForeignKey(blank=True, related_name='project_updated_by', to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ProjectContact',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('contact', models.ForeignKey(to='crams.Contact', related_name='project_contacts')),
                ('contact_role', models.ForeignKey(to='crams.ContactRole', related_name='project_contacts')),
                ('project', models.ForeignKey(to='crams.Project', related_name='project_contacts')),
            ],
        ),
        migrations.CreateModel(
            name='ProjectID',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('identifier', models.CharField(max_length=64)),
                ('project', models.ForeignKey(to='crams.Project', related_name='project_ids')),
            ],
        ),
        migrations.CreateModel(
            name='ProjectIDSystem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('system', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='ProjectProvisionDetails',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('project', models.ForeignKey(to='crams.Project', related_name='linked_provisiondetails')),
            ],
        ),
        migrations.CreateModel(
            name='ProjectQuestionResponse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('question_response', models.TextField(max_length=1024, blank=True)),
                ('project', models.ForeignKey(to='crams.Project', related_name='project_question_responses')),
            ],
        ),
        migrations.CreateModel(
            name='Provider',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('creation_ts', models.DateTimeField(auto_now_add=True)),
                ('last_modified_ts', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=200)),
                ('start_date', models.DateField(auto_now_add=True)),
                ('active', models.BooleanField(default=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('crams_user', models.OneToOneField(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('created_by', models.ForeignKey(blank=True, related_name='provider_created_by', to=settings.AUTH_USER_MODEL, null=True)),
                ('updated_by', models.ForeignKey(blank=True, related_name='provider_updated_by', to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ProvisionDetails',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('creation_ts', models.DateTimeField(auto_now_add=True)),
                ('last_modified_ts', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(max_length=1, default='S', choices=[('S', 'Sent'), ('P', 'Provisioned'), ('F', 'Failed'), ('L', 'Resend'), ('U', 'Updated'), ('X', 'Update Sent')])),
                ('message', models.TextField(blank=True, null=True)),
                ('created_by', models.ForeignKey(blank=True, related_name='provisiondetails_created_by', to=settings.AUTH_USER_MODEL, null=True)),
                ('provider', models.ForeignKey(to='crams.Provider', related_name='provisioned_requests')),
                ('updated_by', models.ForeignKey(blank=True, related_name='provisiondetails_updated_by', to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Publication',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('reference', models.CharField(max_length=255)),
                ('project', models.ForeignKey(to='crams.Project', related_name='publications')),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('key', models.CharField(max_length=50)),
                ('question_type', models.CharField(max_length=200)),
                ('question', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Request',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('creation_ts', models.DateTimeField(auto_now_add=True)),
                ('last_modified_ts', models.DateTimeField(auto_now=True)),
                ('start_date', models.DateField(default=datetime.date.today)),
                ('end_date', models.DateField()),
                ('approval_notes', models.TextField(max_length=1024, blank=True, null=True)),
                ('created_by', models.ForeignKey(blank=True, related_name='request_created_by', to=settings.AUTH_USER_MODEL, null=True)),
                ('funding_scheme', models.ForeignKey(to='crams.FundingScheme', related_name='requests')),
                ('parent_request', models.ForeignKey(blank=True, related_name='history', to='crams.Request', null=True)),
                ('project', models.ForeignKey(to='crams.Project', related_name='requests')),
            ],
        ),
        migrations.CreateModel(
            name='RequestQuestionResponse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('question_response', models.TextField(max_length=1024, blank=True)),
                ('question', models.ForeignKey(to='crams.Question', related_name='request_question_responses')),
                ('request', models.ForeignKey(to='crams.Request', related_name='request_question_responses')),
            ],
        ),
        migrations.CreateModel(
            name='RequestStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('code', models.CharField(max_length=50)),
                ('status', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='StorageProduct',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('name', models.CharField(max_length=200)),
                ('funding_body', models.ForeignKey(to='crams.FundingBody', related_name='storageproduct')),
                ('provider', models.ForeignKey(to='crams.Provider', related_name='storageproduct')),
            ],
        ),
        migrations.CreateModel(
            name='StorageRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('quota', models.FloatField(default=0.0)),
                ('approved_quota', models.FloatField(default=0.0)),
                ('provision_details', models.OneToOneField(blank=True, related_name='storagerequest', to='crams.ProvisionDetails', null=True)),
                ('request', models.ForeignKey(to='crams.Request', related_name='storage_requests')),
                ('storage_product', models.ForeignKey(to='crams.StorageProduct', related_name='storage_requests')),
            ],
        ),
        migrations.CreateModel(
            name='StorageRequestQuestionResponse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('question_response', models.TextField(max_length=1024, blank=True)),
                ('question', models.ForeignKey(to='crams.Question', related_name='storage_question_responses')),
                ('storage_request', models.ForeignKey(to='crams.StorageRequest', related_name='storage_question_responses')),
            ],
        ),
        migrations.CreateModel(
            name='StorageType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('storage_type', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='SupportedInstitution',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('institution', models.CharField(max_length=200)),
                ('project', models.ForeignKey(to='crams.Project', related_name='institutions')),
            ],
        ),
        migrations.CreateModel(
            name='UserEvents',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('creation_ts', models.DateTimeField(auto_now_add=True)),
                ('last_modified_ts', models.DateTimeField(auto_now=True)),
                ('event_message', models.TextField()),
                ('created_by', models.ForeignKey(blank=True, related_name='userevents_created_by', to=settings.AUTH_USER_MODEL, null=True)),
                ('updated_by', models.ForeignKey(blank=True, related_name='userevents_updated_by', to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Zone',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('name', models.CharField(max_length=64)),
                ('description', models.TextField()),
            ],
        ),
        migrations.AddField(
            model_name='storageproduct',
            name='storage_type',
            field=models.ForeignKey(to='crams.StorageType', related_name='storage_products'),
        ),
        migrations.AddField(
            model_name='storageproduct',
            name='zone',
            field=models.ForeignKey(blank=True, related_name='storage_products', to='crams.Zone', null=True),
        ),
        migrations.AddField(
            model_name='request',
            name='request_status',
            field=models.ForeignKey(to='crams.RequestStatus', related_name='requests'),
        ),
        migrations.AddField(
            model_name='request',
            name='updated_by',
            field=models.ForeignKey(blank=True, related_name='request_updated_by', to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='projectquestionresponse',
            name='question',
            field=models.ForeignKey(to='crams.Question', related_name='project_question_responses'),
        ),
        migrations.AddField(
            model_name='projectprovisiondetails',
            name='provision_details',
            field=models.ForeignKey(to='crams.ProvisionDetails', related_name='linked_projects'),
        ),
        migrations.AddField(
            model_name='projectid',
            name='system',
            field=models.ForeignKey(to='crams.ProjectIDSystem', related_name='project_ids'),
        ),
        migrations.AddField(
            model_name='internalmigrationdata',
            name='project',
            field=models.ForeignKey(blank=True, to='crams.Project', null=True),
        ),
        migrations.AddField(
            model_name='internalmigrationdata',
            name='request',
            field=models.ForeignKey(blank=True, to='crams.Request', null=True),
        ),
        migrations.AddField(
            model_name='internalmigrationdata',
            name='system',
            field=models.ForeignKey(to='crams.ProjectIDSystem'),
        ),
        migrations.AddField(
            model_name='grant',
            name='grant_type',
            field=models.ForeignKey(to='crams.GrantType', related_name='grants'),
        ),
        migrations.AddField(
            model_name='grant',
            name='project',
            field=models.ForeignKey(to='crams.Project', related_name='grants'),
        ),
        migrations.AddField(
            model_name='domain',
            name='for_code',
            field=models.ForeignKey(to='crams.FORCode', related_name='domains'),
        ),
        migrations.AddField(
            model_name='domain',
            name='project',
            field=models.ForeignKey(to='crams.Project', related_name='domains'),
        ),
        migrations.AddField(
            model_name='computerequestquestionresponse',
            name='question',
            field=models.ForeignKey(to='crams.Question', related_name='compute_question_responses'),
        ),
        migrations.AddField(
            model_name='computerequest',
            name='provision_details',
            field=models.OneToOneField(blank=True, related_name='computerequest', to='crams.ProvisionDetails', null=True),
        ),
        migrations.AddField(
            model_name='computerequest',
            name='request',
            field=models.ForeignKey(to='crams.Request', related_name='compute_requests'),
        ),
        migrations.AddField(
            model_name='computeproduct',
            name='funding_body',
            field=models.ForeignKey(to='crams.FundingBody', related_name='computeproduct'),
        ),
        migrations.AddField(
            model_name='computeproduct',
            name='provider',
            field=models.ForeignKey(to='crams.Provider', related_name='computeproduct'),
        ),
    ]
