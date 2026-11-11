from netaudit.parsers.ios import parse_ios

BASIC = """hostname r1
!
ip access-list extended BLOCK_WEB
 deny tcp 192.168.1.0 0.0.0.255 any eq 80
 permit ip any any
!
access-list 10 permit 10.0.0.0 0.0.0.255
access-list 110 deny ip host 1.1.1.1 any
!
interface Gi0/0
 ip address 192.168.1.1 255.255.255.0
 ip access-group BLOCK_WEB in
 ip access-group 110 out
!
end
"""


def test_named_and_numbered_acls_and_their_use_on_an_interface():
    d = parse_ios(BASIC)
    assert list(d.acls) == ["BLOCK_WEB", "10", "110"]
    first, second = d.acls["BLOCK_WEB"]
    assert (first.action, first.protocol) == ("deny", "tcp")
    assert first.source == "192.168.1.0 0.0.0.255"
    assert first.destination == "any"
    assert second.source == "any" and second.destination == "any"
    standard = d.acls["10"][0]
    assert standard.protocol == "" and standard.destination == ""
    assert standard.source == "10.0.0.0 0.0.0.255"
    assert d.acls["110"][0].source == "host 1.1.1.1"
    iface = d.interfaces["Gi0/0"]
    assert iface.acl_in == "BLOCK_WEB" and iface.acl_out == "110"
    assert d.unparsed == []


def test_sequence_numbers_and_remarks_are_handled():
    d = parse_ios(
        "ip access-list extended X\n"
        " remark allow everything\n"
        " 10 permit ip any any\n"
    )
    assert [r.line for r in d.acls["X"]] == ["permit ip any any"]
    assert d.unparsed == []


def test_unsupported_rule_goes_to_unparsed_not_half_read():
    d = parse_ios(
        "ip access-list extended X\n"
        " permit ip any any dscp ef\n"
    )
    assert d.acls["X"] == []
    assert len(d.unparsed) == 1
    assert d.unparsed[0].line == "permit ip any any dscp ef"
    assert d.unparsed[0].context == "ip access-list X"
