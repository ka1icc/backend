"""API endpoints for flight search results."""

from typing import Any, Dict, List, Optional

from flask import Blueprint, jsonify

from app.models import FlightResult

flights_bp = Blueprint('flights', __name__)


def _sort_by_price(option: FlightResult) -> float:
    """Sort key: price as float."""
    return float(option.price)


def _sort_by_duration(option: FlightResult) -> int:
    """Sort key: duration in minutes."""
    return option.duration_minutes


def _find_optimal(options: List[FlightResult]) -> Optional[FlightResult]:
    """Find the option with the best price-to-duration ratio (normalized)."""
    if not options:
        return None

    prices = [float(opt.price) for opt in options]
    durations = [opt.duration_minutes for opt in options]
    min_price = min(prices)
    max_price = max(prices)
    min_dur = min(durations)
    max_dur = max(durations)

    price_range = max_price - min_price or 1.0
    dur_range = max_dur - min_dur or 1

    def score(option: FlightResult) -> float:
        norm_price = (float(option.price) - min_price) / price_range
        norm_dur = (option.duration_minutes - min_dur) / dur_range
        return norm_price + norm_dur

    return min(options, key=score)


@flights_bp.route('/flights', methods=['GET'])
def list_flights():
    """Return all DXB to BKK flight options from both sources."""
    options = FlightResult.query.order_by(FlightResult.price).all()
    return jsonify({
        'from': 'DXB',
        'to': 'BKK',
        'total': len(options),
        'flights': [opt.to_dict() for opt in options],
    })


@flights_bp.route('/flights/extremes', methods=['GET'])
def extremes():
    """Return cheapest, most expensive, fastest, slowest, and optimal."""
    options = list(FlightResult.query.all())
    if not options:
        return jsonify({
            'cheapest': None,
            'most_expensive': None,
            'fastest': None,
            'slowest': None,
            'optimal': None,
        })

    by_price = sorted(options, key=_sort_by_price)
    by_dur = sorted(options, key=_sort_by_duration)
    optimal = _find_optimal(options)

    return jsonify({
        'cheapest': by_price[0].to_dict(),
        'most_expensive': by_price[-1].to_dict(),
        'fastest': by_dur[0].to_dict(),
        'slowest': by_dur[-1].to_dict(),
        'optimal': optimal.to_dict() if optimal else None,
    })


@flights_bp.route('/diff', methods=['GET'])
def diff():
    """Compare results from the two XML sources."""
    via3_map: Dict[str, FlightResult] = {
        opt.route_key: opt
        for opt in FlightResult.query.filter_by(source_file='via3').all()
    }
    viaow_map: Dict[str, FlightResult] = {
        opt.route_key: opt
        for opt in FlightResult.query.filter_by(source_file='viaow').all()
    }

    only_via3 = [
        opt.to_dict()
        for key, opt in via3_map.items()
        if key not in viaow_map
    ]
    only_viaow = [
        opt.to_dict()
        for key, opt in viaow_map.items()
        if key not in via3_map
    ]

    shared: List[Dict[str, Any]] = []
    for key, opt3 in via3_map.items():
        if key not in viaow_map:
            continue
        optow = viaow_map[key]
        shared.append({
            'route_key': key,
            'via3': opt3.to_dict(),
            'viaow': optow.to_dict(),
            'price_diff': round(float(optow.price) - float(opt3.price), 2),
            'duration_diff_minutes': optow.duration_minutes - opt3.duration_minutes,
        })

    return jsonify({
        'summary': {
            'via3_total': len(via3_map),
            'viaow_total': len(viaow_map),
            'only_in_via3': len(only_via3),
            'only_in_viaow': len(only_viaow),
            'in_both': len(shared),
        },
        'only_in_via3': only_via3,
        'only_in_viaow': only_viaow,
        'in_both_with_differences': shared,
    })
