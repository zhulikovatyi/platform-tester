#!/usr/bin/python
import sys
import os
import requests
import pickle
import asyncio
import json
import argparse

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

    def __init__(self, args):
        self.clear_cache = args.clear
        self.host = args.host
        self.port = args.port
        self.app_url = "http://" + self.host + ":" + self.port

    @staticmethod
    async def save_cookies(cookie_jar, filename):
        with open(filename, 'wb') as f:
            pickle.dump(cookie_jar, f)

    @staticmethod
    async def load_cookies(filename):
        with open(filename, 'rb') as f:
            return pickle.load(f)

    @staticmethod
    async def future_fetch__operation(s, url, params):
        return s.post(url, json.dumps(params))

    async def login(self, username, password):
        s = requests.Session()
        s.cookies = await self.load_cookies('cookie-' + username)
        s.headers["Content-Type"] = "application/json"
        login_data = {"username": username, "password": password}
        response = await asyncio.wait([self.future_fetch__operation(s, self.app_url + "/webmvc/api/auth", login_data)])
        await self.save_cookies(s.cookies, 'cookie-' + username)
        return response

    async def create_cookie_file_if_need(self, user_login):
        if not os.path.exists('cookie-' + user_login):
            print("Create cookie file for the user '" + user_login + "'")
            await self.save_cookies(requests.Session().cookies, 'cookie-' + user_login)
            return True
        else:
            return False

    async def report(self, username):
        dest_api_call = "/webmvc/api/pageflow/fabulous/reportFile"
        print("Call " + dest_api_call + " by user '" + username + "'")
        request_data = {"operation": "START"}
        s = requests.Session()
        s.cookies = await self.load_cookies('cookie-' + username)
        s.headers["Content-Type"] = "application/json"
        future_set, _ = await asyncio.wait([self.future_fetch__operation(s, self.app_url + dest_api_call,
                                                request_data)])
        response = list(future_set)[0].result()
        await self.save_cookies(s.cookies, 'cookie-' + username)
        print("Response from " + dest_api_call + "for user '" + username + "'\n" + response.text)
        return response

    async def task_for_user(self, username, password):
        print("Start task for the user '" + username + "'")
        await asyncio.wait([self.create_cookie_file_if_need(username)])
        future_set, _ = await asyncio.wait([self.report(username)])
        response = list(future_set)[0].result()
        if response.status_code == 401:
            print("Status = 401")
            await asyncio.wait([self.login(username, password)])
            future_set, _ = await asyncio.wait([self.report(username)])
            response = list(future_set)[0].result()
            print(response)

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
    loop = asyncio.get_event_loop()
    tester = Tester(parser.parse_args())
    loop.run_until_complete(tester.make_test())


if __name__ == "__main__":
    main()
