#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author: abekthink

import time
import random
import asyncio
import aiohttp
import argparse
from collections import namedtuple
from concurrent.futures import ALL_COMPLETED

Service = namedtuple('Service', ('name', 'url', 'ip_attr'))

SERVICES = (
    Service('ipify', 'https://api.ipify.org?format=json', 'ip'),
    Service('ip-api', 'http://ip-api.com/json', 'query'),
    Service('borken', 'http://no-way-this-is-going-to-work.com/json', 'ip')
)

DEFAULT_TIMEOUT = 0.01


async def fetch_ip(service):
    start = time.time()
    print('Fetching IP from {}'.format(service.name))

    await asyncio.sleep(random.randint(1, 3) * 0.1)

    async with aiohttp.ClientSession() as session:
        try:
            response = await session.get(service.url)
        except:
            print('{} is unresponsive'.format(service.name))
            return None
        else:
            json_response = await response.json()
            ip = json_response[service.ip_attr]

            print('{} finished with result: {}, took: {:.2f} seconds'.format(
                service.name, ip, time.time() - start))
            return ip


async def asynchronous(timeout):
    timeout = 10
    response = {
        "message": "Result from asynchronous.",
        "ip": "not available"
    }

    futures = [fetch_ip(service) for service in SERVICES]
    done, pending = await asyncio.wait(
        futures, timeout=timeout, return_when=ALL_COMPLETED)

    for future in pending:
        future.cancel()

    for future in done:
        response["ip"] = future.result() or response["ip"]

    print(response)


parser = argparse.ArgumentParser()
parser.add_argument(
    '-t', '--timeout',
    help='Timeout to use, defaults to {}'.format(DEFAULT_TIMEOUT),
    default=DEFAULT_TIMEOUT, type=float)
args = parser.parse_args()

print("Using a {} timeout".format(args.timeout))
ioloop = asyncio.get_event_loop()
ioloop.run_until_complete(asynchronous(args.timeout))
ioloop.close()
