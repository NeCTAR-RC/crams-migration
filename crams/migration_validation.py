import logging
import datetime
import csv

from django.db.models import Q
import simplejson

from rcallocation import models as nc
from crams import models as cm
from rcportal_migration.settings import BASE_DIR
from crams.lookup_dict import grant_type_dict

LOG = logging.getLogger(__name__)


class MigrationValidation:
    def __init__(self):
        self.missing_users = None
        json_file = open(
            BASE_DIR + '/keystone_users/missing_keystone_users.json')
        self.missing_users = simplejson.load(json_file)

        # load keystone user from csv file
        keystone_users_data = open(BASE_DIR + '/keystone_users/keystone-users.csv')
        self.keystone_users_list = list(csv.reader(keystone_users_data))

    def validate(self):
        print('migration validation ...')

        # get all allocation request where parent is None
        nectar_requests = nc.AllocationRequest.objects.filter(
            parent_request_id=None)
        # loop the nectar requests with parent_request is null
        for req in nectar_requests:
            project_migrated = self.validate_project(req)
            #
            # if True:
            #     sys.exit()
            nc_children_reqs = nc.AllocationRequest.objects.filter(
                parent_request_id=req.id)
            if nc_children_reqs:
                # loop the children request
                for nc_children_req in nc_children_reqs:
                    if project_migrated:
                        # here we only validate the child request
                        # if its parent request is already migrated
                        self.validate_project(nc_children_req)
                    else:
                        # otherwise we just log down the reason
                        LOG.error(
                            'Can not find migrated crams project for [nectar request id: {} - parent request id: {}]'.format(
                                nc_children_req.id, req.id))

    def validate_project(self, nc_request):
        project_migrated = False
        crams_projects = cm.Project.objects.filter(
            Q(project_ids__identifier=nc_request.id) & Q(
                project_ids__system__id=6)).distinct()

        if crams_projects:
            crams_project = crams_projects[0]
            self.compare_projects(nc_request, crams_project)
            project_migrated = True
        else:
            LOG.error(
                'Can not find migrated crams project for [nectar request id: {}]'.format(
                    nc_request.id))
            project_migrated = False
        return project_migrated

    def compare_projects(self, nc_request, crams_project):
        # compare project name
        nc_project_name = nc_request.project_name
        cm_project_name = crams_project.title
        if nc_project_name != cm_project_name:
            LOG.error(
                'project name is not matched, [nectar request id: {} '
                '- crams project id: {}]'.format(
                    nc_request.id, crams_project.id))

        # compare creation date
        nc_submit_date = nc_request.submit_date
        nc_created_time = datetime.datetime.combine(nc_submit_date,
                                                    datetime.time.min)
        cm_created_time = crams_project.creation_ts

        if nc_created_time != cm_created_time:
            LOG.error(
                'project creation date is not matched, [nectar request id: {} '
                '- crams project id: {}]'.format(
                    nc_request.id, crams_project.id))

        # compare modified date
        nc_modified_time = nc_request.modified_time
        cm_modified_time = crams_project.last_modified_ts
        if nc_modified_time != cm_modified_time:
            LOG.error(
                'project modified date is not matched, [nectar request id: {} '
                '- crams project id: {}]'.format(
                    nc_request.id, crams_project.id))

        # compare tenant_name tenant_uuid, allocationrequest.id and created_by
        cm_projectids = cm.ProjectID.objects.filter(
            project__id=crams_project.id)
        for projectid in cm_projectids:
            nc_db_id = nc_request.id
            nc_created_by = nc_request.created_by
            nc_tenant_name = nc_request.tenant_name
            nc_tenant_uuid = nc_request.tenant_uuid

            projectidsystem = projectid.system.system

            identifier = projectid.identifier

            if projectidsystem == 'NeCTAR':
                if nc_tenant_name and nc_tenant_name != identifier:
                    LOG.error(
                        'nectar tenant_name is not matched in crams ProjectId, [nectar request id: {}  - crams project id: {}]'.format(
                            nc_request.id, crams_project.id))

            if projectidsystem == 'NeCTAR_UUID':
                if nc_tenant_uuid and nc_tenant_uuid != identifier:
                    LOG.error(
                        'nectar tenant_uuid is not matched in crams ProjectId, [nectar request id: {}  - crams project id: {}]'.format(
                            nc_request.id, crams_project.id))

            if projectidsystem == 'NeCTAR_Created_By':
                if nc_created_by and nc_created_by != identifier:
                    LOG.error(
                        'nectar created_by is not matched in crams ProjectId, [nectar request id: {}  - crams project id: {}]'.format(
                            nc_request.id, crams_project.id))

            if projectidsystem == 'NeCTAR_DB_Id':
                if nc_db_id and nc_db_id != int(identifier):
                    LOG.error(
                        'nectar allocationrequest db id is not matched in crams ProjectId, [nectar request id: {}  - crams project id: {}]'.format(
                            nc_request.id, crams_project.id))

                    # print('{}'.format(projectid.identifier))

        self.compare_user(nc_request, crams_project)
        self.compare_chiefinvestigator(nc_request, crams_project)
        self.compare_forcode(nc_request, crams_project)
        self.compare_institution(nc_request, crams_project)
        self.compare_publication(nc_request, crams_project)
        self.compare_grant(nc_request, crams_project)
        self.compare_project_questions(nc_request, crams_project)
        self.compare_request(nc_request, crams_project)

    def find_keystone_user(self, email):
        try:
            keystone_user_dict = [x for x in self.keystone_users_list if x[1] == email][0]

            keystone_user = nc.KeystoneUser()
            keystone_user.uuid = keystone_user_dict[0]
            keystone_user.name = keystone_user_dict[1]

        except:
            keystone_user_dict = self.missing_users.get(email)

            if keystone_user_dict:
                keystone_user = nc.KeystoneUser()
                keystone_user.uuid = keystone_user_dict['uuid']
                keystone_user.name = keystone_user_dict['name']
                keystone_user.extra = keystone_user_dict['extra']
            else:
                keystone_user = None

        return keystone_user

    def compare_user(self, nc_request, cm_project):
        nc_contact_email = nc_request.contact_email

        keystone_user = self.find_keystone_user(nc_contact_email)
        # compare users
        if keystone_user:
            nc_user_uuid = keystone_user.uuid
            nc_user_email = keystone_user.name.lower()
            nc_username = keystone_user.name.lower()

            created_by_user = cm_project.created_by
            if created_by_user is None:
                LOG.error(
                    'Created by User is not created - {} for crams project [nectar request id: {}  - crams project id: {}]'.format(
                        nc_contact_email, nc_request.id, cm_project.id))
            else:
                cm_user_uuid = created_by_user.keystone_uuid
                cm_user_email = created_by_user.email.lower()
                cm_username = created_by_user.username.lower()

                if nc_user_uuid != cm_user_uuid:
                    LOG.error(
                        'User uuid is not matched - {} for crams project [nectar request id: {}  - crams project id: {}]'.format(
                            nc_contact_email, nc_request.id, cm_project.id))
                if nc_user_email != cm_user_email:
                    LOG.error(
                        'User email is not matched - {} for crams project [nectar request id: {}  - crams project id: {}]'.format(
                            nc_contact_email, nc_request.id, cm_project.id))
                if nc_username != cm_username:
                    LOG.error(
                        'User name is not matched - {} for crams project [nectar request id: {}  - crams project id: {}]'.format(
                            nc_contact_email, nc_request.id, cm_project.id))
            updated_by_user = cm_project.updated_by
            if updated_by_user is None:
                LOG.error(
                    'Updated by User is not created - {} for crams project [nectar request id: {}  - crams project id: {}]'.format(
                        nc_contact_email, nc_request.id, cm_project.id))
            else:
                if updated_by_user != created_by_user:
                    LOG.error(
                        'Updated_by User is not same as created_by User - {} for crams project [nectar request id: {}  - crams project id: {}]'.format(
                            nc_contact_email, nc_request.id, cm_project.id))

        else:
            LOG.error(
                'Can not find keystone user - {} for nectar request [nectar request id: {}  - crams project id: {}]'.format(
                    nc_contact_email, nc_request.id, cm_project.id))

        # compare the contacts
        project_contacts = cm.ProjectContact.objects.filter(
            Q(project__id=cm_project.id) & Q(contact_role__name='Applicant'))

        if project_contacts and keystone_user:
            crams_contact = project_contacts[0].contact
            nc_user_email = keystone_user.name.lower()
            cm_contact_email = crams_contact.email.lower()
            if nc_user_email != cm_contact_email:
                LOG.error(
                    'User contact email is not matched - {} for crams project [nectar request id: {}  - crams project id: {}]'.format(
                        nc_contact_email, nc_request.id, cm_project.id))
        else:
            LOG.error(
                'Can not find contact for crams project, [nectar request id: {} - crams project id: {}]'.format(
                    nc_request.id, cm_project.id))

    def compare_chiefinvestigator(self, nc_request, cm_project):
        nc_chiefs = nc.ChiefInvestigator.objects.filter(
            allocation__id=nc_request.id)
        if nc_chiefs:
            nc_chief = nc_chiefs[0]
            # nc_title = nc_chief.title
            # nc_given_name = nc_chief.given_name
            # nc_surname = nc_chief.surname
            nc_email = nc_chief.email.lower()
            # nc_institution = nc_chief.institution
            project_contacts = cm.ProjectContact.objects.filter(
                Q(project__id=cm_project.id) & Q(
                    contact_role__name='Chief Investigator'))
            if project_contacts:
                cm_chief = project_contacts[0]
                # cm_title = cm_chief.contact.title
                # cm_given_name = cm_chief.contact.given_name
                # cm_surname = cm_chief.contact.surname
                cm_email = cm_chief.contact.email.lower()
                # cm_institution = cm_chief.contact.organisation

                if nc_email != cm_email:
                    LOG.error(
                        'Chief investigator is not matched for crams project [nectar request id: {}  - crams project id: {}]'.format(
                            nc_request.id, cm_project.id))

            else:
                LOG.error(
                    'Chief investigator is not matched for crams project [nectar request id: {}  - crams project id: {}]'.format(
                        nc_request.id, cm_project.id))

    def compare_forcode(self, nc_request, cm_project):
        num_of_forcode = 0
        for_code1 = nc_request.field_of_research_1
        percent_for_code1 = nc_request.for_percentage_1
        if for_code1 and percent_for_code1 > 0:
            num_of_forcode += 1

        for_code2 = nc_request.field_of_research_2
        percent_for_code2 = nc_request.for_percentage_2
        if for_code2 and percent_for_code2 > 0:
            num_of_forcode += 1

        for_code3 = nc_request.field_of_research_3
        percent_for_code3 = nc_request.for_percentage_3

        if for_code3 and percent_for_code3 > 0:
            num_of_forcode += 1

        cm_domains = cm.Domain.objects.filter(project__id=cm_project.id)

        if num_of_forcode != len(cm_domains):
            LOG.error(
                'Migrated FOR codes are not matched for crams project [nectar request id: {}  - crams project id: {}]'.format(
                    nc_request.id, cm_project.id))
        else:
            for domain in cm_domains:
                matched_times = 0
                for_code = domain.for_code.code
                percent = domain.percentage

                if for_code1 and percent_for_code1 > 0:
                    if for_code == for_code1 and percent == percent_for_code1:
                        matched_times += 1
                if for_code2 and percent_for_code2 > 0:
                    if for_code == for_code2 and percent == percent_for_code2:
                        matched_times += 1
                if for_code3 and percent_for_code3 > 0:
                    if for_code == for_code3 and percent == percent_for_code3:
                        matched_times += 1
                if matched_times != 1:
                    LOG.error(
                        'Migrated FOR code: {} is not matched for crams project [nectar request id: {}  - crams project id: {}]'.format(
                            for_code, nc_request.id, cm_project.id))

    def compare_institution(self, nc_request, cm_project):
        nc_institutions = nc.Institution.objects.filter(
            allocation__id=nc_request.id)
        cm_institutions = cm.SupportedInstitution.objects.filter(
            project__id=cm_project.id)
        if nc_institutions is None and cm_institutions:
            LOG.error(
                'Supported institutions are not matched for crams project [nectar request id: {}  - crams project id: {}]'.format(
                    nc_request.id, cm_project.id))

        if nc_institutions and cm_institutions is None:
            LOG.error(
                'Supported institutions are not matched for crams project [nectar request id: {}  - crams project id: {}]'.format(
                    nc_request.id, cm_project.id))

        if nc_institutions and cm_institutions:
            if len(nc_institutions) != len(cm_institutions):
                LOG.error(
                    'Supported institutions are not matched for crams project [nectar request id: {}  - crams project id: {}]'.format(
                        nc_request.id, cm_project.id))

            for nc_ins in nc_institutions:
                nc_ins_name = nc_ins.name
                nc_ins_name_matched_times = 0
                for cm_ins in cm_institutions:
                    cm_ins_name = cm_ins.institution
                    if nc_ins_name == cm_ins_name:
                        nc_ins_name_matched_times += 1
                if nc_ins_name_matched_times != 1:
                    LOG.error(
                        'Migrated institution: {} is not matched for crams project [nectar request id: {}  - crams project id: {}]'.format(
                            nc_ins_name, nc_request.id, cm_project.id))

    def compare_publication(self, nc_request, cm_project):
        nc_publications = nc.Publication.objects.filter(
            allocation__id=nc_request.id)
        cm_publications = cm.Publication.objects.filter(
            project__id=cm_project.id)

        if nc_publications is None and cm_publications:
            LOG.error(
                'publications are not matched for crams project [nectar request id: {}  - crams project id: {}]'.format(
                    nc_request.id, cm_project.id))

        if nc_publications and cm_publications is None:
            LOG.error(
                'publications are not matched for crams project [nectar request id: {}  - crams project id: {}]'.format(
                    nc_request.id, cm_project.id))

        if nc_publications and cm_publications:
            if len(nc_publications) != len(cm_publications):
                LOG.error(
                    'publications are not matched for crams project [nectar request id: {}  - crams project id: {}]'.format(
                        nc_request.id, cm_project.id))

            for nc_pub in nc_publications:
                nc_publication = nc_pub.publication
                nc_pub_matched_times = 0
                for cm_pub in cm_publications:
                    cm_reference = cm_pub.reference
                    if nc_publication == cm_reference:
                        nc_pub_matched_times += 1
                if nc_pub_matched_times != 1:
                    LOG.error(
                        'Migrated publication: {} is not matched for crams project [nectar request id: {}  - crams project id: {}]'.format(
                            nc_publication, nc_request.id, cm_project.id))

    def compare_grant(self, nc_request, cm_project):
        nc_grants = nc.Grant.objects.filter(allocation__id=nc_request.id)
        cm_grants = cm.Grant.objects.filter(project__id=cm_project.id)
        if nc_grants is None and cm_grants:
            LOG.error(
                'Grants are not matched for crams project [nectar request id: {}  - crams project id: {}]'.format(
                    nc_request.id, cm_project.id))
        if nc_grants and cm_grants is None:
            LOG.error(
                'Grants are not matched for crams project [nectar request id: {}  - crams project id: {}]'.format(
                    nc_request.id, cm_project.id))

        if nc_grants and cm_grants:
            if len(nc_grants) != len(cm_grants):
                LOG.error(
                    'Grants are not matched for crams project [nectar request id: {}  - crams project id: {}]'.format(
                        nc_request.id, cm_project.id))

            for nc_grant in nc_grants:
                nc_grant_type_key = nc_grant.grant_type
                nc_grant_type = grant_type_dict.get(nc_grant_type_key)
                nc_fs = nc_grant.funding_body_scheme
                nc_grant_id = nc_grant.grant_id
                nc_first_year_funded = nc_grant.first_year_funded
                nc_total_funding = nc_grant.total_funding

                nc_grant_matched_times = 0

                for cm_grant in cm_grants:
                    cm_grant_type = cm_grant.grant_type.description
                    cm_fs = cm_grant.funding_body_and_scheme
                    cm_grant_id = cm_grant.grant_id
                    cm_first_year_funded = cm_grant.start_year
                    cm_total_funding = cm_grant.total_funding

                    if (nc_grant_type == cm_grant_type and nc_fs == cm_fs and nc_grant_id == cm_grant_id and
                                nc_first_year_funded == cm_first_year_funded and nc_total_funding == cm_total_funding):
                        nc_grant_matched_times += 1
                if nc_grant_matched_times != 1:
                    LOG.error(
                        'Migrated grant: {} is not matched for crams project [nectar request id: {}  - crams project id: {}]'.format(
                            nc_grant_type, nc_request.id, cm_project.id))

    def compare_project_questions(self, nc_request, cm_project):
        nc_chiefs = nc.ChiefInvestigator.objects.filter(
            allocation__id=nc_request.id)
        if nc_chiefs:
            nc_chief = nc_chiefs[0]
            nc_additional_researchers = nc_chief.additional_researchers

            if nc_additional_researchers:
                cm_question_resps = cm.ProjectQuestionResponse.objects.filter(
                    Q(question__key='additionalresearchers') & Q(
                        project__id=cm_project.id))
                if cm_question_resps:
                    cm_additional_researchers = cm_question_resps[
                        0].question_response
                    if nc_additional_researchers != cm_additional_researchers:
                        LOG.error(
                            'Additional researchers is not matched for crams project, [{} - {}] [nectar request id: {}  - '
                            'crams project id: {}]'.format(
                                nc_additional_researchers,
                                cm_additional_researchers, nc_request.id,
                                cm_project.id))
                else:
                    LOG.error(
                        'Additional researchers is not matched for crams project [nectar request id: {}  - crams project id: {}]'.format(
                            nc_request.id, cm_project.id))

        nc_nectar_support = nc_request.nectar_support
        nc_ncris_support = nc_request.ncris_support

        if nc_nectar_support:
            cm_question_resps = cm.ProjectQuestionResponse.objects.filter(
                Q(question__key='nectarvls') & Q(project__id=cm_project.id))
            if cm_question_resps:
                cm_nectar_support = cm_question_resps[0].question_response
                if nc_nectar_support != cm_nectar_support:
                    LOG.error(
                        'NeCTAR virtual Laboratories supporting is not matched for crams project [nectar request id: {}  - '
                        'crams project id: {}]'.format(
                            nc_request.id, cm_project.id))
            else:
                LOG.error(
                    'NeCTAR virtual Laboratories supporting is not matched for crams project [nectar request id: {}  - '
                    'crams project id: {}]'.format(
                        nc_request.id, cm_project.id))

        if nc_ncris_support:
            cm_question_resps = cm.ProjectQuestionResponse.objects.filter(
                Q(question__key='ncris') & Q(project__id=cm_project.id))
            if cm_question_resps:
                cm_ncris_support = cm_question_resps[0].question_response
                if nc_ncris_support != cm_ncris_support:
                    LOG.error(
                        'NCRIS capabilities supportingis not matched for crams project [nectar request id: {}  - crams project id: {}]'.format(
                            nc_request.id, cm_project.id))
            else:
                LOG.error(
                    'NCRIS capabilities supporting is not matched for crams project [nectar request id: {}  - crams project id: {}]'.format(
                        nc_request.id, cm_project.id))

    def compare_request(self, nc_request, cm_project):
        cm_request = cm.Request.objects.filter(
            project__id=cm_project.id).first()
        if cm_request is None:
            LOG.error(
                'Can not find migrated crams request for [nectar request id: {} - parent request id: {}]'.format(
                    nc_request.id, cm_project.id))
        else:
            nc_submit_date = nc_request.submit_date
            nc_created_time = datetime.datetime.combine(nc_submit_date,
                                                        datetime.time.min)
            nc_modified_time = nc_request.modified_time
            nc_start_date = nc_request.start_date
            nc_end_date = nc_request.end_date
            nc_approval_note = nc_request.status_explanation
            nc_status = self._gen_cm_request_status(nc_request)
            nc_parent_request = nc_request.parent_request

            created_by_user = cm_project.created_by
            cm_req_created_by_user = cm_request.created_by
            cm_req_updated_by_user = cm_request.updated_by
            cm_created_time = cm_request.creation_ts
            cm_modified_time = cm_request.last_modified_ts
            cm_start_date = cm_request.start_date
            cm_end_date = cm_request.end_date
            cm_approval_note = cm_request.approval_notes
            cm_req_status = cm_request.request_status
            cm_parent_request = cm_request.parent_request
            cm_funding_scheme = cm_request.funding_scheme
            if cm_funding_scheme is None or cm_funding_scheme.funding_scheme != 'NeCTAR National Merit':
                LOG.error(
                    'Funding scheme is not set properly, [nectar request id: {} - crams request id: {}]'.format(
                        nc_request.id, cm_request.id))

            if cm_req_created_by_user is None:
                LOG.error(
                    'Created_by_user is not created for crams request [nectar request id: {} - crams request id: {}]'.format(
                        nc_request.id, cm_request.id))
            else:
                if cm_req_created_by_user != created_by_user:
                    LOG.error(
                        'Created_by_user is not matched for crams request [nectar request id: {} - crams request id: {}]'.format(
                            nc_request.id, cm_request.id))

            if cm_req_updated_by_user is None:
                LOG.error(
                    'Updated_by_user is not created for crams request [nectar request id: {} - crams request id: {}]'.format(
                        nc_request.id, cm_request.id))
            else:
                if cm_req_updated_by_user != created_by_user:
                    LOG.error(
                        'Updated_by_user is not matched for crams request [nectar request id: {} - crams request id: {}]'.format(
                            nc_request.id, cm_request.id))

            if nc_created_time != cm_created_time:
                LOG.error(
                    'Created time is not matched for crams request [nectar request id: {} - crams request id: {}]'.format(
                        nc_request.id, cm_request.id))

            if nc_modified_time != cm_modified_time:
                LOG.error(
                    'Modified time is not matched for crams request [nectar request id: {} - crams request id: {}]'.format(
                        nc_request.id, cm_request.id))

            if nc_start_date != cm_start_date:
                LOG.error(
                    'Start date is not matched for crams request [nectar request id: {} - crams request id: {}]'.format(
                        nc_request.id, cm_request.id))

            if nc_end_date != cm_end_date:
                LOG.error(
                    'End date is not matched for crams request [nectar request id: {} - crams request id: {}]'.format(
                        nc_request.id, cm_request.id))

            if nc_approval_note and nc_approval_note != cm_approval_note:
                LOG.error(
                    'Approval is not matched for crams request [nectar request id: {} - crams request id: {}]'.format(
                        nc_request.id, cm_request.id))

            if nc_parent_request:
                if not cm_parent_request:
                    LOG.error(
                        'Parent request is not set for crams request [nectar request id: {} - crams request id: {}]'.format(
                            nc_request.id, cm_request.id))
            if nc_status is not None and nc_status != cm_req_status:
                LOG.error(
                    'Request status is not matched for crams request [nectar request id: {}, status: {} - crams request id: {}, status: {}]'.format(
                        nc_request.id, nc_status.code, cm_request.id,
                        cm_req_status.code))
            else:
                if cm_req_status.code == 'P':
                    proj_provs = cm.ProjectProvisionDetails.objects.filter(project__id=cm_project.id)
                    if proj_provs is not None:
                        if len(proj_provs) != 1:
                            LOG.error(
                                'More than one project provision details are created [nectar request id: {} - crams request id: {}, crams project id{}]'.format(
                                    nc_request.id, cm_request.id, cm_project.id))
                        else:
                            provision_status = proj_provs[0].provision_details.status
                            if provision_status != 'P':
                                    LOG.error('Project provision details status is not P,  [nectar request id: {} - crams request id: {}, '
                                              'crams project id{}]'.format(nc_request.id, cm_request.id, cm_project.id))
                    else:
                        LOG.error(
                            'No project provision details is migrated [nectar request id: {} - crams request id: {}, crams project id{}]'.format(
                                nc_request.id, cm_request.id, cm_project.id))

                            # compare the request question response
            self.compare_request_question_response(nc_request, cm_request)
            self.compare_compute_request(nc_request, cm_request)
            self.compare_storage_request(nc_request, cm_request)

    def compare_request_question_response(self, nc_request, cm_request):
        nc_use_case = nc_request.use_case
        nc_patterns = nc_request.usage_patterns
        nc_additional_location = nc_request.geographic_requirements
        nc_convert_trial = nc_request.convert_trial_project
        nc_duration = nc_request.estimated_project_duration
        nc_homenode = nc_request.allocation_home
        nc_estimated_users = nc_request.estimated_number_users
        nc_approver_email = nc_request.approver_email

        usecase_qresponse = cm.RequestQuestionResponse.objects.filter(
            Q(question__key='researchcase') & Q(
                request__id=cm_request.id)).first()
        if usecase_qresponse:
            cm_use_case = usecase_qresponse.question_response
            if nc_use_case is None:
                if cm_use_case != '':
                    LOG.error(
                        'Research use case is not set as empty for crams request, [nectar request id: {} - crams request id: {}]'.format(
                            nc_request.id, cm_request.id))
            else:
                if nc_use_case != cm_use_case:
                    LOG.error(
                        'Research use case is not matched for crams request, [nectar request id: {} - crams request id: {}]'.format(
                            nc_request.id, cm_request.id))
        else:
            LOG.error(
                'Research use case is not set for crams request, [nectar request id: {} - crams request id: {}]'.format(
                    nc_request.id, cm_request.id))

        patterns_qresponse = cm.RequestQuestionResponse.objects.filter(
            Q(question__key='usagepattern') & Q(
                request__id=cm_request.id)).first()
        if patterns_qresponse:
            cm_patterns = patterns_qresponse.question_response
            if nc_patterns is None:
                if cm_patterns != '':
                    LOG.error(
                        'Usage patterns is not set as empty for crams request, [nectar request id: {} - crams request id: {}]'.format(
                            nc_request.id, cm_request.id))
            else:
                if nc_patterns != cm_patterns:
                    LOG.error(
                        'Usage patterns is not matched for crams request, [nectar request id: {} - crams request id: {}]'.format(
                            nc_request.id, cm_request.id))
        else:
            LOG.error(
                'Usage patterns is not set for crams request, [nectar request id: {} - crams request id: {}]'.format(
                    nc_request.id, cm_request.id))

        additional_location_qresponse = cm.RequestQuestionResponse.objects.filter(
            Q(question__key='homerequirements') & Q(
                request__id=cm_request.id)).first()
        if additional_location_qresponse:
            cm_additional_location = additional_location_qresponse.question_response
            if nc_additional_location is None:
                if cm_additional_location != '':
                    LOG.error(
                        'Additional location requirements is not matched for crams request, [nectar request id: {} - crams request id: {}]'.format(
                            nc_request.id, cm_request.id))
            else:
                if nc_additional_location != cm_additional_location:
                    LOG.error(
                        'Additional location requirements is not matched for crams request, [nectar request id: {} - crams request id: {}]'.format(
                            nc_request.id, cm_request.id))
        else:
            LOG.error(
                'Additional location requirements is not set for crams request, [nectar request id: {} - crams request id: {}]'.format(
                    nc_request.id, cm_request.id))

        convert_trial_qresponse = cm.RequestQuestionResponse.objects.filter(
            Q(question__key='ptconversion') & Q(
                request__id=cm_request.id)).first()
        if convert_trial_qresponse:
            cm_convert_trial_ans = convert_trial_qresponse.question_response
            if cm_convert_trial_ans == 'True':
                cm_convert_trial = True
            else:
                cm_convert_trial = False

            if nc_convert_trial != cm_convert_trial:
                LOG.error(
                    'Convert trial is not matched for crams request, [nectar request id: {}, convert trial: {} - '
                    'crams request id: {}, convert trial: {}'.format(
                        nc_request.id, nc_convert_trial, cm_request.id,
                        cm_convert_trial))
        else:
            LOG.error(
                'Convert trial is not set for crams request, [nectar request id: {} - crams request id: {}]'.format(
                    nc_request.id, cm_request.id))

        duration_qresponse = cm.RequestQuestionResponse.objects.filter(
            Q(question__key='duration') & Q(request__id=cm_request.id)).first()
        if duration_qresponse:
            duration_ans = duration_qresponse.question_response
            cm_duration = int(duration_ans)
            if nc_duration != cm_duration:
                LOG.error(
                    'Estimated project duration is not matched for crams request, [nectar request id: {}, convert trial: {} - '
                    'crams request id: {}, convert trial: {}'.format(
                        nc_request.id, nc_duration, cm_request.id,
                        cm_duration))
        else:
            LOG.error(
                'Estimated project duration is not set for crams request, [nectar request id: {} - crams request id: {}]'.format(
                    nc_request.id, cm_request.id))

        homenode_qresponse = cm.RequestQuestionResponse.objects.filter(
            Q(question__key='homenode') & Q(request__id=cm_request.id)).first()
        if homenode_qresponse:
            cm_homenode = homenode_qresponse.question_response
            if nc_homenode is None:
                if cm_homenode != '':
                    LOG.error(
                        'Allocation home is not set as empty for crams request, [nectar request id: {} - crams request id: {}]'.format(
                            nc_request.id, cm_request.id))
            else:
                if nc_homenode != cm_homenode:
                    LOG.error(
                        'Allocation home is not matched for crams request, [nectar request id: {} - crams request id: {}]'.format(
                            nc_request.id, cm_request.id))
        else:
            LOG.error(
                'Allocation home is not set for crams request, [nectar request id: {} - crams request id: {}]'.format(
                    nc_request.id, cm_request.id))

        estimated_users_qresponse = cm.RequestQuestionResponse.objects.filter(
            Q(question__key='estimatedusers') & Q(
                request__id=cm_request.id)).first()
        if estimated_users_qresponse:
            estimated_users_ans = estimated_users_qresponse.question_response
            cm_estimated_users = int(estimated_users_ans)
            if nc_estimated_users != cm_estimated_users:
                LOG.error(
                    'Estimated users is not matched for crams request, [nectar request id: {}, convert trial: {} - '
                    'crams request id: {}, convert trial: {}'.format(
                        nc_request.id, nc_estimated_users, cm_request.id,
                        cm_estimated_users))
        else:
            LOG.error(
                'Estimated users is not set for crams request, [nectar request id: {} - crams request id: {}]'.format(
                    nc_request.id, cm_request.id))

        approver_email_qresponse = cm.RequestQuestionResponse.objects.filter(
            Q(question__key='n_approver_email') & Q(
                request__id=cm_request.id)).first()
        if approver_email_qresponse:
            cm_approver_email = approver_email_qresponse.question_response
            if nc_approver_email is None:
                if cm_approver_email != '':
                    LOG.error(
                        'Approver email is not set as empty for crams request, [nectar request id: {} - crams request id: {}]'.format(
                            nc_request.id, cm_request.id))
            else:
                if nc_approver_email != cm_approver_email:
                    LOG.error(
                        'Approver email is not matched for crams request, [nectar request id: {} - crams request id: {}]'.format(
                            nc_request.id, cm_request.id))
        else:
            LOG.error(
                'Approver email is not set for crams request, [nectar request id: {} - crams request id: {}]'.format(
                    nc_request.id, cm_request.id))

    def _gen_cm_request_status(self, nc_request):
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
        request_status = None
        if (nc_request.status == 'A' and nc_request.tenant_uuid is None and nc_request.parent_request is None):
            request_status = cm.RequestStatus.objects.get(code="P")

        elif (nc_request.status == 'A' and nc_request.tenant_uuid is not None and nc_request.parent_request is None):
            request_status = cm.RequestStatus.objects.get(code="P")

        elif (nc_request.status == 'A' and nc_request.tenant_uuid is not None and nc_request.parent_request is not None):
            request_status = cm.RequestStatus.objects.get(code="P")

        elif (nc_request.status == 'A' and nc_request.tenant_uuid is None and nc_request.parent_request is not None):
            request_status = cm.RequestStatus.objects.get(code="A")
        else:
            request_status = cm.RequestStatus.objects.get(code=nc_request.status)

        return request_status

    def compare_compute_request(self, nc_request, cm_request):
        nc_cores = nc_request.cores
        nc_core_hours = nc_request.core_hours
        nc_instances = nc_request.instances
        nc_approved_cores = nc_request.core_quota
        nc_approved_core_hours = nc_request.core_hours
        nc_approved_instances = nc_request.instance_quota

        cm_compute_request = cm.ComputeRequest.objects.filter(
            request__id=cm_request.id).first()

        if cm_compute_request is None:
            LOG.error(
                'Crams compute request is not set for crams request, [nectar request id: {} - crams request id: {}]'.format(
                    nc_request.id, cm_request.id))
        else:
            cm_cores = cm_compute_request.cores
            cm_core_hours = cm_compute_request.core_hours
            cm_instances = cm_compute_request.instances
            cm_approved_cores = cm_compute_request.approved_cores
            cm_approved_core_hours = cm_compute_request.approved_core_hours
            cm_approved_instances = cm_compute_request.approved_instances

            if nc_cores != cm_cores:
                LOG.error(
                    'Compute cores is not matched for crams compute request, [{} - {}] [nectar request id: {} - '
                    'crams compute request id: {} and request id: {}]'.format(
                        nc_cores, cm_cores, cm_compute_request.id,
                        cm_request.id))

            if nc_core_hours != cm_core_hours:
                LOG.error(
                    'Compute core hours is not matched for crams compute request, [{} - {}] [nectar request id: {} - '
                    'crams compute request id: {} and request id: {}]'.format(
                        nc_core_hours, cm_core_hours, cm_compute_request.id,
                        cm_request.id))

            if nc_instances != cm_instances:
                LOG.error(
                    'Compute instances is not matched for crams compute request, [{} - {}] [nectar request id: {} - '
                    'crams compute request id: {} and request id: {}]'.format(
                        nc_instances, cm_instances, cm_compute_request.id,
                        cm_request.id))

            if nc_approved_cores != cm_approved_cores:
                LOG.error(
                    'Compute approved cores is not matched for crams compute request, [{} - {}] [nectar request id: {} - '
                    'crams compute request id: {} and request id: {}]'.format(
                        nc_approved_cores, cm_approved_cores,
                        cm_compute_request.id, cm_request.id))

            if nc_approved_core_hours != cm_approved_core_hours:
                LOG.error(
                    'Compute approved core hours is not matched for crams compute request, [{} - {}] [nectar request id: {} - '
                    'crams compute request id: {} and request id: {}]'.format(
                        nc_approved_core_hours, cm_approved_core_hours,
                        cm_compute_request.id, cm_request.id))

            if nc_approved_instances != cm_approved_instances:
                LOG.error(
                    'Compute approved instances is not matched for crams compute request, [{} - {}] [nectar request id: {} - '
                    'crams compute request id: {} and request id: {}]'.format(
                        nc_approved_instances, cm_approved_instances,
                        cm_compute_request.id, cm_request.id))

            compute_product = cm_compute_request.compute_product
            compute_product_name = compute_product.name
            if compute_product_name != 'NeCTAR Compute':
                LOG.error(
                    'Crams compute request compute product name - {} is not set properly for crams request, [nectar request id: {} - '
                    'crams request id: {}]'.format(
                        compute_product_name, nc_request.id, cm_request.id))

            self.compare_compute_request_question(nc_request,
                                                  cm_compute_request,
                                                  cm_request)

            if cm_request.request_status.code == 'P':
                self.compare_compute_request_provision(nc_request,
                                                       cm_compute_request,
                                                       cm_request)

    def compare_compute_request_question(self, nc_request, cm_compute_request,
                                         cm_request):
        nc_primary_instance_type = nc_request.primary_instance_type
        if nc_primary_instance_type is not None and nc_primary_instance_type != ' ':
            cm_compute_qresponse = cm.ComputeRequestQuestionResponse.objects.filter(
                Q(question__key='n_primary_instance_type') & Q(
                    compute_request__id=cm_compute_request.id)).first()
            if cm_compute_qresponse is None:
                LOG.error(
                    'Crams compute request question primary instance type is not set for crams comput request, [nectar request id: {} - '
                    'crams compute request id: {} and request id: {}]'.format(
                        nc_request.id, cm_compute_request.id, cm_request.id,
                        cm_request.id))
            else:
                cm_primary_instance_type = cm_compute_qresponse.question_response
                if nc_primary_instance_type != cm_primary_instance_type:
                    LOG.error(
                        'Crams compute request question primary instance type is not matched for crams comput request, [nectar request id: {} - '
                        'crams compute request id: {} and request id: {}]'.format(
                            nc_request.id, cm_compute_request.id,
                            cm_request.id))

    def compare_compute_request_provision(self, nc_request, cm_compute_request,
                                          cm_request):
        cm_compute_provision_details = cm_compute_request.provision_details
        if cm_compute_provision_details is None:
            LOG.error(
                'The compute provision details is not set for crams compute request, [nectar request id: {} - '
                'crams compute request id: {} and request id: {}]'.format(
                    nc_request.id, cm_compute_request.id,
                    cm_request.id))

        else:
            provision_status = cm_compute_provision_details.status
            if provision_status != 'P':
                LOG.error(
                    'The compute provision details status is not set properly for crams compute request, '
                    'provision_details id: {} - [nectar request id: {} - '
                    'crams compute request id: {} and request id: {}]'.format(
                        cm_compute_provision_details.id, nc_request.id,
                        cm_compute_request.id, cm_request.id))
            provider_name = cm_compute_provision_details.provider.name
            if provider_name != 'NeCTAR':
                LOG.error(
                    'The compute provision details provider is not set properly for crams compute request, provision_details id: {}, '
                    'provider name: {} - [nectar request id: {} - '
                    'crams compute request id: {} and request id: {}]'.format(
                        cm_compute_provision_details.id,
                        cm_compute_provision_details.provider.name,
                        nc_request.id, cm_compute_request.id,
                        cm_request.id))

            created_time = cm_compute_provision_details.creation_ts
            modified_time = cm_compute_provision_details.last_modified_ts
            req_modified_time = cm_request.last_modified_ts
            if created_time != req_modified_time:
                LOG.error(
                    'The compute provision details created time is not set properly for crams compute request, '
                    'provision_details id: {} - [nectar request id: {} - '
                    'crams compute request id: {} and request id: {}]'.format(
                        cm_compute_provision_details.id, nc_request.id,
                        cm_compute_request.id, cm_request.id))
            if modified_time != req_modified_time:
                LOG.error(
                    'The compute provision details last modified time is not set properly for '
                    'crams compute request, provision_details id: {} - [nectar request id: {} - '
                    'crams compute request id: {} and request id: {}]'.format(
                        cm_compute_provision_details.id, nc_request.id,
                        cm_compute_request.id, cm_request.id))

    def compare_storage_request(self, nc_request, cm_request):
        nc_quotas = nc.Quota.objects.filter(allocation__id=nc_request.id)

        if nc_quotas:
            for nc_quota in nc_quotas:
                nc_resource = nc_quota.resource
                storage_type = nc_resource.capitalize()
                nc_zone = nc_quota.zone
                nc_requested_quota = nc_quota.requested_quota
                nc_approved_quota = nc_quota.quota
                crams_storage_prd = cm.StorageProduct.objects.get(
                    zone__name=nc_zone,
                    storage_type__storage_type=storage_type)
                cm_storage_request = cm.StorageRequest.objects.filter(
                    Q(request__id=cm_request.id) & Q(
                        storage_product__zone__name=nc_zone) & Q(
                        storage_product__storage_type__storage_type=storage_type)).first()
                if cm_storage_request is None:
                    LOG.error(
                        'Crams storage request is not set for crams request, [nectar request id: {} - crams request id: {}]'.format(
                            nc_request.id, cm_request.id))
                else:
                    cm_sp = cm_storage_request.storage_product
                    if cm_sp != crams_storage_prd:
                        LOG.error(
                            'Storage product is not matched for crams storage request, [nectar request id: {} - '
                            'crams storage request id: {} and request id: {}]'.format(
                                nc_request.id, cm_storage_request.id,
                                cm_request.id))

                    cm_quota = cm_storage_request.quota
                    cm_approved_quota = cm_storage_request.approved_quota
                    if nc_requested_quota != cm_quota:
                        LOG.error(
                            'Crams storage request quota is not matched for crams storage request, [{} - {}] [nectar request id: {} - '
                            'crams storage request id: {} and request id: {}]'.format(
                                nc_requested_quota, cm_quota, nc_request.id,
                                cm_storage_request.id, cm_request.id))
                    if nc_approved_quota != cm_approved_quota:
                        LOG.error(
                            'Crams storage request approved quota is not matched for crams storage request, [{} - {}] [nectar request id: {} - '
                            'crams storage request id: {} and request id: {}]'.format(
                                nc_approved_quota, cm_approved_quota,
                                nc_request.id, cm_storage_request.id,
                                cm_request.id))
                    # compare the storage request questions
                    self.compare_storage_request_question(nc_request,
                                                          cm_storage_request,
                                                          cm_request)
                    # compate the storage request provisions
                    if cm_request.request_status.code == 'P':
                        self.compare_storage_request_provision(nc_request,
                                                       cm_storage_request,
                                                       cm_request)

    def compare_storage_request_question(self, nc_request, cm_storage_request,
                                         cm_request):
        nc_volume_zone = nc_request.volume_zone
        nc_object_zone = nc_request.object_storage_zone
        cm_storage_type = cm_storage_request.storage_product.storage_type.storage_type
        if cm_storage_type == 'Volume' and nc_volume_zone:
            cm_vszone_qresponse = cm.StorageRequestQuestionResponse.objects.filter(
                Q(question__key='n_volume_storage_zone') & Q(
                    storage_request__id=cm_storage_request.id)).first()
            if cm_vszone_qresponse is None:
                LOG.error(
                    'Storage volume zone question response is not set for crams storage request, [nectar request id: {} - '
                    'crams storage request id: {} and request id: {}]'.format(
                        nc_request.id, cm_storage_request.id, cm_request.id,
                        cm_request.id))
            else:
                cm_volume_zone = cm_vszone_qresponse.question_response
                if nc_volume_zone != cm_volume_zone:
                    LOG.error(
                        'Storage volume zone question response is not matched for crams storage request, [nectar request id: {} - '
                        'crams storage request id: {} and request id: {}]'.format(
                            nc_request.id, cm_storage_request.id,
                            cm_request.id))

        if cm_storage_type == 'Object' and nc_object_zone:
            cm_oszone_qresponse = cm.StorageRequestQuestionResponse.objects.filter(
                Q(question__key='n_object_storage_zone') & Q(
                    storage_request__id=cm_storage_request.id)).first()
            if cm_oszone_qresponse is None:
                LOG.error(
                    'Object zone question response is not set for crams storage request, [nectar request id: {} - '
                    'crams storage request id: {} and request id: {}]'.format(
                        nc_request.id, cm_storage_request.id, cm_request.id,
                        cm_request.id))
            else:
                cm_object_zone = cm_oszone_qresponse.question_response
                if nc_object_zone != cm_object_zone:
                    LOG.error(
                        'Object zone question response is not matched for crams storage request, [nectar request id: {} - '
                        'crams storage request id: {} and request id: {}]'.format(
                            nc_request.id, cm_storage_request.id,
                            cm_request.id))

    def compare_storage_request_provision(self, nc_request, cm_storage_request,
                                          cm_request):

        cm_storage_provision_details = cm_storage_request.provision_details
        if cm_storage_provision_details is None:
            LOG.error(
                'The stroage provision details is not set for crams stroage request, [nectar request id: {} - '
                'crams stroage request id: {} and request id: {}]'.format(
                    nc_request.id, cm_storage_request.id,
                    cm_request.id))

        else:
            provision_status = cm_storage_provision_details.status
            if provision_status != 'P':
                LOG.error(
                    'The stroage provision details status is not set properly for crams stroage request, '
                    'provision_details id: {} - [nectar request id: {} - '
                    'crams stroage request id: {} and request id: {}]'.format(
                        cm_storage_provision_details.id, nc_request.id,
                        cm_storage_request.id, cm_request.id))
            provider_name = cm_storage_provision_details.provider.name
            if provider_name != 'NeCTAR':
                LOG.error(
                    'The stroage provision details provider is not set properly for crams stroage request, '
                    'provision_details id: {}, provider name: {} - [nectar request id: {} - '
                    'crams stroage request id: {} and request id: {}]'.format(
                        cm_storage_provision_details.id,
                        cm_storage_provision_details.provider.name,
                        nc_request.id, cm_storage_request.id,
                        cm_request.id))

            created_time = cm_storage_provision_details.creation_ts
            modified_time = cm_storage_provision_details.last_modified_ts
            req_modified_time = cm_request.last_modified_ts
            if created_time != req_modified_time:
                LOG.error(
                    'The stroage provision details created time is not set properly for crams stroage request, '
                    'provision_details id: {} - [nectar request id: {} - '
                    'crams stroage request id: {} and request id: {}]'.format(
                        cm_storage_provision_details.id, nc_request.id,
                        cm_storage_request.id, cm_request.id))
            if modified_time != req_modified_time:
                LOG.error(
                    'The stroage provision details last modified time is not set properly for crams stroage request, '
                    'provision_details id: {} - [nectar request id: {} - '
                    'crams stroage request id: {} and request id: {}]'.format(
                        cm_storage_provision_details.id, nc_request.id,
                        cm_storage_request.id, cm_request.id))
