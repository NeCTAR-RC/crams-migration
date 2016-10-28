from rcportal_migration.settings import BASE_DIR
from account.models import User
from rcallocation import models as nectar_models
from crams import models as crams_models
from crams.crams_migration.question import create_project_question_response
import csv
import simplejson
import logging

LOG = logging.getLogger(__name__)

# user mapping of missing keystone users
try:
    json_data = open(BASE_DIR + '/keystone_users/missing_keystone_users.json')
    ks_user_mapping_dict = simplejson.load(json_data)
except:   
    ks_user_mapping_dict = None

# load keystone user from csv file
try:
    keystone_users_data = open(BASE_DIR + '/keystone_users/keystone-users.csv')
    keystone_users_list = list(csv.reader(keystone_users_data))
except:
    keystone_users_list = None


# Gets a user and contact object from crams, if not found then a new
# user and contact will be created.
def get_user(email):
    # first check if user already exist
    try:
        user = User.objects.get(email=email)
        contact = crams_models.Contact.objects.get(email=email)

        # return user if already exist
        return user, contact

    # create the user from keystone users
    except User.DoesNotExist:
        # look up user in keystone
        try:
            keystone_user = [x for x in keystone_users_list if x[1] == email][0]
            return create_user(keystone_user[1], keystone_user[0])

        except IndexError:
            # Look in '../../keystone_users/missing_keystone_users.json'
            # to try and map a user keystone email to the allocation contact_email
            try:
                # try and create a user from the mapping email details
                mapped = ks_user_mapping_dict[email]

                # check if user exist already in crams
                try:
                    user = crams_models.User.objects.get(email=mapped['name'])
                    contact = crams_models.Contact.objects.get(email=mapped['name'])

                    return user, contact

                # create user
                except User.DoesNotExist:
                    return create_user(mapped["name"], mapped["uuid"])

            except:
                # finally if no mapping found then no user will be created
                return None, None

    except Exception as ex:
        LOG.error('ERROR: Method _get_user() failed: ' + str(ex))


# creates a new user with email, keystone uuid and also creates a new
# contact using the email.
def create_user(email, ks_uuid):
    # user doesn't exist try to create a new user
    user = User.objects.create(username=email.lower(),
                               email=email.lower(),
                               keystone_uuid=ks_uuid,
                               is_active=True)

    # get contact if exist and reuse contact if not create new contact
    try:
        contact = crams_models.Contact.objects.get(email=email)
    except:
        contact = crams_models.Contact.objects.create(email=email)

    return user, contact


# create a chief contact and linking it to a crams project
def create_chief_contact(alloc_request, crams_project):
    # get chief investigator
    try:
        nectar_ci = nectar_models.ChiefInvestigator.objects.get(allocation=alloc_request)

        try:
            # check crams if ci contact already exist
            crams_contact = crams_models.Contact.objects.get(email=nectar_ci.email)
        except:
            # if no contact found, create new contact
            crams_contact = crams_models.Contact()

        # if successful in get, the contact was first created as a user so won't have any
        # other details except for the email, in that case we copy the ci details across
        crams_contact.title = nectar_ci.title
        crams_contact.given_name = nectar_ci.given_name
        crams_contact.surname = nectar_ci.surname
        crams_contact.email = nectar_ci.email.lower()
        crams_contact.organisation = nectar_ci.institution

        crams_contact.save()

        # get chief contact role
        role = crams_models.ContactRole.objects.get(name='Chief Investigator')

        # create project contact - links contact with ci role and crams project
        crams_prj_cnt = crams_models.ProjectContact()
        crams_prj_cnt.contact = crams_contact
        crams_prj_cnt.project = crams_project
        crams_prj_cnt.contact_role = role
        crams_prj_cnt.save()

        # add additional researchers if available to project question
        if nectar_ci.additional_researchers:
            create_project_question_response(crams_project, 'additionalresearchers',
                                             nectar_ci.additional_researchers)
    except:
        # Do nothing, nectar allocation request has no chief investigator
        pass
