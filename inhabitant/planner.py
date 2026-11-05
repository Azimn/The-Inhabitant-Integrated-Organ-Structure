"""Bounded, evidence-limited search rather than DUCK's predefined route fallback.

The planner receives only known action receipts, admitted observations, the
subject's body/stock information, and current location. Hidden world values
(pump state, spare-part availability, barrel contents) are never read directly.
The external world remains authoritative when an attempted action executes.
"""
from collections import deque
import re


PLACES = ("cabin", "garden", "spring", "workshop")


def known_affordances(events, *, use_memory=True):
    pump_working = True             # Unverified working assumption, not a world fact.
    spare_available = True          # Unverified until repair attempt.
    rain = None                     # A hidden resource until observed.
    visits = {"cabin"}
    for event in events:
        kind, p = event["kind"], event["payload"]
        if kind == "action" and p.get("success") and p.get("action", "").startswith("move_"):
            visits.add(p["action"].removeprefix("move_"))
        if kind == "perception" and p.get("class") == "observed":
            text = p["text"].casefold()
            if "pump is broken" in text:
                pump_working = False
            if "pump was repaired" in text:
                pump_working = True
            # Observations of a past failure are consulted only through episodic
            # memory on later turns; Sensus is not a free autobiographical oracle.
            if "rain barrel contains" in text:
                match = re.search(r"contains (\d+) measure", text)
                if match:
                    rain = max(0, min(3, int(match.group(1))))
            if "barrel to 2 measures" in text:
                rain = 2
        if use_memory and kind == "action":
            if p.get("action") == "repair_pump" and not p.get("success"):
                spare_available = False
            if p.get("action") == "repair_pump" and p.get("success"):
                pump_working = True
                spare_available = False
            if p.get("action") == "collect_rain" and p.get("success") and rain is not None:
                rain = max(0, rain - 2)
    return {"pump": pump_working, "spare": spare_available,
            "rain": rain, "visited": visits}


def successors(state):
    """Model physical affordances, not fixed goals, routes, or scripted outcomes."""
    place, water, pump, spare, rain = state
    if place == "spring" and pump and water < 3:
        yield "collect_water", ("spring", 3, pump, spare, rain)
    if place == "garden" and rain is not None and rain > 0 and water < 3:
        amount = min(2, rain)
        yield "collect_rain", ("garden", min(3, water + amount), pump, spare, rain - amount)
    if place == "workshop" and not pump and spare:
        yield "repair_pump", (place, water, True, False, rain)
    for destination in PLACES:
        if destination != place:
            yield "move_" + destination, (destination, water, pump, spare, rain)


def search_water_route(place, water, known, *, max_depth=6):
    start = (place, min(3, water), known["pump"], known["spare"], known["rain"])
    frontier = deque([(start, ())])
    visited = {start}
    while frontier:
        state, route = frontier.popleft()
        if state[1] >= 3:
            return route
        if len(route) >= max_depth:
            continue
        for action, next_state in successors(state):
            if next_state not in visited:
                visited.add(next_state)
                frontier.append((next_state, route + (action,)))
    return ()


def plan_water(events, state, *, use_memory=True, affect_enabled=True):
    known = known_affordances(events, use_memory=use_memory)
    water = state["stocks"]["water"]
    route = search_water_route(state["place"], water, known)
    if route:
        if route[0] == "repair_pump":
            return route[0], "route search: repair predicted feasible from available evidence", route
        return route[0], "route search: shortest feasible affordance sequence", route
    # With no evidenced solution, explore an unvisited location to acquire
    # new affordances. No rain-barrel target has been predefined.
    unknown = [p for p in PLACES if p not in known["visited"]]
    if unknown:
        destination = unknown[0]
        return "move_" + destination, "information-seeking exploration", ()
    return "inspect", "no currently evidenced feasible route", ()
