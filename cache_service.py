import os.path
import json


class JsonCacheService(object):
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
    def __init__(self, crm_service):
        self.crm_service = crm_service

    def _get_filename(self, **kwargs):
        return "cache/projects/projects_{0}.json".format(kwargs.get('nextPageToken', ''))

    def _get_data(self, **kwargs):
        return self.crm_service.projects().list(
            pageSize=10,
            pageToken=kwargs.get('nextPageToken', None)) .execute()


class CRMProjectIam(JsonCacheService):
    def __init__(self, crm_service):
        self.crm_service = crm_service

    def _get_filename(self, **kwargs):
        return "cache/%s/iam.json" % (kwargs['project_id'])

    def _get_data(self, **kwargs):
        return self.crm_service.projects().getIamPolicy(
            resource=kwargs['project_id'], body={}).execute()
