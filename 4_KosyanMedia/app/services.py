"""Business logic for comparing flight routes."""

from typing import Any

from app.models import Route


def _onward_key(route: Route) -> tuple:
    """Build a comparison key from onward flight segments."""
    onward = [
        seg for seg in route.segments
        if seg.direction == 'onward'
    ]
    onward.sort(key=lambda seg: seg.segment_order)
    return tuple(
        (
            seg.carrier_id,
            seg.flight_number,
            seg.source,
            seg.destination,
        )
        for seg in onward
    )


def _segment_info(segment) -> dict[str, str]:
    """Format a single flight segment for display."""
    return {
        'carrier': '{0} {1}'.format(
            segment.carrier_id,
            segment.flight_number,
        ),
        'route': '{0} -> {1}'.format(
            segment.source,
            segment.destination,
        ),
        'departure': segment.departure_ts,
        'arrival': segment.arrival_ts,
        'class_code': segment.class_code,
    }


def _route_info(route: Route) -> dict[str, Any]:
    """Extract display-ready info from a Route object."""
    onward = sorted(
        [s for s in route.segments if s.direction == 'onward'],
        key=lambda s: s.segment_order,
    )
    ret = sorted(
        [s for s in route.segments if s.direction == 'return'],
        key=lambda s: s.segment_order,
    )

    all_segs = onward + ret
    start = onward[0].departure_ts if onward else ''
    if ret:
        end = ret[-1].arrival_ts
    elif onward:
        end = onward[-1].arrival_ts
    else:
        end = ''

    return {
        'flights': [_segment_info(s) for s in all_segs],
        'start_time': start,
        'end_time': end,
        'price': route.total_adult,
        'currency': route.currency,
        'is_round_trip': route.is_round_trip,
        'classes': [s.class_code for s in all_segs],
    }


def _detect_changes(
    info1: dict[str, Any],
    info2: dict[str, Any],
) -> list[str]:
    """Detect what changed between two route versions."""
    changes: list[str] = []

    price1 = info1['price']
    price2 = info2['price']
    if price1 is not None and price2 is not None:
        if price1 != price2:
            changes.append(
                'цена: {0} -> {1}'.format(price1, price2),
            )

    if info1['start_time'] != info2['start_time']:
        changes.append('даты/время вылета')

    if info1['is_round_trip'] != info2['is_round_trip']:
        changes.append('тип маршрута (RT / OW)')

    return changes


def _chain_label(key: tuple) -> str:
    """Build a human-readable label for a route chain."""
    return ' -> '.join(
        '{0}{1} {2}-{3}'.format(
            carrier, flight, src, dst,
        )
        for carrier, flight, src, dst in key
    )


def compare_routes(
    routes_1: list[Route],
    routes_2: list[Route],
) -> dict[str, Any]:
    """Compare two sets of routes, return structured diff."""
    by_key_1: dict[tuple, list[Route]] = {}
    by_key_2: dict[tuple, list[Route]] = {}

    for route in routes_1:
        key = _onward_key(route)
        by_key_1.setdefault(key, []).append(route)

    for route in routes_2:
        key = _onward_key(route)
        by_key_2.setdefault(key, []).append(route)

    keys_only_1 = set(by_key_1) - set(by_key_2)
    keys_only_2 = set(by_key_2) - set(by_key_1)
    keys_common = set(by_key_1) & set(by_key_2)

    new_routes = [
        _route_info(by_key_2[key][0])
        for key in sorted(keys_only_2)
    ]

    removed_routes = [
        _route_info(by_key_1[key][0])
        for key in sorted(keys_only_1)
    ]

    changed_routes = []
    for key in sorted(keys_common):
        info1 = _route_info(by_key_1[key][0])
        info2 = _route_info(by_key_2[key][0])
        changes = _detect_changes(info1, info2)
        changed_routes.append({
            'chain': _chain_label(key),
            'file1': info1,
            'file2': info2,
            'changes': changes,
        })

    return {
        'new_routes': new_routes,
        'removed_routes': removed_routes,
        'changed_routes': changed_routes,
        'summary': {
            'total_file1': len(routes_1),
            'total_file2': len(routes_2),
            'new_count': len(keys_only_2),
            'removed_count': len(keys_only_1),
            'common_count': len(keys_common),
        },
    }
