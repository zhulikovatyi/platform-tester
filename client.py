#!/usr/bin/python
import sys
import os
import requests
import pickle
import asyncio
import json
import argparse
import re


class Tester:
    clear_cache = None
    host = None
    port = None
    app_url = None
    task_plan_file = None
    task_specification = None
    verbose = None
    _previous_response = None

    def __init__(self, args):
        self.clear_cache = args.clear
        self.verbose = args.verbose
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

    async def compile_parametrized_string(self, string):
        vr = re.findall("\$([^\$]+)\$", string)
        if len(vr) > 0:
            for lm in vr:
                vt = re.findall("([^\[\]\']+)(\[.+\])", lm)
                k = json.loads(eval("self." + vt[0][0]).decode("utf-8"))
                b = eval("k" + vt[0][1])
                string = string.replace("$" + lm + "$", b)
        return string

    async def future_fetch__operation(self, s, username, password, auth_method, url, params, files):
        if files is not None:
            fls = dict()
            i = 0
            for f in files:
                fls['file_' + str(++i)] = open(f, 'rb')
            del s.headers["Content-Type"]
            response = s.post(url, data=params, files=fls)
        else:
            json_str = await self.compile_parametrized_string(json.dumps(params))
            response = s.post(url, json_str) if params is not None else s.get(url)
        if response.status_code == 401:
            print("Invalid session detected", response.content)
            await asyncio.wait([self.login(username, password, auth_method)])
            s.cookies = await self.load_cookies('cookie-' + username)
            if files is not None:
                fls = dict()
                i = 0
                for f in files:
                    fls['file_' + str(++i)] = open(f, 'rb')
                if "Content-Type" in s.headers:
                    del s.headers["Content-Type"]
                response = s.post(url, data=params, files=fls)
            else:
                json_str = await self.compile_parametrized_string(json.dumps(params))
                response = s.post(url, json_str) if params is not None else s.get(url)
        self._previous_response = response
        print(url, json_str, response.status_code)
        if self.verbose:
            print(response.headers, response.content)
        return response

    async def login(self, username, password, auth_method):
        s = requests.Session()
        s.cookies = await self.load_cookies('cookie-' + username)
        s.headers["Content-Type"] = "application/json"
        login_data = {"username": username, "password": password, "authMethod": auth_method}
        response = await asyncio.wait([self.future_fetch__operation(s, username, password, auth_method,
                                                                    self.app_url + "/webmvc/api/auth", login_data,
                                                                    None)])
        await self.save_cookies(s.cookies, 'cookie-' + username)
        return response

    async def create_cookie_file_if_need(self, user_login):
        if not os.path.exists('cookie-' + user_login):
            print("Create cookie file for the user '" + user_login + "'")
            await self.save_cookies(requests.Session().cookies, 'cookie-' + user_login)
            return True
        else:
            return False

    async def task(self, username, password, auth_method, url, params, files, count):
        print("Call " + url + " by user '" + username + "'")
        url = await self.compile_parametrized_string(url)
        s = requests.Session()
        s.cookies = await self.load_cookies('cookie-' + username)
        s.headers["Content-Type"] = "application/json"
        for i in range(count):
            await asyncio.wait(
                [self.future_fetch__operation(s, username, password, auth_method, self.app_url + url, params, files)]
            )

    async def task_for_user(self, username, password, auth_method):
        print("Start task for the user '" + username + "'")
        await asyncio.wait([self.create_cookie_file_if_need(username)])
        if self.task_specification[0] == 'sync':
            for t in [(line['url'], line['params'] if 'params' in line else None,
                       line['files'] if 'files' in line else None,
                       line['requestCount'] if 'requestCount' in line else 1)
                      for line in self.task_specification[1:]]:
                await self.task(username, password, auth_method, t[0], t[1], t[2], t[3])
        else:
            await asyncio.wait([
                                   self.task(username, password, auth_method, t[0], t[1], t[2], t[3])
                                   for t in [(line['url'], line['params'] if 'params' in line else None,
                                              line['files'] if 'files' in line else None,
                                              line['requestCount'] if 'requestCount' in line else 1)
                                             for line in self.task_specification]
                                   ])

    async def make_test(self):
        if self.clear_cache:
            print("Start clean cache")
            requests.get(self.app_url + "/webmvc/_clear")
            print("Finish clean cache")
        await asyncio.wait([
                               self.task_for_user(
                                   line.strip().split(":")[0], line.strip().split(":")[1], line.strip().split(":")[2]
                               ) for line in sys.stdin
                               ])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', dest='clear', action='store_true')
    parser.add_argument('-v', dest='verbose', action='store_true')
    parser.add_argument('--host', dest='host')
    parser.add_argument('--port', dest='port')
    parser.add_argument("--task-plan", dest='task_plan')
    loop = asyncio.get_event_loop()
    tester = Tester(parser.parse_args())
    loop.run_until_complete(tester.make_test())


if __name__ == "__main__":
    main()
