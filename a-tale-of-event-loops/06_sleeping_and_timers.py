#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author: abekthink

from heapq import heappop, heappush
from time import sleep as _sleep
from timeit import default_timer
from types import coroutine

# NEW: we need to keep track of elasped time.
clock = default_timer


# NEW: request that the event loop reschedule us "later".
@coroutine
def sleep(seconds):
    yield ('sleep', seconds)


# NEW: verify elapsed time matches our request.
async def hello(name):
    ref = clock()
    await sleep(3.0)
    now = clock()
    assert (now - ref) >= 3.0
    print('Hello, %s!' % (name,))


def run_until_complete(task):
    tasks = [(task, None)]

    # NEW: keep track of tasks that are sleeping.
    timers = []

    # NEW: watch out, all tasks might be suspended at the same time.
    while tasks or timers:

        # NEW: if we have nothing to do for now, don't spin.
        if not tasks:
            _sleep(max(0.0, timers[0][0] - clock()))

        # NEW: schedule tasks when their timer has elapsed.
        while timers and timers[0][0] < clock():
            _, task = heappop(timers)
            tasks.append((task, None))

        queue, tasks = tasks, []
        for task, data in queue:
            try:
                data = task.send(data)
            except StopIteration:
                pass
            else:
                # NEW: set a timer and don't reschedule right away.
                if data and data[0] == 'sleep':
                    heappush(timers, (clock() + data[1], task))
                else:
                    tasks.append((task, None))

run_until_complete(hello('world'))

# output: Hello, world!
