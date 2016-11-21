#!/usr/bin/python
import sys
import os
import requests
import pickle
import asyncio
import json
import argparse
import aiohttp

# ReportWS method params
# "pfParams": {"reportName": "testReport",
#              "templateName": "REPORTS/ShapesReport",
#              "project": "fabulous",
#              "saveFile": "REPORT", "REPORTFORMATS": "pdf,rtf",
#              "reportParams": {
#                  "reportName": "notTestreport",
#                  "templateName": "REPORTS/ShapesReport"
#              }}


class Tester:

    clear_cache = None
    host = None
    port = None
    app_url = None
    task_plan_file = None
    task_specification = None

    def __init__(self, args):
        self.clear_cache = args.clear
        self.host = args.host
        self.port = args.port
        self.task_plan_file = args.task_plan
        self.task_specification = json.loads(open(self.task_plan_file).read())
        self.app_url = "http://" + self.host + ":" + self.port

    @staticmethod
    async def save_cookies(cookie_jar, filename):
        with open(filename, 'wb') as f:
            pickle.dump(cookie_jar, f)

    @staticmethod
    async def load_cookies(filename):
        with open(filename, 'rb') as f:
            return pickle.load(f)

    async def future_fetch__operation(self, s, username, password, url, params):
        response = s.post(url, json.dumps(params))
        if response.status_code == 401:
            await asyncio.wait([self.login(username, password)])
            s.cookies = await self.load_cookies('cookie-' + username)
            response = s.post(url, json.dumps(params))
        print(response.content)
        return response

    async def login(self, username, password):
        s = requests.Session()
        s.cookies = await self.load_cookies('cookie-' + username)
        s.headers["Content-Type"] = "application/json"
        login_data = {"username": username, "password": password}
        print(self.app_url + "/webmvc/api/auth")
        response = await asyncio.wait([self.future_fetch__operation(s, username, password,
                                                                    self.app_url + "/webmvc/api/auth", login_data)])
        await self.save_cookies(s.cookies, 'cookie-' + username)
        return response

    async def create_cookie_file_if_need(self, user_login):
        if not os.path.exists('cookie-' + user_login):
            print("Create cookie file for the user '" + user_login + "'")
            await self.save_cookies(requests.Session().cookies, 'cookie-' + user_login)
            return True
        else:
            return False

    async def task(self, username, password, url, count):
        print("Call " + url + " by user '" + username + "'")
        request_data = {"operation": "START"}
        s = requests.Session()
        s.cookies = await self.load_cookies('cookie-' + username)
        s.headers["Content-Type"] = "application/json"
        for i in range(0, count):
            await asyncio.wait([self.future_fetch__operation(s, username, password, self.app_url + url, request_data)])

    async def task_for_user(self, username, password):
        print("Start task for the user '" + username + "'")
        await asyncio.wait([self.create_cookie_file_if_need(username)])
        await asyncio.wait([
            self.task(username, password, t[0], t[1]) for t in [(line['url'], line['requestCount'])
                                                      for line in self.task_specification]
        ])

    async def make_test(self):
        if self.clear_cache:
            print("Start clean cache")
            requests.get(self.app_url + "/_clear")
            print("Finish clean cache")
        await asyncio.wait([
            self.task_for_user(line.strip().split(":")[0], line.strip().split(":")[1]) for line in sys.stdin
        ])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', dest='clear', action='store_true')
    parser.add_argument('--host', dest='host')
    parser.add_argument('--port', dest='port')
    parser.add_argument("--task-plan", dest='task_plan')
    loop = asyncio.get_event_loop()
    tester = Tester(parser.parse_args())
    loop.run_until_complete(tester.make_test())


if __name__ == "__main__":
    main()
