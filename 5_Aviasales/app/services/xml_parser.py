"""Parse partner XML responses and load flight data into the database."""

import os
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from app.extensions import db
from app.models import FlightResult

ORIGIN = 'DXB'
DESTINATION = 'BKK'


def parse_timestamp(raw: str) -> Optional[datetime]:
    """Convert '2018-10-22T0005' to a datetime object."""
    text = (raw or '').strip()
    min_length = 15
    if len(text) < min_length:
        return None
    normalized = '{0} {1}:{2}'.format(text[:10], text[11:13], text[13:15])
    try:
        return datetime.strptime(normalized, '%Y-%m-%d %H:%M')
    except ValueError:
        return None


def _extract_total_price(pricing_el: ET.Element) -> Tuple[float, str]:
    """Return (total_amount, currency) for SingleAdult."""
    currency = pricing_el.get('currency', 'SGD')
    for charge in pricing_el.findall('ServiceCharges'):
        is_adult = charge.get('type') == 'SingleAdult'
        is_total = charge.get('ChargeType') == 'TotalAmount'
        if is_adult and is_total:
            return float((charge.text or '0').strip()), currency
    return 0.0, currency


def _build_segment(flight_el: ET.Element) -> Dict[str, object]:
    """Convert one <Flight> element to a segment dict."""
    carrier_el = flight_el.find('Carrier')
    carrier_id = ''
    carrier_name = ''
    if carrier_el is not None:
        carrier_id = carrier_el.get('id', '')
        carrier_name = (carrier_el.text or '').strip()

    return {
        'carrier_id': carrier_id,
        'carrier_name': carrier_name,
        'flight_number': (flight_el.findtext('FlightNumber') or '').strip(),
        'source': (flight_el.findtext('Source') or '').strip(),
        'destination': (flight_el.findtext('Destination') or '').strip(),
        'departure': (flight_el.findtext('DepartureTimeStamp') or '').strip(),
        'arrival': (flight_el.findtext('ArrivalTimeStamp') or '').strip(),
        'class': (flight_el.findtext('Class') or '').strip(),
        'stops': int(flight_el.findtext('NumberOfStops') or '0'),
    }


def _segments_from_itinerary(itin_el: Optional[ET.Element]) -> List[Dict]:
    """Extract list of segment dicts from an itinerary element."""
    if itin_el is None:
        return []
    flights_el = itin_el.find('Flights')
    if flights_el is None:
        return []
    return [_build_segment(fl) for fl in flights_el.findall('Flight')]


def _compute_route_key(segments: List[Dict]) -> str:
    """Build a unique route key from segment chain."""
    parts = []
    for seg in segments:
        part = '{0}{1}-{2}-{3}'.format(
            seg['carrier_id'],
            seg['flight_number'],
            seg['source'],
            seg['destination'],
        )
        parts.append(part)
    return '|'.join(parts)


def _compute_duration(segments: List[Dict]) -> int:
    """Duration in minutes from first departure to last arrival."""
    if not segments:
        return 0
    dep = parse_timestamp(segments[0].get('departure', ''))
    arr = parse_timestamp(segments[-1].get('arrival', ''))
    if dep is None or arr is None:
        return 0
    seconds_per_minute = 60
    return int((arr - dep).total_seconds() / seconds_per_minute)


def _is_dxb_to_bkk(segments: List[Dict]) -> bool:
    """Check if the onward route goes from DXB to BKK."""
    if not segments:
        return False
    return (
        segments[0].get('source') == ORIGIN
        and segments[-1].get('destination') == DESTINATION
    )


def _parse_single_xml(filepath: Path, source_name: str) -> List[Dict]:
    """Parse one XML file and return a list of option dicts."""
    tree = ET.parse(filepath)
    root = tree.getroot()
    itineraries_el = root.find('PricedItineraries')
    if itineraries_el is None:
        return []

    options = []
    for block in itineraries_el.findall('Flights'):
        onward_segments = _segments_from_itinerary(
            block.find('OnwardPricedItinerary'),
        )
        if not _is_dxb_to_bkk(onward_segments):
            continue

        pricing_el = block.find('Pricing')
        if pricing_el is None:
            continue
        price, currency = _extract_total_price(pricing_el)
        if price <= 0:
            continue

        return_segments = _segments_from_itinerary(
            block.find('ReturnPricedItinerary'),
        )

        options.append({
            'source_file': source_name,
            'is_round_trip': bool(return_segments),
            'price': price,
            'currency': currency,
            'duration_minutes': _compute_duration(onward_segments),
            'route_key': _compute_route_key(onward_segments),
            'onward_segments': onward_segments,
            'return_segments': return_segments,
        })
    return options


def load_xml_into_db(data_dir: str) -> int:
    """
    Parse both XML files and insert results into the database.

    Returns total number of options inserted.
    """
    files = [
        ('RS_Via-3.xml', 'via3'),
        ('RS_ViaOW.xml', 'viaow'),
    ]

    db.session.query(FlightResult).delete()

    total = 0
    for filename, source_name in files:
        filepath = Path(data_dir) / filename
        if not filepath.is_file():
            continue
        for option in _parse_single_xml(filepath, source_name):
            row = FlightResult(**option)
            db.session.add(row)
            total += 1

    db.session.commit()
    return total
