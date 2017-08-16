# -*- coding: UTF-8 -*-

import os
import re
import sys
import yaml

from fbchat import Client
from fbchat.models import *

client = Client(<email>, <password>)
HELP = """
    python fbtest.py [OPTIONS...] COMMAND=...
	-h, --help         : List commands for this tool
	-r, --reset        : Set all participants' points to zero
	chat=CHAT          : Name or uid of Facebook message thread to post message (defaults to self)
        message='MESSAGE'  : Message to send to group, lowercase first name with ++ or --(no space) adds or subtracts cool points
                             (i.e. chris--)
    """

def _init_cool(cool_file, name_file, thread):
    users = [client.fetchUserInfo(u) for u in thread.participants]
    names = [u.values()[0].name.lower().split(' ')[0] for u in users]

    with open(cool_file, 'w') as cf:
        for n in names:
           cf.write('{0}: 0\n'.format(n))

    with open(name_file, 'w') as nf:
        for i in range(len(names)):
            nf.write('{0}: {1}\n'.format(names[i], users[i].values()[0].name))


def _write_points(cool_file, score):
    with open(cool_file, 'w') as points:
        yaml.dump(score, points, default_flow_style=False)
    print score


def _load_points(cool_file):
    with open(cool_file) as points:
        scores = yaml.load(points)
        if type(scores) == dict:
            return scores
    return None


def reset_cool():
    score = {}
    for name in COOL_MAP.keys():
        score[name] = 0
    _write_points(score)


def cool_points(msg, chat, chat_type, mode=None):
    print 'COOL!!!!!!!!!!!!'
    cool_file = '.cool_{0}.yaml'.format(chat.name)
    name_file = '.names_{0}.yaml'.format(chat.name)
    if not os.path.isfile(cool_file) and not os.path.isfile(name_file):
        _init_cool(cool_file, name_file, chat)
    points = _load_points(cool_file)
    names = _load_points(name_file)
    cool_alert = ''
    if points and names: 
        name = re.sub(r'\W+', '', msg)
        if name in points.keys():
            curr_points = points[name]
            curr_points = curr_points - 1 if mode == 'sub' else curr_points + 1
            points[name] = curr_points
            _write_points(cool_file, points)
            cool_alert = '{0} now has {1} cool points.'.format(names[name], points[name])
            if curr_points == 1:
                cool_alert = cool_alert.replace('points', 'point')
        else:
            cool_alert = 'Unknown User'
    else:
        print 'Nothing available for group'

    print cool_alert
    client.sendMessage(cool_alert, thread_id=chat.uid, thread_type=chat_type)



def parse_command():
    args = [a for a in sys.argv if a[0] != '-' and a != 'fbtest.py']
    opts = [o for o in sys.argv if o[0] == '-']
    
    if '--help' in opts or '-h' in opts:
        print HELP
        return

    if '--reset' in opts or '-r' in opts:
        reset_cool()

    msg = to = None
    for arg in args:
        if arg.startswith('message='):
            msg = arg.split('=')[1]
            continue
        elif arg.startswith('chat='):
            to = arg.split('=')[1]

    if msg is None:
        msg = 'TEST'
    if to is None:
        to = client.uid    
    

    try:
        int(to)
    except ValueError:
        to = client.searchForGroups(to)[0].uid

    thread = client.fetchThreadInfo(to).values()[0]
    thread_type = thread.type
        
    print 'LOG: sending', msg, 'to', thread.name
    client.sendMessage(msg, thread_id=to, thread_type=thread_type)
    
    if '++' in msg:
        cool_points(msg, thread, thread_type, mode='add')
    elif '--' in msg:
        cool_points(msg, thread, thread_type, mode='sub')


def main():
    parse_command()
    client.logout()

if __name__ == "__main__":
    main()
