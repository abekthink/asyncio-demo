#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author: abekthink

from types import coroutine


@coroutine
def nice():
    yield

async def hello(name):
    # NEW: yield many times!
    for i in range(5):
        await nice()
    print('Hello, %s!' % (name,))

task = hello('world')
try:
    # NEW: loop!
    while True:
        task.send(None)
except StopIteration:
    pass
