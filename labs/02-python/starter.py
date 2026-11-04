"""Stage 02 learner starter. Edit this file; no network required."""

class ValidationError(ValueError):
    """A row violates the stated data contract."""


def normalize_feature(feature):
    """Return normalized event dict from a GeoJSON feature. See README for contract."""
    raise NotImplementedError("Implement validation and normalization first")


def clean_batch(features):
    """Return {'valid': [...], 'rejected': [{'index': int, 'reason': str}, ...]}."""
    raise NotImplementedError("Use normalize_feature and collect invalid rows")
