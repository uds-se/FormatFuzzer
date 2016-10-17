#!/usr/bin/env python
# encoding: utf-8

import random as r

RANDOM = r.Random()
_randint = RANDOM.randint
random =_random = RANDOM.random
choice =_choice = RANDOM.choice

def seed(val):
	RANDOM.seed(val)

def randint(a, b=None):
	if b is None:
		return _randint(0, a)
	else:
		return _randint(a, b)

def randfloat(min_, max_):
	diff = max_ - min_
	res = _random()
	res *= diff
	res += min_
	return res

def maybe(prob=0.5):
	return _random() < prob

def data(length, charset):
	return "".join(_choice(charset) for x in xrange(length))
