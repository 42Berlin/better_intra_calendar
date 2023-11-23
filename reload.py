import requests
from os import getenv
from datetime import datetime
from utils import get_user_data

def main():
    users = list(get_user_data().keys())

    before = datetime.now()

    print(f"Starting reloading {before}:")

    for login in users:
        print(f"Sending request for {login}")
        try:
            requests.post(f"{getenv('CALENDAR_URL')}/reload/{login}",
                      headers = {
                          'X-Secret': getenv("WEBHOOK_TOKEN")
                      })
        except Exception as e:
            print(f"Could not send request to {login}: {e}")
    
    diff = datetime.now() - before

    print(f"\nThe reloading took {diff}\n")


if __name__ == "__main__":
    main()