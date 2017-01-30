#!/usr/bin/env python
# encoding: utf-8


"""
This module tests pfp.fuzz functionality
"""


import os
import six
import sys
import unittest


sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


import pfp
import pfp.fields
import pfp.fuzz
import pfp.interp
import pfp.utils

import utils


class TestPfpFuzz(unittest.TestCase):
    """Test PfpFuzz functionality
    """

    def setUp(self):
        super(TestPfpFuzz, self).setUp()
    
    def tearDown(self):
        super(TestPfpFuzz, self).tearDown()
    
    # see #49 - make mutate return the changed fields
    def test_fuzz_yield_fields(self):
        template = """
            struct {
                struct {
                    char a;
                    char b;
                } nested;
                char c;
            } root;
        """
        data = "abc"
        dom = pfp.parse(template=template, data=data)

        for at_once in [1,2,3]:
            for mutated,changed_fields in pfp.fuzz.mutate(
                    dom,
                    "basic",
                    num           = 100,
                    at_once       = at_once,
                    yield_changed = True
                ):
                self.assertEqual(len(changed_fields), at_once)

    # see #49 - make mutate return the changed fields
    def test_fuzz_yield_fields_no_yield(self):
        template = """
            struct {
                struct {
                    char a;
                    char b;
                } nested;
                char c;
            } root;
        """
        data = "abc"
        dom = pfp.parse(template=template, data=data)

        for at_once in [0,1,2]:
            for mutated in pfp.fuzz.mutate(
                    dom,
                    "basic",
                    num           = 100,
                    at_once       = at_once,
                    yield_changed = False
                ):
                # make sure it does not return a tuple, as would be the case with
                # yield_changed = True
                self.assertFalse(isinstance(mutated, tuple))


if __name__ == "__main__":
    unittest.main() 
