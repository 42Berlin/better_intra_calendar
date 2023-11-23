# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    utils.py                                           :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: nathan <nathan@42berlin.de>                +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2023/10/26 11:18:20 by nathan            #+#    #+#              #
#    Updated: 2023/11/23 17:01:36 by nathan           ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

import json
import requests
from datetime import datetime
from os import getenv
from fastapi import Request, Response
from google.oauth2 import service_account

from intralib.intra import ic


def get_user_data():
    f = open('user_data.json', 'r')
    try:
        users_json = json.load(f)
    except:
        users_json = {}
    f.close()
    return users_json

def get_creds():
    return service_account.Credentials.from_service_account_file(
        '.google-creds.json', scopes=['https://www.googleapis.com/auth/calendar']
    )


def ics_url(cal_id: str):
    return f'https://calendar.google.com/calendar/ical/{cal_id}/public/basic.ics'


def pretty_json(json_data):
    try:
        return json.dumps(json_data, sort_keys=True, indent=4)
    except:
        try:
            data = json.load(json_data)
            return json.dumps(data, sort_keys=True, indent=4)
        except:
            return json_data


def change_slot(slot):
    evaluated_login = "|".join(
            map(lambda x: 
                x["login"], slot["scale_team"]["correcteds"])
            ) if slot["scale_team"] else None

    # (begin_at, end_at, login of the slot creator, logins of the evaluateds)
    #                                               ^ format: login|login|login
    res = (datetime.strptime(slot["begin_at"], "%Y-%m-%dT%H:%M:%S.%fZ"),
            datetime.strptime(slot["end_at"], "%Y-%m-%dT%H:%M:%S.%fZ"),
            slot["user"]["login"], evaluated_login)

    return res


def should_supp_slot(set, x):
    for y in set:
        if y[0] == x[0]:
            if y[1] > x[1]:
                return True
        elif y[1] == x[0]:
            if x[0] > y[0]:
                return True
    
    return False


def evaluating_slots(data, user):
    evaluating_slots = set(filter(lambda x: user in (x[3] or []), map(change_slot, data)))

    new = set()
    for _ in range(0, 25):
        for slot in evaluating_slots:
            for x in evaluating_slots:
                new_slot = None
                if slot[1] >= x[0]:
                    new_slot = (slot[0], x[1], slot[2])
                elif slot[0] >= x[1]:
                    new_slot = (x[0], slot[1], slot[2])
                if new_slot:
                    new.add(new_slot)
        evaluating_slots = None
        evaluating_slots = new
        new = set()

    to_remove = []

    for x in evaluating_slots:
        if should_supp_slot(evaluating_slots, x):
            to_remove.append(x)

    for x in to_remove:
        evaluating_slots.remove(x)

    return sorted(evaluating_slots)


def open_slots(data, user):
    open_slot = set(filter(lambda x: x[2] == user, map(change_slot, data)))

    new = set()
    for _ in range(0, 25):
        for slot in open_slot:
            for x in open_slot:
                new_slot = None
                if slot[1] >= x[0]:
                    new_slot = (slot[0], x[1], slot[2])
                elif slot[0] >= x[1]:
                    new_slot = (x[0], slot[1], slot[2])
                if new_slot:
                    new.add(new_slot)
        open_slot = None
        open_slot = new
        new = set()

    to_remove = []

    for x in open_slot:
        if should_supp_slot(open_slot, x):
            to_remove.append(x)

    for x in to_remove:
        open_slot.remove(x)

    return sorted(open_slot)

def create_events(service, events, name, calendar_id):
    every_events = map(lambda x: 
                    {
                        'summary': name,
                        'location': '42 Berlin',
                        'description': name,
                        'start': {
                            'dateTime': x[0].strftime('%Y-%m-%dT%H:%M:%S%z'),
                            'timeZone': 'UTC',
                        },
                        'end': {
                            'dateTime': x[1].strftime('%Y-%m-%dT%H:%M:%S%z'),
                            'timeZone': 'UTC',
                        },
                    }, events)
    
    for x in every_events:
        service.events().insert(calendarId=calendar_id, body=x).execute()


def verify_secret(req: Request, special_token: str = None):
    secret_header = req.headers.get("x-secret")
    compare_to = special_token
    if not special_token:
        compare_to = getenv("SECRET")

    if not secret_header or secret_header != compare_to:

        print("\033[31;1m", req.client.host, " failed the header auth.\033[0m", sep="")
        print("\033[32mHeaders:\n", req.headers, "\033[0m", sep="")
        return Response("Forbidden", 403)

    return None


def send_email(email: str, url: str):
    f = open("content/email_content.html")

    content = f.read()

    content = content.replace("GOOGLECALENDARURL", url)

    f.close()

    body = {
        "recipients": [],
        "bcc": [
            email
        ],
        "subject": "42Berlin: Better calendar",
        "title": "Better calendar",
        "subtitle": "Welcome to the amazing spiderman",
        "content": content
    }

    res = requests.post(getenv("MAILER_URL"), data=json.dumps(body), headers={
        'X-Secret': getenv("MAILER_SECRET"),
        'Content-Type': 'application/json'
    })

    if res.ok:
        return True
    return False

def clear_calendar(service, cal_id):
    page_token = None
    
    every_events = []

    while True:
        cal_events = service.events() \
                    .list(calendarId=cal_id, pageToken=page_token) \
                    .execute()

        for event in cal_events['items']:
            every_events.append(event)
        page_token = cal_events.get('nextPageToken')
        if not page_token:
            break

    for x in every_events:
        service.events().delete(calendarId=cal_id, eventId=x["id"]).execute()


def create_exam_events(service, cal_id, login: str):
    events = ic.pages_threaded("campus/51/exams?filter[future]=true")
    
    exam_users = []

    for e in events:
        req = ic.pages_threaded(f"exams/{e['id']}/exams_users")
        req = list(filter(lambda x: x["user"]["login"] == login, req))

        if len(req):
            exam_users.append(req)
    
    real = []
    
    for x in exam_users:
        for y in x:
            real.append(y)

    every_events = map(lambda x: 
        {
            'summary': "Exam at 42Berlin",
            'location': '42 Berlin',
            'description': "Exam at 42Berlin",
            'start': {
                'dateTime': x["exam"]["begin_at"],
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': x["exam"]["end_at"],
                'timeZone': 'UTC',
            },
        }, real)
    
    for x in every_events:
        service.events().insert(calendarId=cal_id, body=x).execute()