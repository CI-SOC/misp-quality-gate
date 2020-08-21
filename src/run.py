__author__ = 'Chris Koepp <christian.koepp@siemens.com>'

from controller.quality import QualityController

import logging
logging.basicConfig(filename='example.log',level=logging.INFO,format='%(asctime)s %(message)s')

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

controller = QualityController(
    hostname='<<enter misp server>>',
    secret_key='<<enter auth key>>'
)

events = controller.gather_potential_events()
for event in events:
    qm_result = QualityController.perform_quality_check(event)
    uuid = event['Event']['uuid']
    if qm_result:
        controller.perform_vetting(uuid)
        print(bcolors.OKGREEN + '[X] Event {} PASSED QUALITY GATE'.format(uuid) + bcolors.ENDC)
        logging.info('[X] Event {} PASSED QUALITY GATE'.format(uuid))
    else:
        print(bcolors.FAIL + '[*] Event {} FAILED QUALITY GATE'.format(uuid) + bcolors.ENDC)
        logging.warning('[*] Event {} FAILED QUALITY GATE'.format(uuid))

