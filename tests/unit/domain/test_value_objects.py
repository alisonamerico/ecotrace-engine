from decimal import Decimal

import pytest

from app.domain.exceptions import (
    InvalidAccessKeyException,
    InvalidCNPJException,
    InvalidMassException,
    InvalidNCMException,
)
from app.domain.value_objects.access_key import AccessKey
from app.domain.value_objects.cnpj import CNPJ
from app.domain.value_objects.mass import RecyclableMass
from app.domain.value_objects.ncm import NCM


def test_access_key_valid() -> None:
    raw_key = "35240112345678000190550010000001231234567890"
    access_key = AccessKey(raw_key)
    assert access_key.value == raw_key
    assert str(access_key) == raw_key
    assert len(access_key.hash_sha256) == 64


def test_access_key_invalid_length() -> None:
    with pytest.raises(InvalidAccessKeyException):
        AccessKey("12345")


def test_access_key_non_digit() -> None:
    with pytest.raises(InvalidAccessKeyException):
        AccessKey("3524011234567800019055001000000123123456789X")


def test_cnpj_valid_unformatted() -> None:
    cnpj = CNPJ("12345678000195")  # Valid test CNPJ
    assert cnpj.value == "12345678000195"
    assert cnpj.formatted == "12.345.678/0001-95"


def test_cnpj_valid_formatted() -> None:
    cnpj = CNPJ("12.345.678/0001-95")
    assert cnpj.value == "12345678000195"
    assert str(cnpj) == "12345678000195"


def test_cnpj_invalid_check_digits() -> None:
    with pytest.raises(InvalidCNPJException):
        CNPJ("12345678000100")


def test_cnpj_invalid_length() -> None:
    with pytest.raises(InvalidCNPJException):
        CNPJ("123")


def test_cnpj_repeated_digits() -> None:
    with pytest.raises(InvalidCNPJException):
        CNPJ("11111111111111")


def test_ncm_valid_plastic() -> None:
    ncm = NCM("3915.10.00")
    assert ncm.code == "39151000"
    assert ncm.is_recyclable is True
    assert ncm.material_family == "PLASTICO"


def test_ncm_valid_paper() -> None:
    ncm = NCM("47071000")
    assert ncm.is_recyclable is True
    assert ncm.material_family == "PAPEL"


def test_ncm_non_recyclable() -> None:
    ncm = NCM("84713012")  # Computers
    assert ncm.is_recyclable is False
    assert ncm.material_family is None


def test_ncm_invalid_code() -> None:
    with pytest.raises(InvalidNCMException):
        NCM("3915")


def test_recyclable_mass_valid() -> None:
    mass = RecyclableMass(Decimal("1500.500"))
    assert mass.value_kg == Decimal("1500.500")
    assert mass.to_tons() == Decimal("1.500500")


def test_recyclable_mass_from_float_or_int() -> None:
    mass1 = RecyclableMass(100)
    assert mass1.value_kg == Decimal("100.000")

    mass2 = RecyclableMass(25.45)
    assert mass2.value_kg == Decimal("25.450")


def test_recyclable_mass_operations() -> None:
    m1 = RecyclableMass(Decimal("100.250"))
    m2 = RecyclableMass(Decimal("50.750"))
    total = m1 + m2
    assert total.value_kg == Decimal("151.000")
    diff = m1 - m2
    assert diff.value_kg == Decimal("49.500")


def test_recyclable_mass_invalid_negative() -> None:
    with pytest.raises(InvalidMassException):
        RecyclableMass(Decimal("-5.000"))


def test_recyclable_mass_invalid_zero() -> None:
    with pytest.raises(InvalidMassException):
        RecyclableMass(Decimal("0.000"))


def test_recyclable_mass_comparisons_and_str() -> None:
    m1 = RecyclableMass(Decimal("100.000"))
    m2 = RecyclableMass(Decimal("200.000"))
    m3 = RecyclableMass(Decimal("100.000"))

    assert m1 < m2
    assert m1 <= m2
    assert m1 <= m3
    assert m2 > m1
    assert m2 >= m1
    assert m1 >= m3
    assert m1 == m3
    assert str(m1) == "100.000 kg"


def test_recyclable_mass_subtraction_underflow() -> None:
    m1 = RecyclableMass(Decimal("50.000"))
    m2 = RecyclableMass(Decimal("100.000"))
    with pytest.raises(InvalidMassException):
        _ = m1 - m2


def test_ncm_str() -> None:
    ncm = NCM("3915.10.00")
    assert str(ncm) == "39151000"


def test_recyclable_mass_invalid_operand_type() -> None:
    m = RecyclableMass(10)
    with pytest.raises(TypeError):
        _ = m + "invalid"  # type: ignore[operator]
    with pytest.raises(TypeError):
        _ = m - 5  # type: ignore[operator]
    with pytest.raises(TypeError):
        _ = m < "invalid"  # type: ignore[operator]
    with pytest.raises(TypeError):
        _ = m <= "invalid"  # type: ignore[operator]
    with pytest.raises(TypeError):
        _ = m > "invalid"  # type: ignore[operator]
    with pytest.raises(TypeError):
        _ = m >= "invalid"  # type: ignore[operator]
