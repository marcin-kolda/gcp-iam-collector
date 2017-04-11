import logging
import sys
from googleapiclient.discovery import build
from cache_service import CRMProjects

from oauth2client.client import GoogleCredentials

logging.basicConfig(
    format='%(asctime)s %(levelname)-5s %(filename)-12s %(message)s',
    level=logging.DEBUG, stream=sys.stdout)

credentials = GoogleCredentials.get_application_default()
crm_service = build('cloudresourcemanager', 'v1', credentials=credentials)


def list_projects():
    response = CRMProjects(crm_service).get()

    while response:
        for project in response['projects']:
            yield project

        if 'nextPageToken' in response:
            response = CRMProjects(crm_service).get(nextPageToken=response['nextPageToken'])
        else:
            response = None


if __name__ == '__main__':
    for counter, project_json in enumerate(list_projects()):
        logging.info("parsing project [{0}] projectId: {1}"
                     .format(counter, project_json['projectId']))
