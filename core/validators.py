# core/validators.py
from decimal import Decimal
from rest_framework import serializers

def validate_rating_1_to_10(value):
    v = Decimal(str(value))
    if not (Decimal("1.0") <= v <= Decimal("10.0")):
        raise serializers.ValidationError("rating debe estar entre 1.0 y 10.0")
    return value

def validate_price_non_negative(value):
    if value is None:
        return value
    if value < 0:
        raise serializers.ValidationError("el precio no puede ser negativo")
    return value

def validate_non_blank_trimmed(value: str):
    if value is None:
        return value
    if not value.strip():
        raise serializers.ValidationError("este campo no puede estar vacío")
    return value.strip()
