"""XML parser for Via.com API responses."""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional

from sqlalchemy.orm import Session

from app.models import FlightSegment, Route, XmlResponse


def _el_text(
    element: Optional[ET.Element],
    default: str = '',
) -> str:
    """Extract stripped text content from an XML element."""
    if element is None:
        return default
    return (element.text or '').strip()


def _parse_segment(
    flight_el: ET.Element,
    direction: str,
    order: int,
) -> FlightSegment:
    """Parse a single <Flight> XML element into a model."""
    carrier = flight_el.find('Carrier')
    carrier_id = ''
    carrier_name = ''
    if carrier is not None:
        carrier_id = carrier.get('id', '')
        carrier_name = _el_text(carrier)

    return FlightSegment(
        direction=direction,
        segment_order=order,
        carrier_id=carrier_id,
        carrier_name=carrier_name,
        flight_number=_el_text(
            flight_el.find('FlightNumber'),
        ),
        source=_el_text(flight_el.find('Source')),
        destination=_el_text(
            flight_el.find('Destination'),
        ),
        departure_ts=_el_text(
            flight_el.find('DepartureTimeStamp'),
        ),
        arrival_ts=_el_text(
            flight_el.find('ArrivalTimeStamp'),
        ),
        class_code=_el_text(flight_el.find('Class')),
        ticket_type=_el_text(
            flight_el.find('TicketType'),
        ),
    )


def _extract_adult_total(
    pricing_el: Optional[ET.Element],
) -> tuple:
    """Return (total_amount, currency) for SingleAdult."""
    if pricing_el is None:
        return None, ''
    currency = pricing_el.get('currency', '')
    for charge in pricing_el.findall('ServiceCharges'):
        ptype = charge.get('type', '')
        ctype = charge.get('ChargeType', '')
        is_adult_total = (
            ptype == 'SingleAdult'
            and ctype == 'TotalAmount'
        )
        if is_adult_total:
            try:
                return float(_el_text(charge)), currency
            except (ValueError, TypeError):
                return None, currency
    return None, currency


def _parse_flights_block(
    flights_el: ET.Element,
    index: int,
) -> Route:
    """Parse one <Flights> block into a Route with segments."""
    onward_el = flights_el.find('OnwardPricedItinerary')
    return_el = flights_el.find('ReturnPricedItinerary')
    pricing_el = flights_el.find('Pricing')

    total, currency = _extract_adult_total(pricing_el)

    segments: list[FlightSegment] = []

    if onward_el is not None:
        for idx, flight in enumerate(
            onward_el.findall('.//Flight'),
        ):
            segments.append(
                _parse_segment(flight, 'onward', idx),
            )

    has_return = False
    if return_el is not None:
        ret_flights = return_el.find('Flights')
        if ret_flights is not None:
            has_return = True
            for idx, flight in enumerate(
                ret_flights.findall('Flight'),
            ):
                segments.append(
                    _parse_segment(flight, 'return', idx),
                )

    return Route(
        route_index=index,
        is_round_trip=has_return,
        currency=currency,
        total_adult=total,
        segments=segments,
    )


def parse_xml_file(
    path: Path,
    session: Session,
) -> XmlResponse:
    """Parse a Via.com XML file and persist data to DB."""
    tree = ET.parse(path)  # noqa: S314
    root = tree.getroot()

    response = XmlResponse(
        filename=path.name,
        request_time=root.get('RequestTime', ''),
        response_time=root.get('ResponseTime', ''),
    )

    priced = root.find('PricedItineraries')
    if priced is not None:
        for idx, flights_el in enumerate(
            priced.findall('Flights'),
        ):
            route = _parse_flights_block(
                flights_el, idx + 1,
            )
            response.routes.append(route)

    session.add(response)
    session.commit()
    return response
