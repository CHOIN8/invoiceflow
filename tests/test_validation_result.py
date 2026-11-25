
import pytest

from invoiceflow.validation.validation_result import ValidationResult


def test_create_empty_validation_result():
    result = ValidationResult()

    assert result.errors == []
    assert result.warnings == []
    assert result.is_valid is True
    assert result.requires_review is False


def test_add_error():
    result = ValidationResult()

    result.add_error("Missing invoice number.")

    assert len(result.errors) == 1
    assert result.is_valid is False
    assert result.requires_review is True


def test_add_warning():
    result = ValidationResult()

    result.add_warning("Low OCR confidence.")

    assert len(result.warnings) == 1
    assert result.is_valid is True
    assert result.requires_review is True


def test_result_with_errors_and_warnings():
    result = ValidationResult()

    result.add_error("Invalid invoice total.")
    result.add_warning("Unusual invoice date.")

    assert result.is_valid is False
    assert result.requires_review is True
    assert len(result.errors) == 1
    assert len(result.warnings) == 1


def test_reject_non_string_error():
    result = ValidationResult()

    with pytest.raises(TypeError, match="Error message"):
        result.add_error(123)


def test_reject_empty_error():
    result = ValidationResult()

    with pytest.raises(ValueError, match="cannot be empty"):
        result.add_error("   ")


def test_reject_non_string_warning():
    result = ValidationResult()

    with pytest.raises(TypeError, match="Warning message"):
        result.add_warning(123)


def test_reject_empty_warning():
    result = ValidationResult()

    with pytest.raises(ValueError, match="cannot be empty"):
        result.add_warning("   ")


def test_validation_results_have_independent_lists():
    first = ValidationResult()
    second = ValidationResult()

    first.add_error("First error.")

    assert second.errors == []
