import csv

from rcallocation import models as nc
from rcportal_migration.settings import BASE_DIR


class AllocRequest:
    def __init__(self, database_id, status, created_by, project_name, tenant_uuid):
        self.database_id = database_id
        self.status = status
        self.created_by = created_by
        self.project_name = project_name
        self.tenant_uuid = tenant_uuid

    def __str__(self):
        return '{}, {}, {}, {}, {}'.format(self.database_id,
                                           self.status,
                                           self.created_by,
                                           self.project_name,
                                           self.tenant_uuid)


class MissUserAllocation:
    def __init__(self, contact_email, alloc_requests=None):
        self.contact_email = contact_email
        self.alloc_requests = []
        if alloc_requests:
            self.alloc_requests = alloc_requests

    def add_request(self, missing_user_req):
        self.alloc_requests.append(missing_user_req)


class FindMissingKeystoneUsersRequest:
    def find(self):
        print('found missing keystone user requests ...')

        # get all allocation requests
        nectar_requests = nc.AllocationRequest.objects.all()
        total_not_found_keystone_user = 0
        missing_user_allocs = dict()

        for req in nectar_requests:
            contact_email = req.contact_email
            keystone_user = nc.KeystoneUser.objects.filter(name=contact_email)
            if not keystone_user:
                missing_user_alloc = missing_user_allocs.get(contact_email)
                if not missing_user_alloc:
                    missing_user_alloc = MissUserAllocation(contact_email)

                alloc_req = AllocRequest(req.id,
                                         req.status,
                                         req.created_by,
                                         req.project_name,
                                         req.tenant_uuid)
                missing_user_alloc.add_request(alloc_req)
                missing_user_allocs[contact_email] = missing_user_alloc

                total_not_found_keystone_user += 1
        csv_file = open(BASE_DIR + '/missing_keystone_users/user_not_found_requests.csv', 'w', newline='')
        csv_file_writer = csv.writer(csv_file, delimiter='\t', lineterminator='\n')

        csv_file_writer.writerow(['contact_email', 'id', 'status', 'created_by', 'tenant_uuid', 'project_name'])
        for k, v in missing_user_allocs.items():
            csv_file_writer.writerow([k, '', '', '', '', ''])
            alloc_requests = v.alloc_requests
            for req in alloc_requests:
                print(req)
                csv_file_writer.writerow(['', req.database_id, req.status, req.created_by, req.tenant_uuid, req.project_name])
        csv_file.close()

        print('total not found keystone users: {}'.format(total_not_found_keystone_user))
