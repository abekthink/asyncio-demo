#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author: abekthink

from collections import defaultdict
from types import coroutine


@coroutine
def nice():
    yield


@coroutine
def spawn(task):
    # NEW: recover the child task handle to pass it back to the parent.
    child = yield ('spawn', task)
    return child


# NEW: awaitable object that sends a request to be notified when a
#      concurrent task completes.
@coroutine
def join(task):
    yield ('join', task)

async def hello(name):
    await nice()
    print('Hello, %s!' % (name,))

async def main():
    # NEW: recover the child task handle.
    child = await spawn(hello('world'))
    # NEW: wait for the child task to complete.
    await join(child)
    print('(after join)')


def run_until_complete(task):
    tasks = [(task, None)]
    # NEW: keep track of tasks to resume when a task completes.
    watch = defaultdict(list)
    while tasks:
        queue, tasks = tasks, []
        for task, data in queue:
            try:
                data = task.send(data)
            except StopIteration:
                # NEW: wait up tasks waiting on this one.
                tasks.extend((t, None) for t in watch.pop(task, []))
            else:
                # NEW: dispatch request sent by awaitable object since
                #      we now have 3 diffent types of requests.
                if data and data[0] == 'spawn':
                    tasks.append((data[1], None))
                    tasks.append((task, data[1]))
                elif data and data[0] == 'join':
                    watch[data[1]].append(task)
                else:
                    tasks.append((task, None))

run_until_complete(main())
