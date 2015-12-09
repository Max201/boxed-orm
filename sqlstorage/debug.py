#!/usr/bin/env python
# -*- coding: utf-8 -*-

OKBLUE = '\033[94m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'


def message(string):
    return str(string) + ENDC


def fail(string):
    return FAIL + message(string)


def success(string):
    return OKGREEN + message(string)


def warning(string):
    return WARNING + message(string)


def info(string):
    return OKBLUE + message(string)


def bold(string):
    return BOLD + message(string)


__all__ = ['message', 'fail', 'success', 'warning', 'info', 'bold']