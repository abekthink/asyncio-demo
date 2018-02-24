#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author: abekthink

from types import coroutine


# NEW: this is an awaitable object!
@coroutine
def nice():
    yield

async def hello(name):
    # NEW: this makes ``.send()`` return!
    await nice()
    print('Hello, %s!' % (name,))

task = hello('world')
# NEW: call send twice!
task.send(None)
try:
    task.send(None)
except StopIteration:
    pass
