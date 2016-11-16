import asyncio
import requests

async def fetch(url, n):
    print("fetch from " + str(n))
    return requests.get(url)

async def test1(task_num):
    print("Start task " + str(task_num))
    url = "http://172.17.0.1:8330/webmvc/_clear"
    await asyncio.wait([fetch(url, task_num)])
    print("Finish task = " + str(task_num))

async def run_task():
        await asyncio.wait([test1(i) for i in range(1, 3)])


def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_task())

if __name__ == "__main__":
    main()