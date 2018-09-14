"""
Store adapters to read/write data to from/to mongodb using pymongo.
"""
import pymongo

from twitcher.store.base import AccessTokenStore
from twitcher.datatype import AccessToken
from twitcher.exceptions import AccessTokenNotFound

import logging
LOGGER = logging.getLogger(__name__)


class MongodbStore(object):
    """
    Base class extended by all concrete store adapters.
    """

    def __init__(self, collection):
        self.collection = collection


class MongodbTokenStore(AccessTokenStore, MongodbStore):
    def save_token(self, access_token):
        self.collection.insert_one(access_token)

    def delete_token(self, token):
        self.collection.delete_one({'token': token})

    def fetch_by_token(self, token):
        token = self.collection.find_one({'token': token})
        if not token:
            raise AccessTokenNotFound
        return AccessToken(token)

    def clear_tokens(self):
        self.collection.drop()


from twitcher.store.base import ServiceStore
from twitcher.datatype import Service
from twitcher.exceptions import ServiceRegistrationError, ServiceNotFound
from twitcher import namesgenerator
from twitcher.utils import baseurl


class MongodbServiceStore(ServiceStore, MongodbStore):
    """
    Registry for OWS services. Uses mongodb to store service url and attributes.
    """

    def save_service(self, service, overwrite=True, request=None):
        """
        Stores an OWS service in mongodb.
        """

        service_url = baseurl(service.url)
        # check if service is already registered
        if self.collection.count({'url': service_url}) > 0:
            if overwrite:
                self.collection.delete_one({'url': service_url})
            else:
                raise ServiceRegistrationError("service url already registered.")

        name = namesgenerator.get_sane_name(service.name)
        if not name:
            name = namesgenerator.get_random_name()
            if self.collection.count({'name': name}) > 0:
                name = namesgenerator.get_random_name(retry=True)
        if self.collection.count({'name': name}) > 0:
            if overwrite:
                self.collection.delete_one({'name': name})
            else:
                raise Exception("service name already registered.")
        self.collection.insert_one(Service(
            url=service_url,
            name=name,
            type=service.type,
            public=service.public,
            auth=service.auth))
        return self.fetch_by_url(url=service_url, request=request)

    def delete_service(self, name, request=None):
        """
        Removes service from mongodb storage.
        """
        self.collection.delete_one({'name': name})
        return True

    def list_services(self, request=None):
        """
        Lists all services in mongodb storage.
        """
        my_services = []
        for service in self.collection.find().sort('name', pymongo.ASCENDING):
            my_services.append(Service(service))
        return my_services

    def fetch_by_name(self, name, request=None):
        """
        Gets service for given ``name`` from mongodb storage.
        """
        service = self.collection.find_one({'name': name})
        if not service:
            raise ServiceNotFound
        return Service(service)

    def fetch_by_url(self, url, request=None):
        """
        Gets service for given ``url`` from mongodb storage.
        """
        service = self.collection.find_one({'url': baseurl(url)})
        if not service:
            raise ServiceNotFound
        return Service(service)

    def clear_services(self, request=None):
        """
        Removes all OWS services from mongodb storage.
        """
        self.collection.drop()
        return True


from twitcher.store.base import JobStore
from twitcher.datatype import Job
from twitcher.exceptions import JobRegistrationError, JobNotFound, JobUpdateError
from twitcher.wps_restapi.sort import *
from twitcher.wps_restapi.status import *
from pyramid.security import authenticated_userid
from pymongo import ASCENDING, DESCENDING
from datetime import datetime


class MongodbJobStore(JobStore, MongodbStore):
    """
    Registry for OWS service process jobs tracking. Uses mongodb to store job attributes.
    """

    def save_job(self, task_id, process, service=None, is_workflow=False, user_id=None, async=True, custom_tags=[]):
        """
        Stores a job in mongodb.
        """
        try:
            tags = ['dev']
            tags.extend(custom_tags)
            if is_workflow:
                tags.append('workflow')
            else:
                tags.append('single')
            if async:
                tags.append('async')
            else:
                tags.append('sync')
            new_job = Job({
                'task_id': task_id,
                'user_id': user_id,
                'service': service,     # provider identifier (WPS service)
                'process': process,     # process identifier (WPS request)
                'status': STATUS_ACCEPTED,
                'is_workflow': is_workflow,
                'created': datetime.now(),
                'tags': tags,
            })
            self.collection.insert_one(new_job)
            job = self.fetch_by_id(job_id=task_id)
            if job is None:
                raise JobRegistrationError("Failed to retrieve registered job.")
            return job
        except JobRegistrationError:
            raise
        except Exception as ex:
            raise JobRegistrationError("Error occurred during job registration: {}".format(repr(ex)))

    def update_job(self, job):
        """
        Updates a job parameters in mongodb storage.
        :param job: instance of ``twitcher.datatype.Job``.
        """
        try:
            result = self.collection.update_one({'task_id': job.task_id}, {'$set': job.params})
            if result.acknowledged and result.modified_count == 1:
                return self.fetch_by_id(job.task_id)
        except Exception as ex:
            raise JobUpdateError("Error occurred during job update: {}".format(repr(ex)))
        raise JobUpdateError("Failed to update specified job: {}".format(str(job)))

    def delete_job(self, job_id, request=None):
        """
        Removes job from mongodb storage.
        """
        self.collection.delete_one({'task_id': job_id})
        return True

    def fetch_by_id(self, job_id, request=None):
        """
        Gets job for given ``job_id`` from mongodb storage.
        """
        job = self.collection.find_one({'task_id': job_id})
        if not job:
            raise JobNotFound("Could not find job matching: {}".format(job_id))
        return Job(job)

    def list_jobs(self, request=None):
        """
        Lists all jobs in mongodb storage.
        """
        jobs = []
        for job in self.collection.find().sort('task_id', ASCENDING):
            jobs.append(Job(job))
        return jobs

    def find_jobs(self, request, page=0, limit=10, process=None, service=None,
                  tags=None, access=None, status=None, sort=None):
        """
        Finds all jobs in mongodb storage matching search filters.
        """
        search_filters = {}
        if access == 'public':
            search_filters['tags'] = 'public'
        elif access == 'private':
            search_filters['tags'] = {'$ne': 'public'}
            search_filters['user_id'] = authenticated_userid(request)
        elif access == 'all' and request.has_permission('admin'):
            pass
        else:
            if tags is not None:
                search_filters['tags'] = {'$all': tags}
            search_filters['user_id'] = authenticated_userid(request)

        if status in status_categories.keys():
            search_filters['status'] = {'$in': status_categories[status]}
        elif status:
            search_filters['status'] = status

        if process is not None:
            search_filters['process'] = process

        if service is not None:
            search_filters['service'] = service

        if sort is None:
            sort = SORT_CREATED
        elif sort == SORT_USER:
            sort = 'user_id'

        sort_order = DESCENDING if sort == SORT_FINISHED or sort == SORT_CREATED else ASCENDING
        sort_criteria = [(sort, sort_order)]
        found = self.collection.find(search_filters)
        count = found.count()
        items = [Job(item) for item in list(found.skip(page * limit).limit(limit).sort(sort_criteria))]
        return items, count

    def clear_jobs(self, request=None):
        """
        Removes all jobs from mongodb storage.
        """
        self.collection.drop()
        return True
