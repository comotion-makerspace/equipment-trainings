import requests
import apscheduler
import json
import time
import os
import pickle
import datetime
import logging

# # env vars
API_BASE_URL='https://fabman.io'
FABMAN_API_KEY = os.environ['FABMAN_API_KEY']
# FABMAN_SPACE = os.environ['FABMAN_SPACE']
# USER_AGREEMENT_TRAINING_ID = os.environ['USER_AGREEMENT_TRAINING_ID']

# LOG_DIR_PATH = os.environ['LOG_DIR_PATH']

# # general config

# # TODO: check cached dir exists first!
# OPENING_HOURS_PICKLE = '.{}cached{}hours.pickle'.format(os.sep,os.sep)
# MEMBERS_PICKLE = '.{}cached{}members.pickle'.format(os.sep,os.sep)

# LOG_LEVEL = logging.INFO
# LOG_FILENAME = 'main.log'

# # Logger
# log = logging.getLogger()
# log.setLevel(LOG_LEVEL) 

# fmt = ("%(asctime)s %(levelname)s -> %(message)s")
# datefmt = '%Y-%m-%d %H:%M:%S'
# logging.basicConfig(level=LOG_LEVEL, filename=LOG_FILENAME, format=fmt, datefmt=datefmt)

# # Ensure cached dir exists
# if not os.path.isdir('.{}cached'.format(os.sep)):
#     logging.info('.{}cached doesn\'t exist; creating dir now...'.format(os.sep))
#     try:
#         os.mkdir('.{}cached'.format(os.sep))
#     except Exception as e:
#         logging.warning('{}Couldn\'t create cached dir; cached functions won\'t work!'
#                         .format(e))



def fabman_request(method, url):

    headers = {'Accept': 'application/json',
               'Authorization': 'Bearer {}'.format(FABMAN_API_KEY)}

    if kwargs.get('hours', None):
        print('opening-hours')
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
                with open('{}'.format(MEMBERS_PICKLE), 'wb') as f:
                # with open('{}'.format(MEMBERS_PICKLE), 'wb') as f:
                    pickle.dump(members, f, pickle.HIGHEST_PROTOCOL)
            except Exception as e:
                logging.error('Could not create pickle: {}'
                              '\n{}'
                              .format(MEMBERS_PICKLE, e))
            return members

#     else:
#         logging.info('fabman_request(**kwargs) must be called with specific'
#               'keyword args which match as defined')

# def fabman_request_cached(**kwargs):
#     if kwargs.get('members', None):
#         print('getting cached members')
#         try:
#             with open('.{}cached{}{}'.format(os.sep,os.sep,MEMBERS_PICKLE),'rb') as f:
#             # with open('{}'.format(os.sep,os.sep,MEMBERS_PICKLE),'rb') as f
#                 return pickle.load(f)
#         except Exception as e:
#             logging.info('{} doesn\'t exist! attempting to create it now...'
#                          '\n{}'
#                          .format(MEMBERS_PICKLE, e))
#             fabman_request(members=True)

# def get_opening_hours():
#     if r.status_code == 200 and r.json():
#         with open('.{}cached{}{}'.format(os.sep,os.sep,OPENING_HOURS_PICKLE),'wb') as f:
#             pickle.dump(r.json(), f, pickle.HIGHEST_PROTOCOL)
#         logging.info('Fetching opening hours')
#     else:
#         logging.warning('Unable to fetch opening hours')


# remove trainings from all members - at some time every year




def remove_all_member_training_course(training_course_id):
    ''' input: list or int, removes all members from a given training course output: boolean if successful '''
    course_str = ''
    if type(training_course_id) == list:
        for course_id in training_course_id:
            course_str += f'&trainingCourses={course_id}'
    else:
        course_str = f'&trainingCourses={training_course_id}'
    print(course_str)
    headers = {'Accept': 'application/json',
               'Authorization': f'Bearer {FABMAN_API_KEY}'}
    r = requests.get(f'{API_BASE_URL}/api/v1/members?embed=trainings{course_str}&limit=500', headers=headers)
    if r.status_code == 200:
        members = r.json()
        while r.links and members:
            try:
                link = r.links['next']['url']
                r = requests.get(f'{API_BASE_URL}{link}', headers=headers)
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
            for m in members:
                member_id = str(m['id'])
                if type(training_course_id) == list:
                    for course_id in training_course_id:
                        for training in m['_embedded']['trainings']:
                            if training['_embedded']['trainingCourse']['id'] == course_id:
                                training_id = str(training['id'])
                        r = requests.delete(f'{API_BASE_URL}/api/v1/members/{member_id}/trainings/{training_id}', headers=headers)
                        print(f'removed: {member_id}')
                else:
                    for training in m['_embedded']['trainings']:
                        if training['_embedded']['trainingCourse']['id'] == training_course_id:
                            training_id = str(training['id'])
                            print(f'GOT training {training_id}')
                    r = requests.delete(f'{API_BASE_URL}/api/v1/members/{member_id}/trainings/{training_id}', headers=headers)
                    print(f'removed: {member_id} status: {r.status_code}')
training_course_id = 543
# training_course_id = [ 542, 543 ]
print(remove_all_member_training_course(training_course_id))

# training_course_id = 300
# remove_all_member_training_course(training_course_id)
