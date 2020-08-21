from connectors.misp import MispConnector
import re
import logging
logging.basicConfig(filename='./example.log',level=logging.INFO,format='%(asctime)s %(message)s')

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

__author__ = 'Chris Koepp <christian.koepp@siemens.com>'


class QualityController(object):
    """
    Responsible controller class for the actual Quality Management process.
    """

    # regular expressions to check MISP taxonomies present in event
    ADMIRALTY_REGEXP = re.compile(r'^admiralty-scale:source-reliability=\"[a-g]\"$')
    TLP_REGEXP = re.compile(r'^tlp:(white|green|amber|red)$')
    #CRITICAL_SECTOR_REGEXP = re.compile(
    #    r'^dhs-ciip-sectors:DHS-critical-sectors=\"(transpor​t​|government-facilities​|critical-manufacturing|energy|it|emergency-services|water|financial-services|food-agriculture|healthcare-public)\"$')
    CRITICAL_SECTOR_REGEXP = re.compile(r'^ci-soc:critical-sector=\"(energy|finance|food|government|health|ict|manufacturing|safety|transportation)\"$')
    VICTIM_LOCATION_REGEXP = re.compile(r'^ci-soc:victim-location=\"nb|ns|pe|nf|qc|on|mb|sk|ab|bc|nw|yk|nu"$')

    # actual quality checklist that can be extended/modified whenever needed
    QUALITY_CHECKS = {

        # ToDo: outsource fetching of tag attributes to a dedicated method

        'ADMIRALTY': lambda x: sum([1 for i in x['Event'].get('Tag', []) if QualityController.ADMIRALTY_REGEXP.match(i['name'])]) >= 1,

        'TLP': lambda x: sum([1 for i in x['Event'].get('Tag', []) if QualityController.TLP_REGEXP.match(i['name'])]) >= 1,

        'CRITICAL_INFRASTRUCTURE': lambda x: sum([1 for i in x['Event'].get('Tag', []) if
                                                  QualityController.CRITICAL_SECTOR_REGEXP.match(i['name'])]) >= 1,
        # ToDo: replace with actual location tag check
        #'LOCATION': lambda x: True,
        'VICTIM_LOCATION': lambda x: sum([1 for i in x['Event']['Tag'] if QualityController.VICTIM_LOCATION_REGEXP.match(i['name'])]) >=1,

        'CONTENT': lambda x: len(x['Event']['Attribute']) > 0,
    }

    def __init__(self, hostname, secret_key):
        """ Constructor. Nothing fancy here :) """

        self.__connector = connector = MispConnector(
            hostname=hostname,
            secret_key=secret_key,

            # CI SOC sharing group id
            sharing_group_id='<<enter sharing group name>>'
            #sharing_group_id=1
        )

    @staticmethod
    def _list_event_uuids(events):
        """ Returns a set of potential QM event candidates when given input from MISP event search endpoint """

        event_uuids = set()
        for i in events['response']['Attribute']:
            event_uuids.add(i['Event']['uuid'])
        return event_uuids

    def gather_potential_events(self):
        """
        Returns a list of all events that have to be pushed through the QM check.
        """

        # ToDo: adjust timespan
        unpublished_events, _ = self.__connector.get_unpublished_events(timespan='30d')

        # fetch all potential events
        potential_events = []
        for uuid in QualityController._list_event_uuids(unpublished_events):
            event, _ = self.__connector.get_event_details(uuid)
            potential_events.append(event)

        return potential_events

    def perform_vetting(self, event_uuid):
        """
        Triggers the publication of a successfully checked event using its UUID
        """

        self.__connector.publish_event(event_uuid)


    @staticmethod
    def perform_quality_check(event):
        """
        Returns True if QM check succeeds and False otherwise.
        """

        check_failed = False
        for key, value in QualityController.QUALITY_CHECKS.items():

            qm_result = value(event)

            print(
                bcolors.ENDC +
                '[{}] Event {} {} {}'.format(
                    ' ' if qm_result else '!',
                    event['Event']['uuid'],
                    bcolors.OKGREEN + 'PASSED' + bcolors.ENDC  if qm_result else bcolors.FAIL + 'FAILED' + bcolors.ENDC,
                    key
                )
            )
            logging.info(
                '[{}] Event {} {} {}'.format(
                    ' ' if qm_result else '!',
                    event['Event']['uuid'],
                    'PASSED' if qm_result else 'FAILED',
                    key
                )
            )

            if not qm_result:
                check_failed = True

        return not check_failed
