import os
import re
import tarfile
import json
import requests
import time
from datetime import datetime

import spicedham as sh
THRESHHOLD = 0.5

def test_on_training_data():
    print 'testing against the training data set'
    test_on_data(os.path.join('corpus', 'train'))


def test_on_control_data():
    print 'testing against the control data set'
    test_on_data(os.path.join('corpus', 'control'))

def train_on_api_like_data(file_name):
    time_start = time.time()
    split_time = 0
    train_time = 0
    if os.path.exists(file_name):
        print 'training on the file ' + file_name
        description_spam = []
        description_ham = []
        with open(file_name, 'r') as f:
            load_start = time.time()
            j = json.load(f)
            print 'finished loading file ', str(time.time() - load_start)
        for result in j['results']:
            if result['control']:
                continue
            split_start = time.time()
            description = re.split('[ .,?!\n\r]', result['description'])
            split_time += split_start - time.time()
            train_start = time.time()
            sh.train(description, result['spam'])
            train_time += train_start - time.time()
        #sh.train(description_ham, False)
        #sh.train(description_spam, True)
    else:
        print 'crowd corpus not found. continuing without it.'
    print 'total time', time_start - time.time()
    print 'split time', split_time, 'train time', train_time

def test_file(data_file_name):
    print 'testing on ' + data_file_name
    test_results = {
        'Total': [],
        'True+': [],
        'False+': [],
        'True-': [],
        'False-': [],
        'Error': [],
    }
    with open(data_file_name, 'r') as f:
        j = json.load(f)
        for resp in j['results']:
            test_results['Total'].append(resp['id'])
            probability = sh.classify(re.split('[ \n\r.,?!]', resp['description']))
            if 0.0 > probability > 1.0:
                test_results['Errors'].append(resp['id'])
            if probability > THRESHHOLD:
                if resp['spam']:
                    test_results['True+'].append(resp['id'])
                else:
                    test_results['False+'].append(resp['id'])
            else:
                if resp['spam']:
                    test_results['False-'].append(resp['id'])
                else:
                    test_results['True-'].append(resp['id'])
        show_results(test_results)

def show_results(test_results):
    red = '\033[0;31m'
    green = '\033[0;32m'
    nocolor = '\033[0m'
    print test_results['False-']
    print '{} responses analyzed'.format(len(test_results['Total']))
    print 'True positives:  {} ({}%)'.format(len(test_results['True+']),
        percent(len(test_results['True+']), len(test_results['Total'])))
    print 'False negatives: {} ({}%)'.format(len(test_results['False-']),
        percent(len(test_results['False-']), len(test_results['Total'])))
    print 'True negatives:  {} ({}%)'.format(len(test_results['True-']),
        percent(len(test_results['True-']), len(test_results['Total'])))
    print 'False positives: {} ({}%)'.format(len(test_results['False+']),
        percent(len(test_results['False+']), len(test_results['Total'])))
    print 'Errors:          {} ({}%)'.format(len(test_results['Error']),
        percent(len(test_results['Error']), len(test_results['Total'])))

def percent(numerator, denominator):
    if denominator == 0: return 0
    return round(float(numerator) / float(denominator) * 100, 3)

def test_on_api_data(url='https://input.mozilla.org/api/v1/feedback/?locales=en-US'):
    reqs = requests.get(url)
    resps = reqs.json()
    numSpam = 0
    numTotal = resps['count']
    for resp in resps['results']:
        probability = sh.classify([ x for x in re.split('[ \n\r.,?!]', resp['description']) if x != ''])
        if probability > THRESHHOLD:
            numSpam += 1
            resp['spam'] = True
        else:
            resp['spam'] = False
    file_name = 'analyzed-api-data' + str(datetime.now()) + '.json'
    print 'writing to {}'.format(file_name)
    f = open(file_name, 'w')
    json.dump(resps, f)
    print 'api'
    print '{} api responses anaylzed.'.format(numTotal)
    print 'Tagged Spam: {} ({}%)'.format(numSpam, percent(numSpam, numTotal))
    print 'Tagged Hpam: {} ({}%)'.format(numTotal - numSpam,
        percent(numTotal - numSpam, numTotal))

def test_on_sumo_data_from_mythmons_laptop(url='http://10.252.25.122:8900/api/1/questions?locale=en-US'):
    reqs = requests.get(url)
    resps = reqs.json()
    numSpam = 0
    numTotal = resps['count']
    for resp in resps['results']:
        if not resp['control']:
            continue
        probability = sh.classify(re.split('[ \n\r.,?!]', resp['content']))
        if probability > THRESHHOLD:
            numSpam += 1
            resp['spam'] = True
        else:
            resp['spam'] = False
    file_name = 'sumo-analyzed-api-data' + str(datetime.now()) + '.json'
    print 'writing to {}'.format(file_name)
    f = open(file_name, 'w')
    json.dump(resps, f)
    print 'api'
    print '{} sumo api responses anaylzed.'.format(numTotal)
    print 'Tagged Spam: {} ({}%)'.format(numSpam, percent(numSpam, numTotal))
    print 'Tagged Hpam: {} ({}%)'.format(numTotal - numSpam,
        percent(numTotal - numSpam, numTotal))

if __name__ == '__main__':
    #train_on_api_like_data("jcorpus_new.json")
    train_on_api_like_data("jcorpus.json")
    #test_file('jcorpus.json')
    test_file('jcorpus_new.json')
    test_on_api_data()
