# Copyright 2018 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Firebase Remote Config Management module.

This module enables management of Remote config in Firebase projects.
"""

import requests

import firebase_admin
from firebase_admin import _http_client
from firebase_admin import _utils


_REMOTE_CONFIG_MANAGEMENT_ATTRIBUTE = '_remote_config_management'


def _get_remote_config_management_service(app):
    return _utils.get_app_service(app, _REMOTE_CONFIG_MANAGEMENT_ATTRIBUTE, _RemoteConfigManagementService)


def remote_config(app=None):
    return _get_remote_config_management_service(app).get_remote_config()


class _RemoteConfigManagementService:
    """Provides methods for interacting with the Firebase Remote Config Service."""

    BASE_URL = 'https://firebaseremoteconfig.googleapis.com'
    MAXIMUM_LIST_APPS_PAGE_SIZE = 100
    MAXIMUM_POLLING_ATTEMPTS = 8
    POLL_BASE_WAIT_TIME_SECONDS = 0.5
    POLL_EXPONENTIAL_BACKOFF_FACTOR = 1.5

    REMOTE_CONFIG_RESOURCE_NAME = 'remoteConfig'

    def __init__(self, app):
        project_id = app.project_id
        if not project_id:
            raise ValueError(
                'Project ID is required to access the Firebase Project Management Service. Either '
                'set the projectId option, or use service account credentials. Alternatively, set '
                'the GOOGLE_CLOUD_PROJECT environment variable.')
        self._project_id = project_id
        version_header = 'Python/Admin/{0}'.format(firebase_admin.__version__)
        timeout = app.options.get('httpTimeout', _http_client.DEFAULT_TIMEOUT_SECONDS)
        self._client = _http_client.JsonHttpClient(
            credential=app.credential.get_credential(),
            base_url=_RemoteConfigManagementService.BASE_URL,
            headers={'X-Client-Version': version_header},
            timeout=timeout)

    def get_remote_config(self):
        path = '/v1/projects/{0}/remoteConfig'.format(self._project_id)
        response = self._make_request('get', path)
        return response

    def _make_request(self, method, url, json=None):
        body, _ = self._body_and_response(method, url, json)
        return body

    def _body_and_response(self, method, url, json=None):
        try:
            return self._client.body_and_response(method=method, url=url, json=json)
        except requests.exceptions.RequestException as error:
            raise _utils.handle_platform_error_from_requests(error)