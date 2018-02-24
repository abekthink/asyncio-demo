#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author: abekthink

from selectors import (
    DefaultSelector,
    EVENT_READ,
    EVENT_WRITE,
)
from socket import socketpair as _socketpair
from types import coroutine


# NEW: request that the event loop tell us when we can read.
@coroutine
def recv(stream, size):
    yield (EVENT_READ, stream)
    return stream.recv(size)


# NEW: request that the event loop tell us when we can write.
@coroutine
def send(stream, data):
    while data:
        yield (EVENT_WRITE, stream)
        size = stream.send(data)
        data = data[size:]


# NEW: connect sockets, make sure they never, ever block the loop.
@coroutine
def socketpair():
    lhs, rhs = _socketpair()
    lhs.setblocking(False)
    rhs.setblocking(False)
    yield
    return lhs, rhs


# NEW: send a message through the socket pair.
async def hello(name):
    lhs, rhs = await socketpair()
    await send(lhs, 'Hello, world!'.encode('utf-8'))
    data = await recv(rhs, 1024)
    print(data.decode('utf-8'))
    lhs.close()
    rhs.close()


def run_until_complete(task):
    tasks = [(task, None)]

    # NEW: prepare for I/O multiplexing.
    selector = DefaultSelector()

    # NEW: watch out, all tasks might be suspended at the same time.
    while tasks or selector.get_map():

        # NEW: poll I/O operation status and resume tasks when ready.
        timeout = 0.0 if tasks else None
        for key, events in selector.select(timeout):
            tasks.append((key.data, None))
            selector.unregister(key.fileobj)

        queue, tasks = tasks, []
        for task, data in queue:
            try:
                data = task.send(data)
            except StopIteration:
                pass
            else:
                # NEW: register for I/O and suspend the task.
                if data and data[0] == EVENT_READ:
                    selector.register(data[1], EVENT_READ, task)
                elif data and data[0] == EVENT_WRITE:
                    selector.register(data[1], EVENT_WRITE, task)
                else:
                    tasks.append((task, None))

run_until_complete(hello('world'))

# output: Hello, world!
