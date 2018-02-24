#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author: abekthink

from types import coroutine


@coroutine
def nice():
    yield

async def hello(name):
    for i in range(5):
        await nice()
    print('Hello, %s!' % (name,))


# NEW: now a reusable function!
def run_until_complete(task):
    try:
        while True:
            task.send(None)
    except StopIteration:
        pass

# NEW: call it as a function!
run_until_complete(hello('world'))
