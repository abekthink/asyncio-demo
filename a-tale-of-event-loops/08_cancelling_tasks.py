#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author: abekthink

from inspect import iscoroutine
from types import coroutine
from collections import defaultdict


@coroutine
def spawn(task):
    task = yield ('spawn', task)
    return task


@coroutine
def join(task):
    yield ('join', task)


# NEW: exception to be raised inside tasks when they are cancelled.
class CancelledError(Exception):
    pass


# NEW: request that CancelledError be raised inside the task.
@coroutine
def cancel(task):
    cancelled = yield ('cancel', task, CancelledError())
    assert cancelled is True


# NEW: pause the task without plans to reschedule it (this is simply to
#      guarantee execution order in this demo).
@coroutine
def suspend():
    yield ('suspend',)


async def hello(name):
    try:
        await suspend()
    except CancelledError:
        print('Hello, %s!' % (name,))
        raise


# NEW: spawn a task and then cancel it.
async def main():
    child = await spawn(hello('world'))
    await cancel(child)
    await join(child)


def run_until_complete(task):
    tasks = [(task, None)]
    watch = defaultdict(list)

    # NEW: keep track of all tasks in the tree.
    tree = {task}

    while tasks:
        queue, tasks = tasks, []
        for task, data in queue:
            try:
                # NEW: we may need to pass data or inject an exception.
                if isinstance(data, Exception):
                    data = task.throw(data)
                else:
                    data = task.send(data)
            except (StopIteration, CancelledError):
                tasks.extend((t, None) for t in watch.pop(task, []))
                # NEW: update bookkeeping.
                tree.discard(task)
            else:
                if data and data[0] == 'spawn':
                    tasks.append((data[1], None))
                    tasks.append((task, data[1]))
                    # NEW: update bookkeeping.
                    tree.add(data[1])
                elif data and data[0] == 'join':
                    watch[data[1]].append(task)
                elif data and data[0] == 'cancel':
                    # NEW: schedule to raise the exception in the task.
                    if data[1] in tree:
                        tasks.append((data[1], data[2]))
                        tasks.append((task, True))
                    else:
                        tasks.append((task, False))
                elif data and data[0] == 'suspend':
                    pass
                else:
                    tasks.append((task, None))

run_until_complete(main())

# output: Hello, world!
