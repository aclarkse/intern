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


class MetadataService(DVIDService):
    """
        MetadataService for DVID service.
    """

    def __init__(self, base_url):
        """Constructor.

        Attributes:
            base_url (string): Base url to project service.

        Raises:
            (KeyError): if given invalid version.
        """
        DVIDService.__init__(self)
        self.base_url = base_url

    def get_info(self, resource):
        """
            Returns JSON for just the repository with given root UUID.  The UUID string can be
            shortened as long as it is uniquely identifiable across the managed repositories.

            Args:
                UUID (string): UUID of the DVID repository (str)

            Returns:
                string: History information of the repository

            Raises:
                (HTTPError): on invalid HTTP request.
        """

        response = requests.get("{}/api/repo/{}/info".format(self.base_url, resource.UUID))
        if response.status_code != 200:
            raise requests.HTTPError(response.content)
        return response.content
        
    def get_server_info(self):
        """
            Returns JSON for server properties
        """
        info = requests.get("{}/api/server".format(self.base_url))
        if info.status_code != 200:
            raise requests.HTTPError(info.content)
        return info.content