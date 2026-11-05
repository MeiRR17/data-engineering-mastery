"""Reference implementation for maintainer CI; learner should solve first."""
import math
import re
from datetime import datetime, timezone

class ValidationError(ValueError):
    pass


def number(value, field, low, high, nullable=False):
    if nullable and value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValidationError(f"{field} must be finite numeric")
    if not low <= value <= high:
        raise ValidationError(f"{field} out of bounds")
    return float(value)


def timestamp(value):
    if isinstance(value, bool) or not isinstance(value, (int,float)) or not math.isfinite(value):
        raise ValidationError("timestamp must be epoch milliseconds")
    try:
        return datetime.fromtimestamp(value / 1000, tz=timezone.utc).isoformat()
    except (OSError, ValueError, OverflowError) as exc:
        raise ValidationError("timestamp out of range") from exc


def normalize_feature(feature):
    if not isinstance(feature, dict) or feature.get("type") != "Feature":
        raise ValidationError("expected GeoJSON Feature")
    eid = feature.get("id")
    if not isinstance(eid, str) or not re.fullmatch(r"[a-zA-Z0-9_-]{1,64}", eid):
        raise ValidationError("invalid event id")
    props, geom = feature.get("properties"), feature.get("geometry")
    if not isinstance(props, dict) or not isinstance(geom, dict) or geom.get("type") != "Point":
        raise ValidationError("missing properties or Point geometry")
    coords = geom.get("coordinates")
    if not isinstance(coords, list) or len(coords) < 3:
        raise ValidationError("coordinates must include longitude, latitude and depth")
    if props.get("type") != "earthquake":
        raise ValidationError("not an earthquake")
    time = timestamp(props.get("time"))
    updated = timestamp(props.get("updated"))
    if updated < time:
        raise ValidationError("updated before observed")
    place = props.get("place")
    if place is not None and not isinstance(place, str):
        raise ValidationError("place must be text or null")
    return {
        "event_id": eid,
        "observed_at": time,
        "source_updated_at": updated,
        "magnitude": number(props.get("mag"), "magnitude", -5, 12, nullable=True),
        "longitude": number(coords[0], "longitude", -180, 180),
        "latitude": number(coords[1], "latitude", -90, 90),
        "depth_km": number(coords[2], "depth", -50, 1000),
        "place": (place or "Unknown")[:300],
    }


def clean_batch(features):
    if not isinstance(features, list):
        raise ValidationError("expected list of features")
    valid, rejected = [], []
    for index, feature in enumerate(features):
        try:
            valid.append(normalize_feature(feature))
        except ValidationError as exc:
            rejected.append({"index": index, "reason": str(exc)})
    return {"valid": valid, "rejected": rejected}
