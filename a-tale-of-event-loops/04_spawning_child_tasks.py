#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author: abekthink

from inspect import iscoroutine
from types import coroutine


@coroutine
def nice():
    yield


# NEW: awaitable object that sends a request to launch a child task!
@coroutine
def spawn(task):
    yield task

async def hello(name):
    await nice()
    print('Hello, %s!' % (name,))

# NEW: parent task!
async def main():
     # NEW: create a child task!
    await spawn(hello('world'))


def run_until_complete(task):
    # NEW: schedule the "root" task.
    tasks = [(task, None)]
    while tasks:
        # NEW: round-robin between a set tasks (we may now have more
        #      than one and we'd like to be as "fair" as possible).
        queue, tasks = tasks, []
        for task, data in queue:
            # NEW: resume the task *once*.
            try:
                data = task.send(data)
            except StopIteration:
                pass
            except Exception as error:
                # NEW: prevent crashed task from ending the loop.
                print(error)
            else:
                # NEW: schedule the child task.
                if iscoroutine(data):
                    tasks.append((data, None))
                # NEW: reschedule the parent task.
                tasks.append((task, None))

run_until_complete(main())
