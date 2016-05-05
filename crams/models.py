from django.db import models
from account.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from rest_framework.authtoken.models import Token

import datetime

class CramsToken(Token):
    ks_roles = models.TextField(null=True, blank=True)

    class Meta:
        app_label='crams'

class CramsCommon(models.Model):
    creation_ts = models.DateTimeField(
        auto_now_add=True,
        editable=False
    )
    last_modified_ts = models.DateTimeField(
        auto_now=True,
        editable=False
    )
    created_by = models.ForeignKey(User, related_name="%(class)s_created_by", blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name="%(class)s_updated_by", blank=True, null=True)

    class Meta:
        abstract = True
        app_label='crams'

class UserEvents(CramsCommon):
    event_message = models.TextField()

    class Meta:
        app_label='crams'


class ContactRole(models.Model):
    name = models.CharField(
        max_length=100, unique=True
    )

    class Meta:
        app_label='crams'

    def __str__(self):
        return '{}'.format(self.name)


class Contact(models.Model):
    title = models.CharField(
        max_length=50, blank=True, null=True
    )

    given_name = models.CharField(
        max_length=200, blank=True, null=True
    )

    surname = models.CharField(
        max_length=200, blank=True, null=True
    )

    email = models.EmailField()

    phone = models.CharField(
        max_length=50, blank=True, null=True
    )

    organisation = models.CharField(
        max_length=200, blank=True, null=True
    )

    class Meta:
        app_label='crams'

    def __str__(self):
        return '{0} {1} {2} {3}'.format(self.id, self.title, self.given_name, self.surname)


class Provider(CramsCommon):
    name = models.CharField(max_length=200, unique=False)
    crams_user = models.OneToOneField(User, blank=True, null=True)
    start_date = models.DateField(auto_now_add=True, editable=False)
    active = models.BooleanField(default=True)
    description = models.TextField(null=True, blank=True)

    @classmethod
    def isProvider(cls, userObj):
        if isinstance(userObj, User):
            if userObj.is_active:
                return hasattr(userObj, 'provider')
            raise Exception('User is not an active Provider')
        raise Exception('User object expected got {}'.format(repr(userObj)))

    def getStatusStr(self):
        if not self.active:
            return 'inActive'
        return 'current'

    class Meta:
        app_label='crams'

    def __str__(self):
        return '{}'.format(self.name)


class ProvisionDetails(CramsCommon):
    SENT = 'S'
    PROVISIONED = 'P'
    PROVISION_EXTEND = 'X'
    FAILED = 'F'
    STATUS_CHOICES = (
        (SENT, 'Sent'), (PROVISIONED, 'Provisioned'), (FAILED, 'Failed'), (PROVISION_EXTEND, 'Extend'),
    )
    status =  models.CharField(max_length=1, choices=STATUS_CHOICES, default=SENT)
    provider = models.ForeignKey(Provider, related_name='provisioned_requests')
    message = models.TextField(blank=True, null=True)

    class Meta:
        app_label='crams'

    def __str__(self):
        return '{}. {} : {}'.format(self.id, self.status, self.message)


class ProvisionableItem(models.Model):
    provision_details = models.OneToOneField(ProvisionDetails, blank=True, null=True, related_name='%(class)s')

    class Meta:
        abstract = True
        app_label='crams'

    def getProvider(self):
        raise NotImplementedError('Get Provider not implemented for abstract Product Request model')


class ProjectIDSystem(models.Model):
    system = models.CharField(
        max_length=100
    )

    class Meta:
        app_label='crams'

    def __str__(self):
        return '{}'.format(self.system)


class FundingBody(models.Model):
    name = models.CharField(
        max_length=200
    )

    email = models.EmailField()

    class Meta:
        app_label='crams'

    def __str__(self):
        return '{} - {}'.format(self.name, self.email)


class FundingScheme(models.Model):
    funding_scheme = models.CharField(
        max_length=200
    )

    funding_body = models.ForeignKey(FundingBody, related_name='funding_schemes')

    class Meta:
        app_label='crams'

    def __str__(self):
        return '{} {}'.format(self.funding_body.name, self.funding_scheme)


class Project(CramsCommon):
    # for project versioning, if parent_project is null which means it's a latest project request
    parent_project = models.ForeignKey('Project', null=True, blank=True)

    title = models.CharField(
        max_length=255
    )

    description = models.CharField(
        max_length=255
    )

    notes = models.TextField(
        null=True,
        blank=True,
        max_length=1024
    )

    class Meta:
        app_label='crams'

    def __str__(self):
        if self.parent_project:
            return '{}.{} - (Parent) {}'.format(self.id, self.title, self.parent_project.id)
        else :
            return '{}.{}'.format(self.id, self.title)


class ProjectContact(models.Model):
    project = models.ForeignKey(Project, related_name='project_contacts')
    contact = models.ForeignKey(Contact, related_name='project_contacts')
    contact_role = models.ForeignKey(ContactRole, related_name='project_contacts')

    class Meta:
        app_label='crams'

class ProjectProvisionDetails(models.Model):
    project = models.ForeignKey(Project, related_name='linked_provisiondetails')
    provision_details = models.ForeignKey(ProvisionDetails, related_name='linked_projects')

    class Meta:
        app_label='crams'

class ProjectID(models.Model):
    identifier = models.CharField(max_length=64)

    project = models.ForeignKey(Project, related_name='project_ids')

    system = models.ForeignKey(ProjectIDSystem, related_name='project_ids')

    def getProvider(self):
        if self.provision_details:
            return self.provision_details.provider
        return None

    class Meta:
        app_label='crams'

    def __str__(self):
        return '{} {}'.format(self.identifier, self.project)


class RequestStatus(models.Model):
    code = models.CharField(
        max_length=50
    )

    status = models.CharField(
        max_length=100
    )

    class Meta:
        app_label='crams'

    def __str__(self):
        return '{} {} {}'.format(self.id, self.code, self.status)


class Request(CramsCommon):
    # For versioning
    parent_request = models.ForeignKey('Request', null=True, blank=True, related_name='history')

    project = models.ForeignKey(Project, related_name='requests')

    request_status = models.ForeignKey(RequestStatus, related_name='requests')

    funding_scheme = models.ForeignKey(FundingScheme, related_name='requests')

    start_date = models.DateField(
        default=datetime.date.today
    )
    end_date = models.DateField()

    approval_notes = models.TextField(
        null=True,
        blank=True,
        max_length=1024
    )

    class Meta:
        app_label='crams'

    def __str__(self):
        return '{}.{}'.format(self.id, self.project.title)

class ProductCommon(models.Model):
    name = models.CharField( max_length=200 )

    funding_body = models.ForeignKey(FundingBody, related_name='%(class)s')

    provider = models.ForeignKey(Provider, related_name='%(class)s')

    class Meta:
        abstract = True
        app_label='crams'

    def __str__(self):
        return '{} {}'.format(self.id, self.name)

class ComputeProduct(ProductCommon):
    pass


class ComputeRequest(ProvisionableItem):
    instances = models.IntegerField(
        default=2,
        validators=[MinValueValidator(1)]
    )

    approved_instances = models.IntegerField(
        default=2,
        validators=[MinValueValidator(1)]
    )

    cores = models.IntegerField(
        default=2,
        validators=[MinValueValidator(1)]
    )

    approved_cores = models.IntegerField(
        default=2,
        validators=[MinValueValidator(1)]
    )

    core_hours = models.IntegerField(
        default=744,
        validators=[MinValueValidator(1)]
    )

    approved_core_hours = models.IntegerField(
        default=744,
        validators=[MinValueValidator(1)]
    )

    compute_product = models.ForeignKey(ComputeProduct, related_name='compute_requests')

    request = models.ForeignKey(Request, related_name='compute_requests')

    def getProvider(self):
        return self.compute_product.provider

    class Meta:
        app_label='crams'

    def __str__(self):
        return '{}/{}: {} {} {}'.format(self.id, self.request.id, self.instances, self.cores, self.core_hours)


class FORCode(models.Model):
    code = models.CharField(
        max_length=50
    )

    description = models.CharField(
        max_length=200
    )

    class Meta:
        app_label='crams'

    def __str__(self):
        return '{} {}'.format(self.code, self.description)


class Domain(models.Model):
    percentage = models.FloatField(
        default=0.0
    )

    project = models.ForeignKey(Project, related_name='domains')

    for_code = models.ForeignKey(FORCode, related_name='domains')

    class Meta:
        app_label='crams'

    def __str__(self):
        return '{} {} {}'.format(self.project.title, self.for_code.code, self.percentage)


class SupportedInstitution(models.Model):
    institution = models.CharField(
        max_length=200
    )

    project = models.ForeignKey(Project, related_name='institutions')

    class Meta:
        app_label='crams'

    def __str__(self):
        return '{}'.format(self.institution)


class Publication(models.Model):
    reference = models.CharField(
        max_length=255
    )

    project = models.ForeignKey(Project, related_name='publications')

    class Meta:
        app_label='crams'

    def __str__(self):
        return '{}'.format(self.reference)


class GrantType(models.Model):
    description = models.CharField(
        max_length=200
    )

    class Meta:
        app_label='crams'

    def __str__(self):
        return '{} {}'.format(self.id, self.description)


class Grant(models.Model):
    project = models.ForeignKey(Project, related_name='grants')

    grant_type = models.ForeignKey(GrantType, related_name='grants')

    funding_body_and_scheme = models.CharField(
        blank=False,
        max_length=200
    )

    grant_id = models.CharField(
        blank=True,
        max_length=200
    )

    start_year = models.IntegerField(
        blank=False,
        default=datetime.datetime.now().year,
        validators=[MinValueValidator(1970), MaxValueValidator(3000)],
        error_messages={
            'min_value': 'Please input a year between 1970 ~ 3000',
            'max_value': 'Please input a year between 1970 ~ 3000'}
    )

    total_funding = models.FloatField(
        blank=True,
        default=0.0
    )

    class Meta:
        app_label='crams'

    def __str__(self):
        return '{} {} {}'.format(self.grant_type, self.funding_body, self.start_year)


class StorageType(models.Model):
    storage_type = models.CharField(
        max_length=100
    )

    class Meta:
        app_label='crams'

    def __str__(self):
        return '{}'.format(self.storage_type)

class Zone(models.Model):
    name = models.CharField(max_length=64)
    description = models.TextField()

    class Meta:
        app_label='crams'

    def __str__(self):
        return '{}'.format(self.name)


class StorageProduct(ProductCommon):
    zone = models.ForeignKey(Zone, related_name='storage_products', null=True, blank=True)

    storage_type = models.ForeignKey(StorageType, related_name='storage_products')

    class Meta:
        app_label='crams'

    def __str__(self):
        return '{} - {}'.format(self.name, self.provider)


class StorageRequest(ProvisionableItem):
    quota = models.FloatField(
        default=0.0
    )

    approved_quota = models.FloatField(
        default=0.0
    )

    storage_product = models.ForeignKey(StorageProduct, related_name='storage_requests')

    request = models.ForeignKey(Request, related_name='storage_requests')

    def getProvider(self):
        return self.storage_product.provider

    class Meta:
        app_label='crams'

    def __str__(self):
        return '{}/{}: {} {}'.format(self.id, self.request.id, self.storage_product.name, self.quota)


class Question(models.Model):
    key = models.CharField(
        max_length=50
    )

    question_type = models.CharField(
        max_length=200
    )

    question = models.CharField(
        max_length=200
    )

    class Meta:
        app_label='crams'

    def __str__(self):
        return '{} {} {}'.format(self.key, self.question_type, self.question)


class ComputeRequestQuestionResponse(models.Model):
    question_response = models.TextField(
        max_length=1024,
        blank=True
    )

    question = models.ForeignKey(Question, related_name='compute_question_responses')

    compute_request = models.ForeignKey(ComputeRequest, related_name='compute_question_responses')

    class Meta:
        app_label='crams'


class StorageRequestQuestionResponse(models.Model):
    question_response = models.TextField(
        max_length=1024,
        blank=True
    )

    question = models.ForeignKey(Question, related_name='storage_question_responses')

    storage_request = models.ForeignKey(StorageRequest, related_name='storage_question_responses')

    class Meta:
        app_label='crams'



class ProjectQuestionResponse(models.Model):
    question_response = models.TextField(
        max_length=1024,
        blank=True

    )

    question = models.ForeignKey(Question, related_name='project_question_responses')

    project = models.ForeignKey(Project, related_name='project_question_responses')

    class Meta:
        app_label='crams'


class RequestQuestionResponse(models.Model):
    question_response = models.TextField(
        max_length=1024,
        blank=True
    )

    question = models.ForeignKey(Question, related_name='request_question_responses')

    request = models.ForeignKey(Request, related_name='request_question_responses')

    class Meta:
        app_label='crams'


class Duration(models.Model):
    duration = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)]
    )
    duration_label = models.CharField(
        max_length=50
    )

    class Meta:
        app_label='crams'

    def __str__(self):
        return '{} {}'.format(self.duration, self.duration_label)


class AllocationHome(models.Model):
    code = models.CharField(
        max_length=50
    )
    description = models.CharField(
        max_length=200
    )

    class Meta:
        app_label='crams'

    def __str__(self):
        return '{} {} {}'.format(self.id, self.code, self.description)
