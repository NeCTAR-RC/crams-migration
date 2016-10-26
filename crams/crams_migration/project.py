from django.db.models import Q
from django.db import connections
from rcportal_migration.settings import CRAMS_DB, DATABASES
from rcallocation import models as NectarModels
from crams import models as CramsModels
from crams.lookup_dict import grant_type_dict
from crams.crams_migration.request import create_request, create_compute_product_request, \
    create_storage_product_request
from crams.crams_migration.question import create_project_question_response
from crams.crams_migration.user import get_user, create_chief_contact
import datetime
import logging

LOG = logging.getLogger(__name__)

"""
 Reads django model objects from the Nectar rcallocation and migrate
 the data over across to crams database using the crams models mapping.
"""
# for error messages, append error msg to this and output the results in the end
user_errors = ''
user_count = 0
parent_errors = ''
parent_count = 0


# Migration function starting point, run this to start migration
def migrate():
    global user_errors, user_count, parent_errors, parent_count

    # get all allocation request where parent is None
    nectar_alloc_requests = NectarModels.AllocationRequest.objects.filter(parent_request_id=None)
    create_projects(nectar_alloc_requests)

    # get all allocation request where parent is not none
    nectar_parent_alloc_requests = NectarModels.AllocationRequest.objects.filter(~Q(parent_request_id=None))
    create_projects(nectar_parent_alloc_requests, child=True)

    # set the project seq id to start at the max id, only required for posgres
    if 'postgresql' in DATABASES[CRAMS_DB]:
        try:
            cursor = connections[CRAMS_DB].cursor()
            cursor.execute("SELECT setval('crams_project_id_seq', (SELECT MAX(id) FROM crams_project));")
        except Exception as ex:
            LOG.error("Failed to update project sequence id")
            LOG.error(str(ex))

    if parent_errors or user_errors:
        LOG.error("-----Migration completed with some errors-----" + user_errors + parent_errors)
        LOG.error("User error count: " + str(user_count))
        LOG.error("Parent error count: " + str(parent_count))
    else:
        LOG.info("-----Migration complete with no errors-----")


# creates projects from nectar allocation request list, if child == True then proceed to get/add parent to project
# only creates the project if user can be matched with the allocation request and if a child request has a parent
def create_projects(alloc_requests, child=False):
    global user_errors, user_count, parent_errors, parent_count

    for alloc_request in alloc_requests:
        # create a crams project
        crams_project = CramsModels.Project()
        crams_project.id = alloc_request.id
        crams_project.title = alloc_request.project_name
        crams_project.description = alloc_request.project_name

        if child:
            try:
                parent = CramsModels.Project.objects.get(pk=alloc_request.parent_request_id)
                crams_project.parent_project = parent
            except:
                # ERROR: Can not find parent, do not save this child project
                parent_errors = (parent_errors + '\n[Missing Parent]Could not find parent id ' +
                                 str(alloc_request.parent_request_id) + ' for this allocation id ' + str(alloc_request.id))
                if parent_errors:
                    LOG.debug('parent errors: {}'.format(parent_errors))

                parent_count = parent_count + 1

                if parent_count:
                    LOG.debug('parent count: {}'.format(parent_count))
                continue

        # try to get/create user from keystone user list
        user, contact = get_user(alloc_request.contact_email)

        if user:
            crams_project.created_by = user
            crams_project.updated_by = user
        else:
            # ERROR: Could not find user, do not save this project
            user_errors = (user_errors + '\n[Missing User]Could not find user ' +
                           alloc_request.contact_email + ' for this allocation id ' + str(alloc_request.id))
            if user_errors:
                LOG.debug('user errors: {}'.format(user_errors))

            user_count = user_count + 1
            if user_count:
                LOG.debug('user count: {}'.format(user_count))
            continue

        # no errors up to this point save project
        crams_project.save()

        # set the timestamps, have to do this after creating project using update()
        created_datetime = datetime.datetime.combine(alloc_request.submit_date, datetime.time.min)
        CramsModels.Project.objects.filter(pk=crams_project.id).update(creation_ts=created_datetime)
        CramsModels.Project.objects.filter(pk=crams_project.id).update(last_modified_ts=alloc_request.modified_time)

        # set the user contact to project with the role "Applicant"
        app_role = CramsModels.ContactRole.objects.get(name="Applicant")
        CramsModels.ProjectContact.objects.create(contact=contact,
                                                  contact_role=app_role,
                                                  project=crams_project)

        # create chief contact for project
        create_chief_contact(alloc_request, crams_project)

        # create additional project question and responses
        create_project_question_response(crams_project, 'nectarvls', alloc_request.nectar_support)
        create_project_question_response(crams_project, 'ncris', alloc_request.ncris_support)

        # create the projectID's
        create_projectids(alloc_request, crams_project)

        # create the domain for code
        create_domain(alloc_request, crams_project)

        # create project request
        crams_request = create_request(alloc_request, crams_project)

        # create supported institution
        create_supported_institution(alloc_request, crams_project)

        # create publication
        create_publication(alloc_request, crams_project)

        # create grant
        create_grant(alloc_request, crams_project)

        # create compute request
        create_compute_product_request(alloc_request, crams_request)

        # create storage request
        create_storage_product_request(alloc_request, crams_request)


# create project question response
# creates 4 kinds of project identifiers: tenant_name, tenant_uuid, created_by and DB_Id
def create_projectids(alloc_request, crams_project):
    # create projectID using tenant name from nectar request if available
    if alloc_request.tenant_name:
        tenant_name = CramsModels.ProjectIDSystem.objects.get(system='NeCTAR')
        CramsModels.ProjectID.objects.create(identifier=alloc_request.tenant_name,
                                             project=crams_project,
                                             system=tenant_name)

    # create projectID using tenant uuid from nectar request if available
    if alloc_request.tenant_uuid:
        uuid = CramsModels.ProjectIDSystem.objects.get(system='NeCTAR_UUID')
        CramsModels.ProjectID.objects.create(identifier=alloc_request.tenant_uuid,
                                             project=crams_project,
                                             system=uuid)

    # create projectID using created by from nectar request
    created_by = CramsModels.ProjectIDSystem.objects.get(system='NeCTAR_Created_By')
    CramsModels.ProjectID.objects.create(identifier=alloc_request.created_by,
                                         project=crams_project,
                                         system=created_by)

    # create projectID using table id from nectar request
    db_id = CramsModels.ProjectIDSystem.objects.get(system='NeCTAR_DB_Id')
    CramsModels.ProjectID.objects.create(identifier=alloc_request.id,
                                         project=crams_project,
                                         system=db_id)


# create SupportedInstitution
def create_supported_institution(alloc_request, crams_project):
    # get the institute from nectar rcportal db
    try:
        nectar_institute = NectarModels.Institution.objects.get(allocation=alloc_request)
        # create new crams supported institute
        crams_institute = CramsModels.SupportedInstitution()
        crams_institute.institution = nectar_institute.name
        crams_institute.project = crams_project

        crams_institute.save()
    except:
        pass


# create publication
def create_publication(alloc_request, crams_project):
    # get list of pubs for allocation request
    nectar_pub_list = NectarModels.Publication.objects.filter(allocation=alloc_request)

    # iterate through the list of pubs save one for each pub
    for nectar_pub in nectar_pub_list:
        # create new crams publication
        crams_pub = CramsModels.Publication()
        crams_pub.reference = nectar_pub.publication
        crams_pub.project = crams_project

        crams_pub.save()


# create grant
def create_grant(alloc_request, crams_project):
    def get_grant_type(type):
        # if unable to find mapping type return None
        try:
            return grant_type_dict[type]
        except:
            return None

    # get list of grant from allocation request
    nectar_grant_list = NectarModels.Grant.objects.filter(allocation=alloc_request)

    # iterate through the list of grants and save for each grant
    for nectar_grant in nectar_grant_list:
        # create new crams grant
        crams_grant = CramsModels.Grant()
        crams_grant.grant_id = nectar_grant.grant_id
        crams_grant.start_year = nectar_grant.first_year_funded
        crams_grant.total_funding = nectar_grant.total_funding

        # save grant type if found
        grant_type = get_grant_type(nectar_grant.grant_type)
        if grant_type:
            crams_grant.grant_type = CramsModels.GrantType.objects.get(description=grant_type)

        crams_grant.project = crams_project
        crams_grant.funding_body_and_scheme = nectar_grant.funding_body_scheme

        crams_grant.save()


# create new domain of forcodes
def create_domain(alloc_request, crams_project):
    # 1st domain mandatory but in some cases there are no for_codes recorded
    # if for_Code is null then don't migrate anything across
    if alloc_request.field_of_research_1:
        for_code = CramsModels.FORCode.objects.get(code=alloc_request.field_of_research_1)
        domain = CramsModels.Domain()
        domain.for_code = for_code
        domain.percentage = alloc_request.for_percentage_1
        domain.project = crams_project
        domain.save()

    # 2nd domain optional, create if exist
    if alloc_request.for_percentage_2 > 0:
        for_code = CramsModels.FORCode.objects.get(code=alloc_request.field_of_research_2)
        domain = CramsModels.Domain()
        domain.for_code = for_code
        domain.percentage = alloc_request.for_percentage_2
        domain.project = crams_project
        domain.save()

    # 3rd domain optional, create if exist
    if alloc_request.for_percentage_3 > 0:
        for_code = CramsModels.FORCode.objects.get(code=alloc_request.field_of_research_3)
        domain = CramsModels.Domain()
        domain.for_code = for_code
        domain.percentage = alloc_request.for_percentage_3
        domain.project = crams_project
        domain.save()
