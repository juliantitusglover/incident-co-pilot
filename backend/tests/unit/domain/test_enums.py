from backend.domain.incidents.enums import Severity, Status


def test_severity_values_are_stable():
    assert Severity.SEV1.value == "sev1"
    assert Severity.SEV2.value == "sev2"
    assert Severity.SEV3.value == "sev3"
    assert Severity.SEV4.value == "sev4"


def test_status_values_are_stable():
    assert Status.OPEN.value == "open"
    assert Status.INVESTIGATING.value == "investigating"
    assert Status.MITIGATED.value == "mitigated"
    assert Status.RESOLVED.value == "resolved"


def test_severity_can_be_constructed_from_value():
    assert Severity("sev1") is Severity.SEV1
    assert Severity("sev2") is Severity.SEV2
    assert Severity("sev3") is Severity.SEV3
    assert Severity("sev4") is Severity.SEV4


def test_status_can_be_constructed_from_value():
    assert Status("open") is Status.OPEN
    assert Status("investigating") is Status.INVESTIGATING
    assert Status("mitigated") is Status.MITIGATED
    assert Status("resolved") is Status.RESOLVED


def test_enums_behave_like_strings():
    assert Severity.SEV1 == "sev1"
    assert Status.OPEN == "open"


def test_enum_iteration_order_is_stable():
    assert list(Severity) == [
        Severity.SEV1,
        Severity.SEV2,
        Severity.SEV3,
        Severity.SEV4,
    ]
    assert list(Status) == [
        Status.OPEN,
        Status.INVESTIGATING,
        Status.MITIGATED,
        Status.RESOLVED,
    ]
