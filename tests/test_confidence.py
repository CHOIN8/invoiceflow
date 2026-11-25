
from invoiceflow.confidence import ConfidenceLevel


def test_high_confidence_does_not_require_review():
    assert ConfidenceLevel.HIGH.requires_review is False


def test_medium_confidence_requires_review():
    assert ConfidenceLevel.MEDIUM.requires_review is True


def test_low_confidence_requires_review():
    assert ConfidenceLevel.LOW.requires_review is True
