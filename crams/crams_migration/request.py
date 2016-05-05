import datetime
import logging
from crams import models as crams_models
from rcallocation import models as nectar_models
from crams.lookup_dict import funding_node
from crams.crams_migration.question import create_request_question_response, \
    create_storage_request_question_response, create_compute_request_question_response

LOG = logging.getLogger(__name__)


# create new request
def create_request(alloc_request, crams_project):
    crams_request = crams_models.Request()
    crams_request.project = crams_project
    crams_request.start_date = alloc_request.start_date
    crams_request.end_date = alloc_request.end_date
    crams_request.approval_notes = alloc_request.status_explanation

    # reuse the same user who created project
    crams_request.created_by = crams_project.created_by
    crams_request.updated_by = crams_project.created_by

    # funding scheme - get the "NeCTAR National Merit"
    get_funding_scheme(alloc_request)
    funding_scheme = crams_models.FundingScheme.objects.get(funding_scheme="NeCTAR National Merit")
    crams_request.funding_scheme = funding_scheme

    # Check request project has a parent, if yes use parent project.request as request parent
    if crams_project.parent_project:
        crams_request.parent_request = crams_project.parent_project.requests.all()[0]

    # request status
    crams_request.request_status = get_request_status(alloc_request)

    crams_request.save()

    # set the timestamps from the crams_project, have to do this after creating request using update()
    created_datetime = datetime.datetime.combine(alloc_request.submit_date, datetime.time.min)
    crams_models.Request.objects.filter(pk=crams_request.id).update(creation_ts=created_datetime)
    crams_models.Request.objects.filter(pk=crams_request.id).update(last_modified_ts=alloc_request.modified_time)

    # create additional project question and responses
    create_request_question_response(crams_request, 'researchcase', alloc_request.use_case)
    create_request_question_response(crams_request, 'usagepattern', alloc_request.usage_patterns)
    create_request_question_response(crams_request, 'homerequirements', alloc_request.geographic_requirements)

    create_request_question_response(crams_request, 'ptconversion', alloc_request.convert_trial_project)
    create_request_question_response(crams_request, 'duration', alloc_request.estimated_project_duration)
    create_request_question_response(crams_request, 'homenode', alloc_request.allocation_home)
    create_request_question_response(crams_request, 'estimatedusers', alloc_request.estimated_number_users)

    create_request_question_response(crams_request, 'n_approver_email', alloc_request.approver_email)

    return crams_request


def get_funding_scheme(alloc_request):
    if alloc_request.funding_national_percent == 100:
        funding_scheme = crams_models.FundingScheme.objects.get(funding_scheme="NeCTAR National Merit")
    else:
        funding_scheme = crams_models.FundingScheme.objects.get(funding_scheme=funding_node[alloc_request.funding_node])

    return funding_scheme


# get the request status based on nectar_request condition/state
def get_request_status(alloc_request):
    """
    The crams status that is migrated across is determine by the conditions
    from the table below:
    _________________________________________________________________________
       status   |   tenant_uuid   |   parent_request_id   |   crams_status
    ------------+-----------------+-----------------------+------------------
          A     |      NULL       |         NULL          |         P
    ------------+-----------------+-----------------------+------------------
          A     |    NOT NULL     |         NULL          |         P
    ------------+-----------------+-----------------------+------------------
          A     |    NOT NULL     |       NOT NULL        |         P
    ------------+-----------------+-----------------------+------------------
          A     |      NULL       |       NOT NULL        |         A
    ------------+-----------------+-----------------------+------------------
    """
    if (alloc_request.status == 'A' and alloc_request.tenant_uuid is None and alloc_request.parent_request is None):
        request_status = crams_models.RequestStatus.objects.get(code="P")

    elif (alloc_request.status == 'A' and alloc_request.tenant_uuid is not None and alloc_request.parent_request is None):
        request_status = crams_models.RequestStatus.objects.get(code="P")

    elif (alloc_request.status == 'A' and alloc_request.tenant_uuid is not None and alloc_request.parent_request is not None):
        request_status = crams_models.RequestStatus.objects.get(code="P")

    elif (alloc_request.status == 'A' and alloc_request.tenant_uuid is None and alloc_request.parent_request is not None):
        request_status = crams_models.RequestStatus.objects.get(code="A")

    # for every status that is not 'A', retrieve the crams equivalent status
    elif alloc_request.status != 'A':
        request_status = crams_models.RequestStatus.objects.get(code=alloc_request.status)

    return request_status


# create provision details if the status is "Provisioned"
def create_provision_detail(alloc_request, crams_request):
    if crams_request.request_status.code == "P":
        provision_detail = crams_models.ProvisionDetails()

        provision_detail.status = "P"
        # same user who created request
        provision_detail.created_by = crams_request.created_by
        provision_detail.updated_by = crams_request.created_by
        # get provider, will always be NeCTAR
        provider = crams_models.Provider.objects.get(name="NeCTAR")
        provision_detail.provider = provider

        provision_detail.save()

        # set the timestamps from the crams_request, have to do this after creating request using update()
        # created_datetime = datetime.datetime.combine(alloc_request.submit_date, datetime.time.min)
        crams_models.ProvisionDetails.objects.filter(pk=provision_detail.id).update(creation_ts=alloc_request.modified_time)
        crams_models.ProvisionDetails.objects.filter(pk=provision_detail.id).update(last_modified_ts=alloc_request.modified_time)

        return provision_detail
    else:
        return None


# create compute products requests
def create_compute_product_request(alloc_request, crams_request):
    comp_req = crams_models.ComputeRequest()

    # set crams request
    comp_req.request = crams_request

    # set comp product - NeCTAR
    comp_prd = crams_models.ComputeProduct.objects.get(name='NeCTAR Compute')
    comp_req.compute_product = comp_prd

    # Provision details
    comp_req.provision_details = create_provision_detail(alloc_request, crams_request)

    # check if ProjectProvisionDetails has been recorded
    try:
        proj_prov_det = crams_models.ProjectProvisionDetails.objects.get(project=crams_request.project)
    except crams_models.ProjectProvisionDetails.DoesNotExist:
        if comp_req.provision_details:
            proj_prov_det = crams_models.ProjectProvisionDetails()
            proj_prov_det.project = crams_request.project
            proj_prov_det.provision_details = comp_req.provision_details

            proj_prov_det.save()

    # compute details
    comp_req.instances = alloc_request.instances
    comp_req.approved_instances = alloc_request.instance_quota
    comp_req.cores = alloc_request.cores
    comp_req.approved_cores = alloc_request.core_quota
    comp_req.core_hours = alloc_request.core_hours
    comp_req.approved_core_hours = alloc_request.core_hours

    comp_req.save()

    # compute questions
    create_compute_request_question_response(comp_req, 'n_primary_instance_type',
                                             alloc_request.primary_instance_type)


# create storage product requests
def create_storage_product_request(alloc_request, crams_request):
    # get all storage products for the allocation request
    nectar_quota_list = nectar_models.Quota.objects.filter(allocation=alloc_request)

    # create a new storage request for each quota obj from nectar
    for quota in nectar_quota_list:
        crams_stor_req = crams_models.StorageRequest()

        # set crams request
        crams_stor_req.request = crams_request

        # get storage product
        try:
            crams_stor_prd = crams_models.StorageProduct.objects.get(zone__name=quota.zone,
                                                                     storage_type__storage_type=quota.resource.capitalize())
            crams_stor_req.storage_product = crams_stor_prd
        except:
            LOG.error("Storage Product not found for: allocation.Id - " + str(quota.allocation_id) +
                      " type - " + str(quota.resource) + " and zone - " + str(quota.zone))
            continue

        # Provision details
        crams_stor_req.provision_details = create_provision_detail(alloc_request, crams_request)

        # check if ProjectProvisionDetails has been recorded
        try:
            proj_prov_det = crams_models.ProjectProvisionDetails.objects.get(project=crams_request.project)
        except crams_models.ProjectProvisionDetails.DoesNotExist:
            if crams_stor_req.provision_details:
                proj_prov_det = crams_models.ProjectProvisionDetails()
                proj_prov_det.project = crams_request.project
                proj_prov_det.provision_details = crams_stor_req.provision_details

                proj_prov_det.save()

        # storage details
        crams_stor_req.quota = quota.requested_quota
        crams_stor_req.approved_quota = quota.quota

        crams_stor_req.save()

        # save storage request questions
        if crams_stor_req.storage_product.storage_type.storage_type == 'Volume':
            create_storage_request_question_response(crams_stor_req,
                                                     'n_volume_storage_zone',
                                                     alloc_request.volume_zone)
        if crams_stor_req.storage_product.storage_type.storage_type == 'Object':
            create_storage_request_question_response(crams_stor_req,
                                                     'n_object_storage_zone',
                                                     alloc_request.object_storage_zone)
