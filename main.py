import requests
import apscheduler
import json
import time
import os
import pickle
import datetime
import logging

# env vars

FABMAN_API_KEY = os.environ['FABMAN_API_KEY']
FABMAN_SPACE = os.environ['FABMAN_SPACE']
USER_AGREEMENT_TRAINING_ID = os.environ['USER_AGREEMENT_TRAINING_ID']

# general config

# TODO: check cached dir exists first!
OPENING_HOURS_PICKLE = '.{}cached{}hours.pickle'.format(os.sep,os.sep)
MEMBERS_PICKLE = '.{}cached{}members.pickle'.format(os.sep,os.sep)

LOG_LEVEL = logging.INFO
LOG_FILENAME = 'main.log'

# Logger
log = logging.getLogger()
log.setLevel(LOG_LEVEL) 

fmt = ("%(asctime)s %(levelname)s -> %(message)s")
datefmt = '%Y-%m-%d %H:%M:%S'
logging.basicConfig(level=LOG_LEVEL, filename=LOG_FILENAME, format=fmt, datefmt=datefmt)

def fabman_request(**kwargs):

    headers = {'Accept': 'application/json',
               'Authorization': 'Bearer {}'.format(FABMAN_API_KEY)}

    if kwargs.get('hours', None):
        print('opening-hours')
        r = requests.get('https://fabman.io/api/v1/spaces/{}/opening-hours'
                         .format(FABMAN_SPACE), headers=headers)

    elif kwargs.get('trainings', None):
        r = requests.get('https://fabman.io/api/v1/spaces/{}/opening-hours'
                         .format(FABMAN_SPACE), headers=headers)

    elif kwargs.get('members', None):
        r = requests.get('https://fabman.io/api/v1/members?embed=trainings&limit=500', headers=headers)
        if r.status_code == 200:
            members = r.json()
            while r.links and members:
                try:
                    link = r.links['next']['url']
                    r = requests.get('https://fabman.io{}'.format(link), headers=headers)
                    if r.status_code == 200:
                        members += r.json()
                    else:
                        logging.error('Could not complete request to get Fabman members: {}'
                                      .format(r.reason))
                except KeyError:
                    logging.error('response.links contains values but no response.links[\'next\'][\'url\'] found.'
                                  '\nContent of response.links is: {}'
                                  .format(str(r.links)))
                    break
            if members:
                members = json.loads(json.dumps(members))
            try:
                with open(MEMBERS_PICKLE, 'wb') as f:
                    pickle.dump(members, f, pickle.HIGHEST_PROTOCOL)
            except Exception as e:
                logging.error('Could not create pickle: {}'
                              '\n{}'
                              .format(MEMBERS_PICKLE, e))
            return members

    else:
        logging.info('fabman_request(**kwargs) must be called with specific'
              'keyword args which match as defined')

def fabman_request_cached(**kwargs):
    if kwargs.get('members', None):
        print('getting cached members')
        try:
            with open(MEMBERS_PICKLE, 'rb') as f:
                return pickle.load(f)
        except (OSError, IOError):
            logging.info('{} doesn\'t exist! attempting to get it now...'
                         .format(MEMBERS_PICKLE))
            fabman_request(members=True)

def get_opening_hours():
    if r.status_code == 200 and r.json():
        with open(OPENING_HOURS_PICKLE, 'wb') as f:
            pickle.dump(r.json(), f, pickle.HIGHEST_PROTOCOL)
        logging.info('Fetching opening hours')
    else:
        logging.warning('Unable to fetch opening hours')