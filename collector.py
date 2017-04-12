import logging
import sys
import csv

from gcp_iam_iterator import GcpIamIterator

logging.basicConfig(
    format='%(asctime)s %(levelname)-5s %(filename)-12s %(message)s',
    level=logging.DEBUG, stream=sys.stdout)


def dump_projects(iam_iterator):
    with open('projects.csv', 'wb') as csvfile:
        writer = csv.writer(csvfile)
        for counter, project in enumerate(iam_iterator.list_projects()):
            project_id = project['projectId']
            logging.info("parsing project [{0}] projectId: {1}"
                         .format(counter, project_id))
            writer.writerow([project_id, project['projectNumber'],
                             project['createTime'], project['name']])


def dump_service_accounts(iam_iterator):
    with open('serviceAccounts.csv', 'wb') as csvfile:
        writer = csv.writer(csvfile)
        for counter, project in enumerate(iam_iterator.list_projects()):
            project_id = project['projectId']
            logging.info("parsing project [{0}] projectId: {1}"
                         .format(counter, project_id))
            for account in iam_iterator.list_service_accounts(project_id):
                email = account['email']
                for sa_key in iam_iterator.list_service_account_keys(email):
                    writer.writerow(
                        [project_id, email, account.get('displayName', ''),
                         sa_key['validAfterTime'],
                         sa_key['validBeforeTime'],
                         sa_key['name'].split('/')[5]])


if __name__ == '__main__':
    iam_iterator = GcpIamIterator()
    dump_projects(iam_iterator)
    dump_service_accounts(iam_iterator)
