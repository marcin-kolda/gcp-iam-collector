import logging
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from cache_service import CRMProjects, ServiceAccountService, \
    ServiceAccountKeyService

from oauth2client.client import GoogleCredentials


class GcpIamIterator:
    def __init__(self):
        credentials = GoogleCredentials.get_application_default()
        self.crm_service = CRMProjects(build('cloudresourcemanager', 'v1',
                                             credentials=credentials))
        google_iam_service = build('iam', 'v1', credentials=credentials)
        self.sa_service = ServiceAccountService(google_iam_service)
        self.sak_service = ServiceAccountKeyService(google_iam_service)

    def list_projects(self):
        response = self.crm_service.get()

        while response:
            for project in response['projects']:
                yield project

            if 'nextPageToken' in response:
                response = self.crm_service.get(
                    nextPageToken=response['nextPageToken'])
            else:
                response = None

    def list_service_accounts(self, project_id):
        try:
            response = self.sa_service.get(project_id=project_id)
        except HttpError as e:
            if e.resp.status == 404:
                logging.info("404 received for project_id: {0}"
                             .format(project_id))
                return
            elif e.resp.status == 403:
                logging.warning("403 received for project_id: {0}"
                                .format(project_id))
                return
            else:
                raise e

        while response:
            for account in response['accounts']:
                yield account

            if 'nextPageToken' in response:
                response = self.sa_service \
                    .get(project_id=project_id,
                         nextPageToken=response['nextPageToken'])
            else:
                response = None

    def list_service_account_keys(self, email):
        response = self.sak_service.get(email=email)

        for key in response['keys']:
            yield key
