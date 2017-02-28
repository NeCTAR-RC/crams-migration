# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rcportal_migration.settings import BASE_DIR
from django.db import migrations, models
import django.core.validators
from django.conf import settings
import datetime
import os


def load_crams_inital_data_from_sql():
    file_name = 'crams/sql/crams_initial.mysql.sql'

    sql_statements = open(os.path.join(BASE_DIR, file_name), 'r').read()

    return sql_statements

def load_forcode_data_from_sql():
    file_name = 'crams/sql/forcode.sql'

    sql_statements = open(os.path.join(BASE_DIR, file_name), 'r').read()

    return sql_statements


class Migration(migrations.Migration):

    dependencies = [
        ('authtoken', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AllocationHome',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('code', models.CharField(max_length=50, unique=True)),
                ('description', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='ComputeProduct',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=200)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ComputeRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('instances', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)])),
                ('approved_instances', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)])),
                ('cores', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)])),
                ('approved_cores', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)])),
                ('core_hours', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)])),
                ('approved_core_hours', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)])),
                ('compute_product', models.ForeignKey(related_name='compute_requests', to='crams.ComputeProduct')),
            ],
        ),
        migrations.CreateModel(
            name='ComputeRequestQuestionResponse',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('question_response', models.TextField(max_length=1024, blank=True)),
                ('compute_request', models.ForeignKey(related_name='compute_question_responses', to='crams.ComputeRequest')),
            ],
        ),
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('title', models.CharField(max_length=50, null=True, blank=True)),
                ('given_name', models.CharField(max_length=200, null=True, blank=True)),
                ('surname', models.CharField(max_length=200, null=True, blank=True)),
                ('email', models.EmailField(max_length=254)),
                ('phone', models.CharField(max_length=50, null=True, blank=True)),
                ('organisation', models.CharField(max_length=200, null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='ContactRole',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='CramsToken',
            fields=[
                ('token_ptr', models.OneToOneField(to='authtoken.Token', serialize=False, primary_key=True, parent_link=True, auto_created=True)),
                ('ks_roles', models.TextField(blank=True, null=True)),
            ],
            bases=('authtoken.token',),
        ),
        migrations.CreateModel(
            name='Domain',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('percentage', models.FloatField(default=0.0)),
            ],
        ),
        migrations.CreateModel(
            name='Duration',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('duration', models.IntegerField(default=1, validators=[django.core.validators.MinValueValidator(1)])),
                ('duration_label', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='FORCode',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('code', models.CharField(max_length=50)),
                ('description', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='FundingBody',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('email', models.EmailField(max_length=254, null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='FundingScheme',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('funding_scheme', models.CharField(max_length=200)),
                ('funding_body', models.ForeignKey(related_name='funding_schemes', to='crams.FundingBody')),
            ],
        ),
        migrations.CreateModel(
            name='Grant',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('funding_body_and_scheme', models.CharField(max_length=200)),
                ('grant_id', models.CharField(max_length=200, null=True, blank=True)),
                ('start_year', models.IntegerField(default=2017, error_messages={'max_value': 'Please input a year between 1970 ~ 3000', 'min_value': 'Please input a year between 1970 ~ 3000'}, validators=[django.core.validators.MinValueValidator(1970), django.core.validators.MaxValueValidator(3000)])),
                ('duration', models.IntegerField(error_messages={'max_value': 'Please enter funding duration (in months 1~1000).', 'min_value': 'Please enter funding duration (in months 1-1000).'}, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(1000)])),
                ('total_funding', models.FloatField(default=0.0, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='GrantType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('description', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='InternalMigrationData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('data', models.TextField()),
                ('contact', models.ForeignKey(to='crams.Contact', blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='NotificationTemplate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('template_file_path', models.CharField(max_length=99)),
                ('alert_funding_body', models.BooleanField(default=False)),
                ('funding_body', models.ForeignKey(related_name='notification_templates', to='crams.FundingBody')),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('creation_ts', models.DateTimeField(auto_now_add=True)),
                ('last_modified_ts', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=255)),
                ('description', models.CharField(max_length=1500)),
                ('notes', models.TextField(max_length=1024, null=True, blank=True)),
                ('created_by', models.ForeignKey(related_name='project_created_by', to=settings.AUTH_USER_MODEL, blank=True, null=True)),
                ('parent_project', models.ForeignKey(to='crams.Project', blank=True, null=True)),
                ('updated_by', models.ForeignKey(related_name='project_updated_by', to=settings.AUTH_USER_MODEL, blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ProjectContact',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('contact', models.ForeignKey(related_name='project_contacts', to='crams.Contact')),
                ('contact_role', models.ForeignKey(related_name='project_contacts', to='crams.ContactRole')),
                ('project', models.ForeignKey(related_name='project_contacts', to='crams.Project')),
            ],
        ),
        migrations.CreateModel(
            name='ProjectID',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('identifier', models.CharField(max_length=64)),
                ('project', models.ForeignKey(related_name='project_ids', to='crams.Project')),
            ],
        ),
        migrations.CreateModel(
            name='ProjectIDSystem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('system', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='ProjectProvisionDetails',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('project', models.ForeignKey(related_name='linked_provisiondetails', to='crams.Project')),
            ],
        ),
        migrations.CreateModel(
            name='ProjectQuestionResponse',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('question_response', models.TextField(max_length=1024, blank=True)),
                ('project', models.ForeignKey(related_name='project_question_responses', to='crams.Project')),
            ],
        ),
        migrations.CreateModel(
            name='Provider',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('creation_ts', models.DateTimeField(auto_now_add=True)),
                ('last_modified_ts', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=200)),
                ('start_date', models.DateField(auto_now_add=True)),
                ('active', models.BooleanField(default=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('crams_user', models.OneToOneField(to=settings.AUTH_USER_MODEL, blank=True, null=True)),
                ('created_by', models.ForeignKey(related_name='provider_created_by', to=settings.AUTH_USER_MODEL, blank=True, null=True)),
                ('updated_by', models.ForeignKey(related_name='provider_updated_by', to=settings.AUTH_USER_MODEL, blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ProvisionDetails',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('creation_ts', models.DateTimeField(auto_now_add=True)),
                ('last_modified_ts', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(default='S', max_length=1, choices=[('S', 'Sent'), ('P', 'Provisioned'), ('F', 'Failed'), ('L', 'Resend'), ('U', 'Updated'), ('X', 'Update Sent')])),
                ('message', models.TextField(blank=True, null=True)),
                ('created_by', models.ForeignKey(related_name='provisiondetails_created_by', to=settings.AUTH_USER_MODEL, blank=True, null=True)),
                ('provider', models.ForeignKey(related_name='provisioned_requests', to='crams.Provider')),
                ('updated_by', models.ForeignKey(related_name='provisiondetails_updated_by', to=settings.AUTH_USER_MODEL, blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Publication',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('reference', models.CharField(max_length=255)),
                ('project', models.ForeignKey(related_name='publications', to='crams.Project')),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('key', models.CharField(max_length=50)),
                ('question_type', models.CharField(max_length=200)),
                ('question', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Request',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('creation_ts', models.DateTimeField(auto_now_add=True)),
                ('last_modified_ts', models.DateTimeField(auto_now=True)),
                ('national_percent', models.PositiveSmallIntegerField(default=100, validators=[django.core.validators.MaxValueValidator(100)])),
                ('start_date', models.DateField(default=datetime.date.today)),
                ('end_date', models.DateField()),
                ('approval_notes', models.TextField(max_length=1024, null=True, blank=True)),
                ('allocation_home', models.ForeignKey(related_name='requests', to='crams.AllocationHome', blank=True, null=True)),
                ('created_by', models.ForeignKey(related_name='request_created_by', to=settings.AUTH_USER_MODEL, blank=True, null=True)),
                ('funding_scheme', models.ForeignKey(related_name='requests', to='crams.FundingScheme')),
                ('parent_request', models.ForeignKey(related_name='history', to='crams.Request', blank=True, null=True)),
                ('project', models.ForeignKey(related_name='requests', to='crams.Project')),
            ],
        ),
        migrations.CreateModel(
            name='RequestQuestionResponse',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('question_response', models.TextField(max_length=1024, blank=True)),
                ('question', models.ForeignKey(related_name='request_question_responses', to='crams.Question')),
                ('request', models.ForeignKey(related_name='request_question_responses', to='crams.Request')),
            ],
        ),
        migrations.CreateModel(
            name='RequestStatus',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('code', models.CharField(max_length=50)),
                ('status', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='StorageProduct',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('funding_body', models.ForeignKey(related_name='storageproduct', to='crams.FundingBody')),
                ('provider', models.ForeignKey(related_name='storageproduct', to='crams.Provider')),
            ],
        ),
        migrations.CreateModel(
            name='StorageRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('quota', models.FloatField(default=0.0)),
                ('approved_quota', models.FloatField(default=0.0)),
                ('provision_details', models.OneToOneField(related_name='storagerequest', to='crams.ProvisionDetails', blank=True, null=True)),
                ('request', models.ForeignKey(related_name='storage_requests', to='crams.Request')),
                ('storage_product', models.ForeignKey(related_name='storage_requests', to='crams.StorageProduct')),
            ],
        ),
        migrations.CreateModel(
            name='StorageRequestQuestionResponse',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('question_response', models.TextField(max_length=1024, blank=True)),
                ('question', models.ForeignKey(related_name='storage_question_responses', to='crams.Question')),
                ('storage_request', models.ForeignKey(related_name='storage_question_responses', to='crams.StorageRequest')),
            ],
        ),
        migrations.CreateModel(
            name='StorageType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('storage_type', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='SupportedInstitution',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('institution', models.CharField(max_length=200)),
                ('project', models.ForeignKey(related_name='institutions', to='crams.Project')),
            ],
        ),
        migrations.CreateModel(
            name='UserEvents',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('creation_ts', models.DateTimeField(auto_now_add=True)),
                ('last_modified_ts', models.DateTimeField(auto_now=True)),
                ('event_message', models.TextField()),
                ('created_by', models.ForeignKey(related_name='userevents_created_by', to=settings.AUTH_USER_MODEL, blank=True, null=True)),
                ('updated_by', models.ForeignKey(related_name='userevents_updated_by', to=settings.AUTH_USER_MODEL, blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Zone',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=64)),
                ('description', models.TextField()),
            ],
        ),
        migrations.AddField(
            model_name='storageproduct',
            name='storage_type',
            field=models.ForeignKey(related_name='storage_products', to='crams.StorageType'),
        ),
        migrations.AddField(
            model_name='storageproduct',
            name='zone',
            field=models.ForeignKey(related_name='storage_products', to='crams.Zone', blank=True, null=True),
        ),
        migrations.AddField(
            model_name='request',
            name='request_status',
            field=models.ForeignKey(related_name='requests', to='crams.RequestStatus'),
        ),
        migrations.AddField(
            model_name='request',
            name='updated_by',
            field=models.ForeignKey(related_name='request_updated_by', to=settings.AUTH_USER_MODEL, blank=True, null=True),
        ),
        migrations.AddField(
            model_name='projectquestionresponse',
            name='question',
            field=models.ForeignKey(related_name='project_question_responses', to='crams.Question'),
        ),
        migrations.AddField(
            model_name='projectprovisiondetails',
            name='provision_details',
            field=models.ForeignKey(related_name='linked_projects', to='crams.ProvisionDetails'),
        ),
        migrations.AddField(
            model_name='projectid',
            name='system',
            field=models.ForeignKey(related_name='project_ids', to='crams.ProjectIDSystem'),
        ),
        migrations.AddField(
            model_name='notificationtemplate',
            name='request_status',
            field=models.ForeignKey(to='crams.RequestStatus'),
        ),
        migrations.AddField(
            model_name='internalmigrationdata',
            name='project',
            field=models.ForeignKey(to='crams.Project', blank=True, null=True),
        ),
        migrations.AddField(
            model_name='internalmigrationdata',
            name='request',
            field=models.ForeignKey(to='crams.Request', blank=True, null=True),
        ),
        migrations.AddField(
            model_name='internalmigrationdata',
            name='system',
            field=models.ForeignKey(to='crams.ProjectIDSystem'),
        ),
        migrations.AddField(
            model_name='grant',
            name='grant_type',
            field=models.ForeignKey(related_name='grants', to='crams.GrantType'),
        ),
        migrations.AddField(
            model_name='grant',
            name='project',
            field=models.ForeignKey(related_name='grants', to='crams.Project'),
        ),
        migrations.AddField(
            model_name='domain',
            name='for_code',
            field=models.ForeignKey(related_name='domains', to='crams.FORCode'),
        ),
        migrations.AddField(
            model_name='domain',
            name='project',
            field=models.ForeignKey(related_name='domains', to='crams.Project'),
        ),
        migrations.AddField(
            model_name='computerequestquestionresponse',
            name='question',
            field=models.ForeignKey(related_name='compute_question_responses', to='crams.Question'),
        ),
        migrations.AddField(
            model_name='computerequest',
            name='provision_details',
            field=models.OneToOneField(related_name='computerequest', to='crams.ProvisionDetails', blank=True, null=True),
        ),
        migrations.AddField(
            model_name='computerequest',
            name='request',
            field=models.ForeignKey(related_name='compute_requests', to='crams.Request'),
        ),
        migrations.AddField(
            model_name='computeproduct',
            name='funding_body',
            field=models.ForeignKey(related_name='computeproduct', to='crams.FundingBody'),
        ),
        migrations.AddField(
            model_name='computeproduct',
            name='provider',
            field=models.ForeignKey(related_name='computeproduct', to='crams.Provider'),
        ),
        migrations.AlterUniqueTogether(
            name='notificationtemplate',
            unique_together=set([('funding_body', 'request_status')]),
        ),
        migrations.RunSQL(load_crams_inital_data_from_sql()),
        migrations.RunSQL(load_forcode_data_from_sql()),
    ]
