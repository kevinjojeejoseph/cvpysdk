# -*- coding: utf-8 -*-

# --------------------------------------------------------------------------
# Copyright Commvault Systems, Inc.
# See LICENSE.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""Main file for performing Metrics operations.

_Metrics        : Class for representing all common operations on Metrics Reporting
PrivateMetrics  : Class for representing Private Metrics and performing operations on it.
PublicMetrics   : Class for representing Public Metrics and performing operations on it.

use method save_config() or upload_now() to save the updated configurations.

Metrics:
    __init__(Commcell_object, isprivate)--  initialise with object of CommCell and flag to
                                            specificy metrics Type

    __repr__()                   --  returns the string to represent the instance of the
                                            Metrics class
    enable_health()              --  enables Health service

    disable_health()             --  disables Health service

    enable_activity()            --  enables Activity service

    disable_activity()           --  disables Activity service

    enable_audit()               --  enables Audit service

    disable_audit()              --  disables Audit service

    disable_chargeback()         --  disables Chargeback service

    enable_post_upgrade_check()  -- enables enable_post_upgrade_check Service

    enable_all_services()        -- enables All Service in metrics

    disable_all_services()       -- disables All Service

    enable_metrics()             -- enables Metrics Service

    disable_metrics()            -- disables Metrics Service in CommServe

    set_upload_freq()            --  updates the upload frequency

    set_data_collection_window   -- updates the data collection window

    remove_data_collection_window-- removes data collection window

    set_all_clientgroup()        -- updates metrics configuration with all client groups

    set_clientgroups()           -- sets the client groups for metrics

    save_config()                -- updates the configuration of Metrics, this must be
                                    called to save the configuration changes made in this object

    upload_now()                 -- Performs Upload Now operation of metrics

PrivateMetrics:
    __init__(Commcell_object)   --  initialise with object of CommCell

    update_url(hostname)        --  Updates Metrics URL for download and upload

    enable_chargeback(daily, weekly, monthly)
                                --  deletes the subclient (subclient name) from the backupset

PublicMetrics:
    __init__(Commcell_object)   --  initialise with object of CommCell

    enable_chargeback()         --  deletes the subclient (subclient name) from the backupset

    enable_upgrade_readiness()  -- Enables pre upgrade readiness service

    disable_upgrade_readiness() -- disables pre upgrade readiness service

    enable_proactive_support()  -- Enables Proactive Support service

    disable_proactive_support() -- disables Proactive Support service

    enable_cloud_assist()       -- Enables Cloud Assist service

    disable_cloud_assist()      -- disables Cloud Assist service

"""

from __future__ import absolute_import
from __future__ import unicode_literals
from .exception import SDKException


class _Metrics(object):
    """Class for common operations in Metrics reporting
    this will be inherited by Private and Cloud metrics"""

    def __init__(self, commcell_object, isprivate):
        self._commcell_object = commcell_object
        self._isprivate = isprivate
        self._METRICS = self._commcell_object._services['METRICS']
        self._GET_METRICS = self._commcell_object._services['GET_METRICS'] % self._isprivate
        self._enable_service = True
        self._disable_service = False
        self._get_metrics_config()

    def __repr__(self):
        """Representation string for the instance of the UserGroups class."""
        if self._isprivate == 1:
            metrics_type = 'Private'
        else:
            metrics_type = 'Public'
        return "{0} Metrics class instance for Commcell: '{1}' with config '{2}'".format(
            metrics_type,
            self._commcell_object.webconsole_hostname,
            self._metrics_config
        )

    def _get_metrics_config(self):
        flag, response = self._commcell_object._cvpysdk_object.make_request(
            'GET', self._GET_METRICS
        )
        if flag:
            self._metrics_config = response.json()
            self._metrics_config.update({'isPrivateCloud': bool(self._isprivate == 1)})
            if self._metrics_config and 'config' in self._metrics_config:
                # get services
                self.services = {}
                self._cloud = self._metrics_config['config']['cloud']
                self._service_list = self._cloud['serviceList']
                for service in self._service_list:
                    service_name = service['service']['name']
                    status = service['enabled']
                    self.services[service_name] = status
            else:
                raise SDKException('Response', '102')
        else:
            raise SDKException('Response', '101', response.text)

    def _update_service_state(self, service_name, state):
        for idx, service in enumerate(self._service_list):
            if service['service']['name'] == service_name:
                self._service_list[idx]['enabled'] = state
                self.services[service_name] = state

    @property
    def lastcollectiontime(self):
        """Returns last collection time in unix time format"""
        return self._metrics_config['config']['lastCollectionTime']

    @property
    def lastuploadtime(self):
        """Returns last upload time in unix time format"""
        return self._metrics_config['config'][' lastUploadTime']

    @property
    def nextuploadtime(self):
        """Returns last Next time in unix time format"""
        return self._metrics_config['config']['nextUploadTime']

    @property
    def uploadfrequency(self):
        """Returns last Next time in unix time format"""
        return self._metrics_config['config']['uploadFrequency']

    def enable_health(self):
        """enables Health Service"""
        if self.services['Health Check'] is not True:
            self._update_service_state('Health Check', self._enable_service)

    def disable_health(self):
        """disables Health Service"""
        if self.services['Health Check'] is True:
            self._update_service_state('Health Check', self._disable_service)

    def enable_activity(self):
        """enables Activity Service"""
        if self.services['Activity'] is not True:
            self._update_service_state('Activity', self._enable_service)

    def disable_activity(self):
        """disables Activity Service"""
        if self.services['Activity'] is True:
            self._update_service_state('Activity', self._disable_service)

    def enable_audit(self):
        """enables Audit Service"""
        if self.services['Audit'] is not True:
            self._update_service_state('Audit', self._enable_service)

    def disable_audit(self):
        """disables Audit Service"""
        if self.services['Audit'] is True:
            self._update_service_state('Audit', self._disable_service)

    def enable_post_upgrade_check(self):
        """enables post_upgrade_check Service"""
        if self.services['Post Upgrade Check'] is not True:
            self._update_service_state('Post Upgrade Check', self._enable_service)

    def disables_post_upgrade_check(self):
        """disables post_upgrade_check Service"""
        if self.services['Post Upgrade Check'] is True:
            self._update_service_state('Post Upgrade Check', self._disable_service)

    def disables_chargeback(self):
        """disables post_upgrade_check Service"""
        if self.services['Charge Back'] is True:
            self._update_service_state('Charge Back', self._disable_service)

    def enable_all_services(self):
        """enables All Service"""
        for index, service in enumerate(self._service_list):
            self._service_list[index]['enabled'] = self._enable_service
            service_name = service['service']['name']
            self.services[service_name] = self._enable_service

    def disable_all_services(self):
        """disables All Service"""
        for index, service in enumerate(self._service_list):
            self._service_list[index]['enabled'] = self._disable_service
            service_name = service['service']['name']
            self.services[service_name] = self._disable_service

    def set_upload_freq(self, days=1):
        """
        updates the upload frequency
        Args:
            days (int): number of days for upload frequency, value can be between 1 to 7

        Raises:
            SDKException:
                if invalid days supplied for upload frequency

        """
        if days < 1:
            raise SDKException('Metrics', '101', 'Invalid Upload Frequency supplied')
        self._metrics_config['config']['uploadFrequency'] = days

    def set_data_collection_window(self, seconds=28800):
        """
        updates the data collection window
        Args:
            seconds: number for seconds after 12 AM
            e.g.; 28800 for 8 AM
            default; 28800

        Raises:
            SDKException:
                if window specified is below 12.05 am

        """
        if seconds < 300:  # minimum 5 minutes after 12 midnight
            raise SDKException('Metrics', '101', 'Data collection window should be above 12.05 AM')
        self._metrics_config['config']['dataCollectionTime'] = seconds

    def remove_data_collection_window(self):
        """removes data collection window"""
        self._metrics_config['config']['dataCollectionTime'] = -1

    def set_all_clientgroups(self):
        """updates metrics configuration with all client groups"""

        # sets the list to one row with client group id as -1
        self._metrics_config['config']['clientGroupList'] = [{'_type_': 28, 'clientGroupId': -1}]

    def set_clientgroups(self, clientgroup_name=None):
        """
        sets the client groups for metrics
        Args:
            clientgroup_name (list): list of client group names, None is set all client groups
            will be enabled.
        """
        if clientgroup_name is None:
            self.set_all_clientgroups()
        else:
            clientgroupid_list = []
            for each_clientgroup in clientgroup_name:
                cg_id = self._commcell_object.client_groups.get(each_clientgroup).clientgroup_id
                clientgroupid_list.append(cg_id)

            self._metrics_config['config']['clientGroupList'] = []
            clientgroup = self._metrics_config['config']['clientGroupList']
            for clientgroupid in clientgroupid_list:
                clientgroup.append(
                    {'_type_': 28, 'clientGroupId': clientgroupid, 'clientGroupName': ''}
                )

    def enable_metrics(self):
        """enables Metrics in CommServe"""
        self._metrics_config['config']['commcellDiagUsage'] = self._enable_service

    def disable_metrics(self):
        """disables Metrics in CommServe"""
        self._metrics_config['config']['commcellDiagUsage'] = self._disable_service

    def save_config(self):
        """
        updates the configuration of Metrics
        this must be called to save the configuration changes made in this object
        Raises:
            SDKException:
                if response is not success
        """
        flag, response = self._commcell_object._cvpysdk_object.make_request(
            'POST', self._METRICS, self._metrics_config
        )
        if not flag:
            raise SDKException('Response', '101', response.text)

    def upload_now(self):
        """
        Performs Upload Now operation of metrics
        Raises:
            SDKException:
                if response is not success:
        """

        self._metrics_config['config']['uploadNow'] = 1
        flag, response = self._commcell_object._cvpysdk_object.make_request(
            'POST', self._METRICS, self._metrics_config
        )
        if not flag:
            raise SDKException('Response', '101', response.text)
        # reset upload now flag
        self._metrics_config['config']['uploadNow'] = 0


class PrivateMetrics(_Metrics):
    """Class for operations in private Metrics reporting"""

    def __init__(self, commcell_object):
        """Initialize object of the UserGroups class.

                    Args:
                        commcell_object (object)  --  instance of the Commcell class
                        type -- 1 for private, 0 for public

                    Returns:
                        object - instance of the UserGroups class
        """
        _Metrics.__init__(self, commcell_object, isprivate=1)

    def _update_private_download_url(self, hostname, port, protocol):
        self._cloud['downloadURL'] = '{0}://{1}:{2}/downloads/sqlscripts/'.format(protocol,
                                                                                  hostname,
                                                                                  port)

    def _update_private_upload_url(self, hostname, port, protocol):
        self._cloud['uploadURL'] = '{0}://{1}:{2}/webconsole/'.format(protocol, hostname, port)

    def _update_chargeback_flags(self, daily, weekly, monthly):
        flags = 0
        if daily:
            flags = flags | 4
        if weekly:
            flags = flags | 8
        if monthly:
            flags = flags | 16
        for service in self._service_list:
            if service['service']['name'] == 'Charge Back':
                service['flags'] = flags

    @property
    def downloadurl(self):
        """Returns download URL of private metrics"""
        return self._metrics_config['config']['cloud']['downloadURL']

    @property
    def uploadurl(self):
        """Returns Upload URL of private metrics"""
        return self._metrics_config['config']['cloud']['uploadURL']

    def update_url(self, hostname, port=80, protocol='http'):
        """
        updates private Metrics URL in CommServe
        Args:
            hostname (str): Metrics server hostname
            port (int): port of webconsole
                e.g.; 80 for http and 443 for https
            protocol (str): http or https
                default: http
        """
        self._update_private_download_url(hostname, port, protocol)
        self._update_private_upload_url(hostname, port, protocol)

    def enable_chargeback(self, daily=True, weekly=False, monthly=False):
        """
        Enables Chargeback service as per the daily,weekly and Monthly arguments passes
        Args:
            daily  (bool): enables daily chargeback
            weekly (bool): enables weekly chargeback
            monthly(bool): enables Monthly chargeback

        """
        if self.services['Charge Back'] is not True:
            self._update_service_state('Charge Back', self._enable_service)
        self._update_chargeback_flags(daily, weekly, monthly)


class CloudMetrics(_Metrics):
    """Class for operations in Cloud Metrics reporting"""

    def __init__(self, commcell_object):
        """Initialize object of the UserGroups class.

                    Args:
                        commcell_object (object)  --  instance of the Commcell class

                    Returns:
                        object - instance of the UserGroups class
        """
        _Metrics.__init__(self, commcell_object, isprivate=0)

    def enable_chargeback(self):
        """Enables Chargeback service"""
        if self.services['Charge Back'] is not True:
            self._update_service_state('Charge Back', self._enable_service)

    def enable_upgrade_readiness(self):
        """Enables pre upgrade readiness service"""
        if self.services['Upgrade Readiness'] is not True:
            self._update_service_state('Upgrade Readiness', self._enable_service)

    def disable_upgrade_readiness(self):
        """disables pre upgrade readiness service"""
        if self.services['Upgrade Readiness'] is True:
            self._update_service_state('Upgrade Readiness', self._disable_service)

    def enable_proactive_support(self):
        """Enables Proactive Support service"""
        if self.services['Proactive Support'] is not True:
            self._update_service_state('Proactive Support', self._enable_service)

    def disable_proactive_support(self):
        """disables Proactive Support service"""
        if self.services['Proactive Support'] is True:
            self._update_service_state('Proactive Support', self._disable_service)

    def enable_cloud_assist(self):
        """Enables Cloud Assist service and proactive support if not already enabled"""
        if self.services['Proactive Support'] is not True:
            # pro active support must be enabled to enable cloud assist
            self.enable_proactive_support()
            self._update_service_state('Cloud Assist', self._enable_service)

    def disable_cloud_assist(self):
        """disables Cloud Assist service"""
        if self.services['Cloud Assist'] is True:
            self._update_service_state('Cloud Assist', self._disable_service)
