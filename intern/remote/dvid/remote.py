"""
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
"""
from intern.remote import Remote
from intern.resource.dvid.resource import *
from intern.service.dvid.project import ProjectService
from intern.service.dvid.metadata import MetadataService
from intern.service.dvid.volume import VolumeService
from intern.service.dvid.versioning import VersioningService

CONFIG_METADATA_SECTION = 'Metadata Service'
CONFIG_VERSIONING_SECTION = 'Versioning Service'
CONFIG_PROJECT_SECTION = 'Project Service'
CONFIG_VOLUME_SECTION = 'Volume Service'
CONFIG_PROTOCOL = 'protocol'
CONFIG_HOST = 'host'

class DVIDRemote(Remote):

	"""
	Remote provides an SDK to the DVID API.
	"""

	def __init__(self, cfg_file_or_dict=None,):
		"""
			Constructor.

			Checks for latest version. If no version is given, assigns version as none
			Protocol and host specifications are taken in as keys -values of dictionary.
			global api variable is named and used for every command that requires api.
		"""
		Remote.__init__(self, cfg_file_or_dict)

		# Init the services
		self._init_project_service()
		self._init_metadata_service()
		self._init_volume_service()
		self._init_versioning_service()

	def _init_project_service(self):
		"""
		Method to initialize the Volume Service from the config data

		Args:
			None

		Returns:
			None

		Raises:
			(KeyError): if given invalid version.
		"""
		project_cfg = self._load_config_section(CONFIG_PROJECT_SECTION)
		proto = project_cfg[CONFIG_PROTOCOL]
		host = project_cfg[CONFIG_HOST]
		api = proto + "://" + host

		self._project = ProjectService(api)
		self._project.base_protocol = proto

	def _init_metadata_service(self):
		"""
		Method to initialize the Volume Service from the config data

		Args:
			None

		Returns:
			None

		Raises:
			(KeyError): if given invalid version.
		"""
		metadata_cfg = self._load_config_section(CONFIG_METADATA_SECTION)
		proto = metadata_cfg[CONFIG_PROTOCOL]
		host = metadata_cfg[CONFIG_HOST]
		api = proto + "://" + host

		self._metadata = MetadataService(api)
		self._metadata.base_protocol = proto

	def _init_volume_service(self):
		"""
		Method to initialize the Volume Service from the config data

		Args:
			None

		Returns:
			None

		Raises:
			(KeyError): if given invalid version.
		"""
		volume_cfg = self._load_config_section(CONFIG_VOLUME_SECTION)
		proto = volume_cfg[CONFIG_PROTOCOL]
		host = volume_cfg[CONFIG_HOST]
		api = proto + "://" + host

		self._volume = VolumeService(api)
		self._volume.base_protocol = proto

	def _init_versioning_service(self):
		"""
		Method to initialize the Volume Service from the config data

		Args:
			None

		Returns:
			None

		Raises:
			(KeyError): if given invalid version.
		"""
		versioning_cfg = self._load_config_section(CONFIG_VERSIONING_SECTION)
		proto = versioning_cfg[CONFIG_PROTOCOL]
		host = versioning_cfg[CONFIG_HOST]
		api = proto + "://" + host

		self._versioning = VersioningService(api)
		self._versioning.base_protocol = proto

	def __repr__(self):
		"""
		Stringify the Remote.

		Returns a representation of the DVIDRemote that lists the host.
		"""
		return "<intern.remote.DVIDRemote [" + self._config['Default']['host'] + "]>"

	def _load_config_section(self, section_name):
		"""
		Method to load the specific Service section from the config file if it
		exists, or fall back to the default

		Args:
			section_name (str): The desired service section name

		Returns:
			(dict): the section parameters
		"""
		if self._config.has_section(section_name):
			# Load specific section
			section = dict(self._config.items(section_name))
		elif self._config.has_section("Default"):
			# Load Default section
			section = dict(self._config.items("Default"))
		else:
			raise KeyError((
				"'{}' was not found in the configuration file and no default " +
				"configuration was provided."
			).format(section_name))

		# Make sure section is valid
		if "protocol" in section and "host" in section:
			return section
		else:
			raise KeyError(
				"Missing values in configuration data. " +
				"Must contain: protocol, host"
			)

	def get_channel(self, chan_name, UUID, exp_name):
		"""
            Method to input all channel hierarchy requirememnts, works as a dummy
            for DVIDRemote Parallelism.

            Args:
                UUID_coll_exp (str) : Root UUID of the repository along with collection and experiment

            Returns:
                chan (str) : String of UUID/col/exp
		"""
		return ChannelResource(chan_name, UUID, exp_name)

	def get_cutout(self, chan, res, xrange, yrange, zrange):
		"""
			Method to request a volume of data from DVID server uploaded through command window

			Args:
				IDrepos (string) : UUID assigned to DVID repository and repository name
				xrange (int) : range of pixels in x axis ([1000:1500])
				yrange (int) : range of pixels in y axis ([1000:1500])
				zrange (int) : range of pixels in z axis ([1000:1010])

			Returns:
				array: numpy array representation of the requested volume

			Raises:
				(KeyError): if given invalid version.
		"""
		return self._volume.get_cutout(chan, res, xrange, yrange, zrange)
    
	def get_project(self, resource):
		"""
		Get attributes of the data model object named by the given resource.

		Args:
			resource (intern.resource.dvid.DVIDResource): resource.name as well
				as any parents must be identified to succeed.

		Returns:
			(intern.resource.dvid.DVIDResource): Returns resource of type
				requested on success.

		Raises:
			requests.HTTPError on failure.
		"""
		return self._project.get(resource)

	def create_project(self, resource):
		"""
			Method to create a project space in the DVID server

			Args:
				coll (str) : Name of collection
				des (str) : Description of collection

			Returns:
				string: Confirmation message

			Raises:
				(KeyError): if given invalid version.
		"""
		return self._project.create(resource)

	def delete_project(self, resource):
		"""
        Method to delete a project

        Args:
            UUID (str) : hexadecimal character long string characterizing the project

        Returns:
            (str) : Confirmation message
		"""

		return self._project.delete(resource)

	def ChannelResource(self, UUID, exp, datatype =  "uint8blk"):
		"""
		Method to create a channel within specified collection, experiment and of a known datatype

		Args:
			UUID (str) : UUID
			exp (str) : Name of the instance of data that will be created
			datatype (str) : Type of data that will be uploaded. Deafaults to uint8blk

		Returns:
			chan (str) : composed of UUID, exp and chan for use in create_cutout function
		"""

		return ChannelResource(UUID, exp, datatype)

	def get_info(self, UUID):
		"""
			Method to obtain information on the requested repository

			Args:
				UUID (string): UUID of the DVID repository (str)

			Returns:
				string: History information of the repository

			Raises:
				(KeyError): if given invalid version.
		"""
		return self._metadata.get_info(UUID)

	def get_log(self, UUID):
		"""
			The log is a list of strings that will be appended to the repo's log.  They should be
			descriptions for the entire repo and not just one node.

			Args:
				UUID (string): UUID of the DVID repository (str)

			Returns:
				string: list of all log recordings related to the DVID repository

			Raises:
				(ValueError): if given invalid UUID.
		"""
		return self._versioning.get_log(UUID)

	def post_log(self, UUID,log1):
		"""
			Allows the user to write a short description of the content in the repository
			{ "log": [ "provenance data...", "provenance data...", ...] }
			Args:
				UUID (string): UUID of the DVID repository (str)
				log_m (string): Message to record on the repositories history log (str)

			Returns:
				HTTP Response

			Raises:
				(ValueError): if given invalid UUID or log.
		"""
		return self._versioning.post_log(UUID,log1)

	def get_server_info(self):
		"""
		Method to obtain information about the server

		Args:
		    none

		Returns:
		    string: Server information

		Raises:
		    (KeyError): if given invalid version.
		"""
		return self._metadata.get_server_info()

	def merge(self, UUID, parents, mergeType="conflict-free", note=""):
		"""
			Creates a conflict-free merge of a set of committed parent UUIDs into a child.  Note
			the merge will not necessarily create an error immediately

			Args:
				mergeType (string) = "conflict-free"
				parents (array) = [ "parent-uuid1", "parent-uuid2", ... ]
				note (string) = this is a description of what I did on this commit

			Returns:
				merge_child_uuid (string): child generated uuid after merge

			Raises:
				HTTPError: On non 200 status code
		"""
		return self._versioning.merge(UUID, parents,mergeType, note)

	def resolve(self, UUID, data, parents, note=""):
		"""
			Forces a merge of a set of committed parent UUIDs into a child by specifying a
			UUID order that establishes priorities in case of conflicts

			Args:
				data (array) = [ "instance-name-1", "instance-name2", ... ],
				parents (array): [ "parent-uuid1", "parent-uuid2", ... ],
				note (string): this is a description of what I did on this commit

			Returns:
				resolve_child_uuid (string): child generated uuid after resolution

			Raises:
				HTTPError: On non 200 status code
		"""

		return self._versioning.resolve(UUID, data, parents, note)

	def commit(self, UUID, note='', log_m=''):
		"""
			Allows the user to write a short description of the content in the repository

			Args:
				UUID (string): UUID of the DVID repository (str)
				note (string): human-readable commit message
				log_m (string): Message to record on the repositories history log (str)

			Returns:
				commit_uuid (string): commit hash

			Raises:
				(ValueError): if given invalid UUID.
		"""

		return self._versioning.commit(UUID, note, log_m)

	def branch(self, UUID, note=''):
		"""
			Allows the user to write a short description of the content in the repository
			
			Args:
				UUID (string): UUID of the DVID repository (str)
				note (string): Message to record when branching

			Returns:
				branch_uuid (string): The child branch UUID

			Raises:
				(KeyError): if given invalid version.
		"""

		return self._versioning.branch(UUID, note)