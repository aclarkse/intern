# Copyright 2019 The Johns Hopkins University Applied Physics Laboratory
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from intern.service.dvid import DVIDService
from intern.resource.dvid.resource import *
import requests
import json
import ast

class ProjectService(DVIDService):
    """
        ProjectService for DVID service.
    """

    def __init__(self, base_url):
        """Constructor.

        Args:
            base_url (string): Base url to project service.

        """
        DVIDService.__init__(self)
        self.base_url = base_url

    def create(self, resource):
        """
            Creates a repository for the data to be placed in.
        Args:
            resource (intern.resource.dvid.DVIDResource): Data model object with attributes matching those of the resource.

        Returns:
            UUID (str): Randomly generated 32 character long UUID
        
        Raises:
            (HTTPError): On invalid request
        """

        if isinstance(resource, ExperimentResource):
            exp_name = resource.name
            r = requests.post("{}/api/repos".format(self.base_url),
                data = json.dumps({"Alias" : resource.UUID,
                    "Description" : exp_name}
                    )
            )
            r = str(r.content)
            UUID = ast.literal_eval(r.split("'")[0])["root"]
            return UUID

        if isinstance(resource, ChannelResource):
            exp_name = resource.exp_name
            chan_name = resource.name
            exp_create_resp = requests.post("{}/api/repos".format(self.base_url),
                data = json.dumps({"Alias" : resource.UUID,
                    "Description" : exp_name}
                    )
            )
            exp_create_resp_cont = str(exp_create_resp.content)
            if exp_create_resp.status_code != 200:
                raise requests.HTTPError(exp_create_resp.content)
            UUID = ast.literal_eval(exp_create_resp_cont.split("'")[0])["root"]

            chan_create_resp_cont = requests.post("{}/api/repo/{}/instance".format(self.base_url, UUID),
                data=json.dumps({"typename" : resource._type,
                    "dataname" : chan_name,
                    "versioned" : resource.version,
                    "sync": resource.sync
                }))

            if chan_create_resp_cont.status_code != 200:
                raise requests.HTTPError(chan_create_resp_cont.content)
            return UUID

    def get(self, resource):
        """Get attributes of the given resource.

        Args:
            resource (intern.resource.dvid.DVIDResource): Data model object with attributes matching those of the resource.

        Raises:
            (HTTPError): On invalid request
        """
        return resource.UUID, resource.exp_name

    def delete(self, resource):
        """
        Method to delete a project

        Args:
            resource (intern.resource.dvid.DVIDResource): Data model object with attributes matching those of the resource.

        Returns:
            (str) : HTTP Response

        Raises:
            (HTTPError): On invalid request
        """
        if isinstance(resource, ExperimentResource):
            del_resp = requests.delete("{}/api/repo/{}?imsure=true".format(self.base_url, resource.UUID))
            if del_resp.status_code != 200:
                raise requests.HTTPError(del_resp.content)
        
        if isinstance(resource, ChannelResource):
            del_resp = requests.delete("{}/api/repo/{}/{}?imsure=true".format(self.base_url, resource.UUID, resource.name))
            if del_resp.status_code != 200:
                raise requests.HTTPError(del_resp.content)
            
        return del_resp