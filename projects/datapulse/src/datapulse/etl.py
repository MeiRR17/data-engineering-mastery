"""Deterministic, testable transformations for the USGS GeoJSON feed."""

from __future__ import annotations

import hashlib
import json
import math
import re
from datetime import datetime, timezone
from typing import Any


class DataQualityError(ValueError):
    """A source record cannot be stored without violating our data contract."""


def ms_to_iso(value: Any) -> str:
    if isinstance(value, bool) or not isinstance(value, (float, int)):
        raise DataQualityError("timestamp must be numeric Unix milliseconds")
    if not math.isfinite(value):
        raise DataQualityError("timestamp must be finite")
    try:
        return datetime.fromtimestamp(value / 1000, tz=timezone.utc).isoformat()
    except (OverflowError, OSError, ValueError) as exc:
        raise DataQualityError("timestamp out of range") from exc


def finite_number(value: Any, field: str, low: float, high: float, nullable: bool = False) -> float | None:
    if value is None and nullable:
        return None
    if isinstance(value, bool) or not isinstance(value, (float, int)):
        raise DataQualityError(f"{field} must be numeric")
    num = float(value)
    if not math.isfinite(num) or not low <= num <= high:
        raise DataQualityError(f"{field} out of range")
    return num


def normalize(feature: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(feature, dict) or feature.get("type") != "Feature":
        raise DataQualityError("expected GeoJSON Feature")
    event_id = feature.get("id")
    if not isinstance(event_id, str) or not re.fullmatch(r"[a-zA-Z0-9_-]{1,64}", event_id):
        raise DataQualityError("invalid USGS event ID")
    props, geom = feature.get("properties"), feature.get("geometry")
    if not isinstance(props, dict) or not isinstance(geom, dict) or geom.get("type") != "Point":
        raise DataQualityError("missing properties or point geometry")
    coords = geom.get("coordinates")
    if not isinstance(coords, list) or len(coords) < 3:
        raise DataQualityError("expected [longitude, latitude, depth] coordinates")
    if props.get("type") != "earthquake":
        raise DataQualityError("non-earthquake feature")
    observed_at = ms_to_iso(props.get("time"))
    updated_at = ms_to_iso(props.get("updated"))
    if updated_at < observed_at:
        raise DataQualityError("updated timestamp precedes event timestamp")
    longitude = finite_number(coords[0], "longitude", -180, 180)
    latitude = finite_number(coords[1], "latitude", -90, 90)
    depth = finite_number(coords[2], "depth_km", -50, 1000)
    magnitude = finite_number(props.get("mag"), "magnitude", -5, 12, nullable=True)
    place = props.get("place")
    if place is not None and not isinstance(place, str):
        raise DataQualityError("place must be text")
    source_url = props.get("url")
    if not isinstance(source_url, str) or not source_url.startswith("https://earthquake.usgs.gov/"):
        raise DataQualityError("missing or unexpected USGS source URL")
    raw_json = json.dumps(feature, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return {
        "event_id": event_id,
        "observed_at": observed_at,
        "source_updated_at": updated_at,
        "magnitude": magnitude,
        "place": (place or "Unknown")[:300],
        "longitude": longitude,
        "latitude": latitude,
        "depth_km": depth,
        "source_url": source_url,
        "payload_sha256": hashlib.sha256(raw_json.encode("utf-8")).hexdigest(),
        "raw_payload": feature,
    }


def transform_feed(feed: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    if not isinstance(feed, dict) or feed.get("type") != "FeatureCollection":
        raise DataQualityError("expected a GeoJSON FeatureCollection")
    features = feed.get("features")
    if not isinstance(features, list):
        raise DataQualityError("features must be an array")
    rows: dict[str, dict[str, Any]] = {}
    rejects: list[dict[str, str]] = []
    for index, feature in enumerate(features):
        try:
            row = normalize(feature)
            old = rows.get(row["event_id"])
            if old is None or row["source_updated_at"] >= old["source_updated_at"]:
                rows[row["event_id"]] = row
        except DataQualityError as exc:
            rejects.append({"index": str(index), "reason": str(exc)})
    return list(rows.values()), rejects
