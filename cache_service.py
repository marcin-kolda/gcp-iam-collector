import os.path
import json


class JsonCacheService(object):
    def __init__(self, service):
        self.service = service

    def get(self, **kwargs):
        cached_file = self._get_filename(**kwargs)
        if os.path.isfile(cached_file):
            with open(cached_file) as data_file:
                return json.load(data_file)
        response = self._get_data(**kwargs)
        if not os.path.exists(os.path.dirname(cached_file)):
            os.makedirs(os.path.dirname(cached_file))
        with open(cached_file, 'w') as data_file:
            json.dump(response, data_file)

        return response

    def _get_filename(self, **kwargs):
        raise NotImplementedError()

    def _get_data(self, **kwargs):
        raise NotImplementedError()


class CRMProjects(JsonCacheService):
    def _get_filename(self, **kwargs):
        return "cache/projects/projects_{0}.json".format(
            kwargs.get('nextPageToken', ''))

    def _get_data(self, **kwargs):
        return self.service.projects().list(
            pageSize=10,
            pageToken=kwargs.get('nextPageToken', None)).execute()


class CRMProjectIam(JsonCacheService):
    def _get_filename(self, **kwargs):
        return "cache/%s/iam.json" % (kwargs['project_id'])

    def _get_data(self, **kwargs):
        return self.service.projects().getIamPolicy(
            resource=kwargs['project_id'], body={}).execute()


class ServiceAccountService(JsonCacheService):
    def _get_filename(self, **kwargs):
        return "cache/serviceAccounts/{0}_{1}.json" \
            .format(kwargs['project_id'], kwargs.get('nextPageToken', ''))

    def _get_data(self, **kwargs):
        return self.service.projects().serviceAccounts().list(
            name='projects/' + kwargs['project_id'],
            pageToken=kwargs.get('nextPageToken', None)).execute()


class ServiceAccountKeyService(JsonCacheService):
    def _get_filename(self, **kwargs):
        return "cache/serviceAccountsKeys/{0}.json".format(kwargs['email'])

    def _get_data(self, **kwargs):
        return self.service.projects().serviceAccounts().keys().list(
            name='projects/-/serviceAccounts/' + kwargs['email'],
            keyTypes='USER_MANAGED').execute()


class GCSBuckets(JsonCacheService):
    def _get_filename(self, **kwargs):
        return "cache/{0}/buckets_{1}.json"\
            .format(kwargs['project_id'], kwargs.get('pageToken', ''))

    def _get_data(self, **kwargs):
        return self.service.buckets().list(
            project=kwargs['project_id'],
            pageToken=kwargs.get('pageToken', '')).execute()


class GCSBucketACL(JsonCacheService):
    def _get_filename(self, **kwargs):
        return "cache/buckets/gcs_acl_{0}.json".format(kwargs['bucket_id'])

    def _get_data(self, **kwargs):
        return self.service.bucketAccessControls().list(
            bucket=kwargs['bucket_id']).execute()


class BQDataset(JsonCacheService):
    def _get_filename(self, **kwargs):
        return "cache/{0}/datasets/{1}.json".format(
            kwargs['project_id'], kwargs['dataset_id'])

    def _get_data(self, **kwargs):
        return self.service.datasets().get(projectId=kwargs['project_id'],
                                           datasetId=kwargs[
                                               'dataset_id']).execute()


class BQDatasets(JsonCacheService):
    def _get_filename(self, **kwargs):
        return "cache/{0}/datasets_{1}.json" \
            .format(kwargs['project_id'], kwargs.get('pageToken', ''))

    def _get_data(self, **kwargs):
        return self.service.datasets().list(
            projectId=kwargs['project_id'],
            pageToken=kwargs.get('pageToken', '')).execute()
