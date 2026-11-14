from netaudit.audit import (
    check_acl_applied_undefined,
    check_acl_never_applied,
    check_acl_shadowed_rules,
    check_acl_subnet_mask,
)
from netaudit.parsers.ios import parse_ios


def _dev(body):
    return parse_ios("hostname r1\n" + body)


def test_acl_applied_but_undefined_is_reported():
    d = _dev("interface Gi0/0\n ip address 10.0.0.1 255.255.255.0\n ip access-group NOPE in\n")
    findings = check_acl_applied_undefined(d)
    assert len(findings) == 1
    assert findings[0].severity == "error"
    assert "NOPE" in findings[0].message


def test_acl_applied_and_defined_is_fine():
    d = _dev(
        "ip access-list extended WEB\n permit ip any any\n"
        "interface Gi0/0\n ip address 10.0.0.1 255.255.255.0\n ip access-group WEB in\n"
    )
    assert check_acl_applied_undefined(d) == []


def test_acl_never_applied_is_reported():
    d = _dev("ip access-list extended WEB\n permit ip any any\n")
    findings = check_acl_never_applied(d)
    assert len(findings) == 1
    assert findings[0].severity == "warning"
    assert "WEB" in findings[0].message


def test_acl_that_is_applied_is_not_reported_as_unused():
    d = _dev(
        "ip access-list extended WEB\n permit ip any any\n"
        "interface Gi0/0\n ip address 10.0.0.1 255.255.255.0\n ip access-group WEB out\n"
    )
    assert check_acl_never_applied(d) == []


def test_rules_after_permit_any_any_are_shadowed():
    d = _dev(
        "ip access-list extended WEB\n"
        " permit ip any any\n"
        " deny tcp 192.168.1.0 0.0.0.255 any eq 80\n"
    )
    findings = check_acl_shadowed_rules(d)
    assert len(findings) == 1
    assert findings[0].severity == "warning"
    assert "WEB" in findings[0].message


def test_permit_any_any_as_last_rule_is_fine():
    d = _dev(
        "ip access-list extended WEB\n"
        " deny tcp 192.168.1.0 0.0.0.255 any eq 80\n"
        " permit ip any any\n"
    )
    assert check_acl_shadowed_rules(d) == []


def test_subnet_mask_written_instead_of_wildcard_is_reported():
    d = _dev("ip access-list extended WEB\n permit ip 192.168.1.0 255.255.255.0 any\n")
    findings = check_acl_subnet_mask(d)
    assert len(findings) == 1
    assert findings[0].severity == "error"
    assert "255.255.255.0" in findings[0].message


def test_wildcard_and_host_are_fine():
    d = _dev(
        "ip access-list extended WEB\n"
        " permit ip 192.168.1.0 0.0.0.255 host 10.0.0.5\n"
        " permit ip any any\n"
    )
    assert check_acl_subnet_mask(d) == []
