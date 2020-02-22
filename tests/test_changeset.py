#!/usr/bin/env python3


import pfp
from pfp.utils import binary
from pfp.fuzz import Changer


def test_changeset():
    template = """
        struct {
            ushort a;
            ushort b;
            ushort c;
            ushort d;
            uint e;
        } data;
    """
    data = "aabbccddeeee"
    dom = pfp.parse(template=template, data=data)
    orig_data = dom._pfp__build()
    assert orig_data == binary(data)

    dom.data.a = 0x4141
    dom.data.b = 0x4242
    dom.data.c = 0x4343
    dom.data.d = 0x4444
    dom.data.e = 0x45454545

    changer = Changer(orig_data)
    changer.push_changes([dom.data.a])
    assert changer.build() == binary("AAbbccddeeee")
    changer.pop_changes()
    assert changer.build() == binary(data)

    changer.push_changes([dom.data.a, dom.data.d])
    assert changer.build() == binary("AAbbccDDeeee")
    changer.push_changes([dom.data.b, dom.data.c])
    assert changer.build() == binary("AABBCCDDeeee")
    changer.push_changes([dom.data.e])
    assert changer.build() == binary("AABBCCDDEEEE")

    changer.pop_changes()
    assert changer.build() == binary("AABBCCDDeeee")
    changer.pop_changes()
    assert changer.build() == binary("AAbbccDDeeee")
    changer.pop_changes()
    assert changer.build() == binary(data)
