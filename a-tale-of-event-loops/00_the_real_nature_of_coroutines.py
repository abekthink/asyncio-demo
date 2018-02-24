#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author: abekthink

async def hello(name):
    print('Hello, %s!' % (name,))

coro = hello('world')
type(coro)
# output: <class 'coroutine'>

type(coro.send)
# output: <class 'builtin_function_or_method'>

type(coro.throw)
# output: <class 'builtin_function_or_method'>


async def hello(name):
    print('Hello, %s!' % (name,))

task = hello('world')
try:
    task.send(None)
except StopIteration:
    pass

# output: Hello, world!


class Hello(Exception):
   def __init__(self, name):
       self._name = name
   def __str__(self):
       return 'Hello, %s!' % (self._name,)

async def hello(name):
    raise Hello(name)

task = hello('world')
try:
    task.send(None)
except Exception as error:
    # NEW: exception will be propagated here!
    print(error)

# output: Hello, world!


class Hello(Exception):
   def __init__(self, name):
       self._name = name
   def __str__(self):
       return 'Hello, %s!' % (self._name,)

async def hello():
    pass

task = hello()
try:
    # NEW: inject exception.
    task.throw(Hello('world'))
except Exception as error:
    print(error)

# output: Hello, world!
