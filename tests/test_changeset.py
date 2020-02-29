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
    assert changer.build() == bytearray(b"AAbbccddeeee")
    changer.pop_changes()
    assert changer.build() == bytearray(binary(data))

    changer.push_changes([dom.data.a, dom.data.d])
    assert changer.build() == bytearray(b"AAbbccDDeeee")
    changer.push_changes([dom.data.b, dom.data.c])
    assert changer.build() == bytearray(b"AABBCCDDeeee")
    changer.push_changes([dom.data.e])
    assert changer.build() == bytearray(b"AABBCCDDEEEE")

    changer.pop_changes()
    assert changer.build() == bytearray(b"AABBCCDDeeee")
    changer.pop_changes()
    assert changer.build() == bytearray(b"AAbbccDDeeee")
    changer.pop_changes()
    assert changer.build() == bytearray(binary(data))


def test_changeset_with_bitfields():
    template = """
        BigEndian();
        struct {
            char a:2; // 11
            char b:2; // 00
            char c:3; // 111
            char d:1; // 0
            uint e;
        } data;
    """
    # 0xc3 = 0b11001110
    data = "\xceeeee"
    dom = pfp.parse(template=template, data=data)
    orig_data = dom._pfp__build()
    assert orig_data == binary(data)

    dom.data.a = 0

    changer = Changer(orig_data)

    with changer.change([dom.data.a]) as changed:
        assert changed == binary("\x0eeeee") # 0x0e = 0b00001110
    assert changer.build() == binary(data)

    dom._pfp__snapshot()
    dom.data.a = 0
    dom.data.d = 1
    with changer.change([dom.data.a, dom.data.d]) as changed:
        assert changed == binary("\x0feeee")  # 0x0f = 0b00001111

        dom._pfp__snapshot()
        dom.data.b = 3
        dom.data.c = 0
        with changer.change([dom.data.b, dom.data.c]) as changed:
            assert changed == binary("\x31eeee") # 0x31 = 0b00110001

            dom._pfp__snapshot()
            dom.data.e = 0x45454545
            with changer.change([dom.data.e]) as changed:
                assert changed == binary("\x31EEEE") # 0x31 = 0b00110001

            dom._pfp__restore_snapshot()
            assert changer.build() == binary("\x31eeee") # 0x31 = 0b00110001

        dom._pfp__restore_snapshot()
        assert changer.build() == binary("\x0feeee")  # 0x0f = 0b00001111

    dom._pfp__restore_snapshot()
    assert changer.build() == binary(data)
