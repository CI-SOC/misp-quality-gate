__author__ = 'Chris Koepp <christian.koepp@siemens.com>'

import requests


class MispConnector(object):
    """
    Responsible for connecting with MISP API.
    """

    # generic url suffixes of required API endpoints
    SEARCH_URL_SUFFIX = '/attributes/restSearch'
    EVENT_VIEW_URL_SUFFIX = '/events/view/{}'
    EVENT_PUBLISH_URL_SUFFIX = '/events/publish/{}'

    def __create_url(self, suffix):
        """ Returns an URL combining base URL with custom suffix """

        return self._base_url.format(suffix)

    def __create_header(self):
        """ Returns dict containing required HTTP headers to access MISP """

        return {
            'Accept': 'application/json',
            'Authorization': self.__secret_key,
            'Content-Type': 'application/json',
        }

    def __init__(self, hostname, secret_key, sharing_group_id, tls_verify=True):
        """ Constructor """

        self._base_url = 'https://{}'.format(hostname) + '{}'
        self.__secret_key = secret_key
        self._sharing_group_id = sharing_group_id
        self._verify = tls_verify

    def publish_event(self, uuid):
        """
        Triggers publication of given MISP event.
        Returns tuple containing JSON-like dict and HTTP status code
        """

        url = self.__create_url(MispConnector.EVENT_PUBLISH_URL_SUFFIX.format(uuid))
        header = self.__create_header()
        payload = {
            'locked':False,
        }
        #payload={'Event':{'published':1}}

        r = requests.post(url, json=payload, headers=header, verify=self._verify)
        return r.json(), r.status_code

    def get_event_details(self, uuid):
        """
        Fetches all available details for any given MISP event identified by its UUID.
        Returns tuple containing JSON-like dict and HTTP status code
        """

        url = self.__create_url(MispConnector.EVENT_VIEW_URL_SUFFIX.format(uuid))
        header = self.__create_header()

        r = requests.get(url, headers=header, verify=self._verify)
        return r.json(), r.status_code

    def get_unpublished_events(self, timespan='7d'):
        """
        Fetches all unpublished events of the pre-configured organization/sharing-community that was
        pushed within the given timespan (handed over in MISP notation).
        Returns tuple containing JSON-like dict and HTTP status code
        """

        url = self.__create_url(MispConnector.SEARCH_URL_SUFFIX)
        header = self.__create_header()
        payload = {
            'returnFormat': 'json',
            'sharing_group_id': self._sharing_group_id,
            'published': False,
            'event_timestamp': timespan,
        }

        r = requests.post(url, json=payload, headers=header, verify=self._verify)
        return r.json(), r.status_code
