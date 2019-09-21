#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
This module defines constants that don't fit into tool or inteferface
categories
"""


from pfp.native import predefine


predefine(
    """
    const int true = 1;
    const int True = 1;
    const int TRUE = 1;

    const int false = 0;
    const int False = 0;
    const int FALSE = 0;
"""
)
