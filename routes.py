# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    routes.py                                          :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: nathan <nathan@42berlin.de>                +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2023/10/26 11:18:23 by nathan            #+#    #+#              #
#    Updated: 2023/11/23 15:16:57 by nathan           ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

import os
import uvicorn
import json
import requests
from datetime import datetime
from sys import stderr
from fastapi import FastAPI, Request, Response
from googleapiclient.discovery import build, Resource
from intralib.intra import ic

from utils import clear_calendar, create_exam_events, ics_url, \
                    evaluating_slots, create_events, open_slots, \
                    pretty_json, get_creds, get_user_data, send_email, \
                    verify_secret

ITEM_ID = 1076

app = FastAPI()

# Under this line, every request should need a secret token in x-secret header

@app.post('/reload/{user}')
async def reload(req: Request, user: str):
    verification = verify_secret(req, special_token=os.getenv("WEBHOOK_TOKEN"))
    if verification:
        return verification

    print(datetime.now(), ": Reloading", user)

    creds = get_creds()
    service: Resource = build('calendar', 'v3', credentials=creds)

    users_json = get_user_data()

    if user not in users_json:
        return Response(f'User {user} does not exist', 404)

    cal_id = users_json[user]["calendar_id"]

    data = ic.pages_threaded(f"users/{user}/slots", params={
        "filter[future]": "true",
        "filter[campus_id]": 51
    })
    
    open_slot = open_slots(data, user)
    evaluating = evaluating_slots(data, user)

    clear_calendar(service, cal_id)
    
    create_events(service, open_slot, "Open 42 correction slot", cal_id)
    create_events(service, evaluating, "Getting corrected at 42", cal_id)

    events = ic.pages_threaded(f"users/{user}/events_users")

    for e in events:
        e = e["event"]
        body = {
            'summary': e["name"],
            'location': e["location"],
            'description': e["description"],
            'start': {
                'dateTime': e["begin_at"],
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': e["end_at"],
                'timeZone': 'UTC',
            },
        }
        service.events().insert(calendarId=cal_id, body=body).execute()
    
    create_exam_events(service, cal_id, user)

    return Response("User reloaded", 200)


@app.post('/create/')
async def create_a_calendar(req: Request):
    verification = verify_secret(req, special_token=os.getenv("WEBHOOK_TOKEN"))
    if verification:
        return verification

    webhook_data = await req.json()

    if webhook_data["transactable_id"] != ITEM_ID:
        return Response("Ok", 200)

    user = webhook_data["user"]["login"]

    print("Creating user", user)

    users_data = get_user_data()

    if user in users_data:
        print(f"Error: User {user} already exists")
        return Response(f"User {user} already exists", 400)

    creds = get_creds()

    service = build("calendar", "v3", credentials=creds)
    calendar = {
        "summary": f"42Berlin: {user}",
        "timeZone": "Europe/Berlin",
    }
    created_calendar = service.calendars().insert(body=calendar).execute()
    rule = {
        "role": "reader",
        "scope": {
            "type": "default"
        }
    }

    service.acl().insert(calendarId=created_calendar["id"], body=rule).execute()

    url = ics_url(created_calendar["id"])

    users_data[user] = {
        "calendar_id": created_calendar["id"],
        "url": url,
    }

    os.remove("user_data.json")
    f = open("user_data.json", "w")
    json.dump(users_data, f, indent = 4)
    f.close()

    reload(req, user)

    # sending the email
    if not send_email(webhook_data["user"]["email"], url):
        print(f"Warning: Email for {user} was not sent.")
        print(f"Link: {url}")

    return Response("Ok", 200)


@app.get('/every_calendars')
def every(req: Request):
    verification = verify_secret(req)
    if verification:
        return verification

    creds = get_creds()

    service = build('calendar', 'v3', credentials=creds)

    calendar_list = service.calendarList().list().execute()

    print(pretty_json(calendar_list))

    return Response("Printed every calendars on stdout", 200)


@app.delete('/every_calendars')
def delete_all(req: Request):
    verification = verify_secret(req)
    if verification:
        return verification

    creds = get_creds()
    i = 0

    service = build('calendar', 'v3', credentials=creds)

    calendar_list = service.calendarList().list().execute()

    for calendar_entry in calendar_list['items']:
        calendar_id = calendar_entry['id']
        service.calendars().delete(calendarId=calendar_id).execute()
        print(f"Deleted calendar with ID: {calendar_id}")
        i += 1

    os.remove("user_data.json")
    with open('user_data.json', 'w') as f:
        f.write('{}')
    return (Response(f'Deleted {i} calendars', 200))


# Behind this line, x-secret header is not required as it's the root page if someone
#   accidently gets to the site via a web navigator
@app.get('/')
def get_root():
    page = open('content/index.html').read()
    return Response(page, 200)

@app.get('/hello')
def healthcheck():
    rep = ""

    if not os.path.exists("user_data.json"):
        rep = "No user_data.json."
    
    else:        
        data = get_user_data()
        
        if not data:
            rep = "Empty user_data.json or not good json format"

    if len(rep) == 0:
        return Response("Ok", 200)
    return Response("\n".join(rep), 500)

if __name__ == "__main__":
    if not os.path.exists("./ssl/wildcard.key") or \
        not os.path.exists("./ssl/wildcard.crt"):
        print("Need ssl/wildcard.key and ssl/wilcard.crt to launch. Aborting.", file=stderr)
        exit(1)

    uvicorn.run("routes:app", host="0.0.0.0", port=4233,
                ssl_keyfile="./ssl/wildcard.key",
                ssl_certfile="./ssl/wildcard.crt",
                reload=True, use_colors=True)