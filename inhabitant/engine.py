"""One synthetic life with a canonical append-only event history.

Donor engines are real imported source, but their stores are advisory projections.
Only Archive may declare world, identity, delivered speech, and commitment facts.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import asdict
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import copy
import json
import random
import re
import sqlite3
import time

from vendor.sensus_artificialis.core import Evidence, Percept, Sensus
from vendor.synthetic_ipseity.core import Ipseity, Kind, MemoryClass, SourceSignal, render_frame
from vendor.duck.living import SubjectState, WorldEvent
from vendor.duck.living_v09 import LivingDuck
from vendor.noetic_engine.engine import NoeticEngine
from vendor.noetic_engine.models import Configuration, Observation, EvidenceClass
from vendor.doctor_lives.speech_emission import SpeechEmissionJournal, SpeechSinkAck, digest


def encode(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def initial(name="PROTO-1"):
    return {
        "id": "prototype-subject-1", "name": name, "day": 0, "place": "cabin",
        "stocks": {"food": 2, "water": 1, "fuel": 2},
        "body": {"thirst": .42, "hunger": .28, "cold": .18, "fatigue": .15},
        "pump": "working", "spare_part": True, "rain": 2, "door": "closed",
        "visitor": False, "goals": {}, "weather": "cool",
    }


class Archive:
    """Single canonical authority. Every update is an append-only transition."""

    def __init__(self, path):
        self.path = str(path)
        self.db = sqlite3.connect(self.path)
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("PRAGMA synchronous=FULL")
        self.db.execute("""CREATE TABLE IF NOT EXISTS events(
            seq INTEGER PRIMARY KEY, kind TEXT NOT NULL, payload TEXT NOT NULL,
            prev TEXT NOT NULL, hash TEXT NOT NULL, utc TEXT NOT NULL)""")
        self.db.commit()

    def events(self):
        return [{"seq": row[0], "kind": row[1], "payload": json.loads(row[2]),
                 "prev": row[3], "hash": row[4], "utc": row[5]}
                for row in self.db.execute(
                    "SELECT seq,kind,payload,prev,hash,utc FROM events ORDER BY seq")]

    def append(self, kind, payload):
        payload = copy.deepcopy(payload)
        last = self.db.execute("SELECT seq,hash FROM events ORDER BY seq DESC LIMIT 1").fetchone()
        seq, prev = (last[0] + 1, last[1]) if last else (1, "GENESIS")
        core = encode({"seq": seq, "kind": kind, "payload": payload, "prev": prev})
        checksum = sha256(core.encode()).hexdigest()
        utc = datetime.now(timezone.utc).isoformat()
        with self.db:
            self.db.execute("INSERT INTO events VALUES(?,?,?,?,?,?)",
                            (seq, kind, encode(payload), prev, checksum, utc))
        return seq

    def verify(self):
        prev = "GENESIS"
        for index, e in enumerate(self.events(), 1):
            core = encode({"seq": index, "kind": e["kind"],
                           "payload": e["payload"], "prev": prev})
            expected = sha256(core.encode()).hexdigest()
            if e["seq"] != index or e["prev"] != prev or e["hash"] != expected:
                raise ValueError("Canonical ledger tampering at event " + str(index))
            prev = expected
        return True

    def state(self):
        result = None
        for e in self.events():
            p = e["payload"]
            if e["kind"] == "genesis":
                result = copy.deepcopy(p)
            elif e["kind"] in {"day", "change", "action"}:
                if result is None:
                    raise ValueError("Missing genesis")
                for key, value in p.get("changes", {}).items():
                    result[key] = copy.deepcopy(value)
            elif e["kind"] == "goal":
                if result is None:
                    raise ValueError("Missing genesis")
                old = result["goals"].get(p["goal_id"], {})
                result["goals"][p["goal_id"]] = {**old, **p}
        if result is None:
            raise ValueError("Missing genesis")
        return result

    def close(self):
        self.db.close()


class Inhabitant:
    """Single-authority runtime. Sensus -> Ipseity -> memory -> Noesis/Telos -> Corpus."""

    def __init__(self, root, *, disabled=(), name="PROTO-1"):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.archive = Archive(self.root / "life.sqlite3")
        if not self.archive.events():
            self.archive.append("genesis", initial(name))
        self.archive.verify()
        self.disabled = frozenset(disabled)
        self.subject_id = self.archive.state()["id"]
        self.sensus = Sensus()
        self.ipseity = Ipseity(capacity=6)
        self.duck = LivingDuck(SubjectState.create(
            name=self.archive.state()["name"], subject_id=self.subject_id))
        self.noetic = NoeticEngine(config=Configuration(subject_id=self.subject_id))
        self.speech = SpeechEmissionJournal(self.root)
        self.last_frame = ""
        self.last_causal = {}
        self._restore_projection()

    def _restore_projection(self):
        entries = self.archive.events()
        snaps = [e for e in entries if e["kind"] == "duck_projection"]
        if snaps:
            self.duck = LivingDuck(SubjectState.from_dict(snaps[-1]["payload"]["state"]))
        for e in entries:
            p = e["payload"]
            if e["kind"] == "sensed":
                percepts = [Percept(
                    event_id=x["event_id"], channel=x["channel"], evidence=Evidence(x["evidence"]),
                    source_ref=x["source_ref"], tick=p["tick"], attribute=x["attribute"],
                    value=x["value"], confidence=x["confidence"], object_hint=x.get("object_hint", "")
                ) for x in p["percepts"]]
                self.sensus.step(p["tick"], percepts)
            if e["kind"] == "noetic_input":
                self.noetic.step(Observation(
                    origin_id=str(e["seq"]), subject_id=self.subject_id,
                    text=p["text"], source=p["source"], evidence_class=EvidenceClass(p["class"]),
                    actor_id=p.get("actor", "environment"),
                    affect_delta=p.get("affect_delta", {})))
        self.reconcile_speech()

    def reconcile_speech(self):
        """The native two-phase speech journal can ACK before the main ledger append."""
        existing = {e["payload"]["key"] for e in self.archive.events() if e["kind"] == "speech"}
        db = self.speech._db
        for row in db.execute(
            "SELECT delivery_key,content,content_sha256,sink_id FROM emissions WHERE state='acknowledged'"):
            key, text, checksum, sink = row
            if key not in existing:
                if digest(text) != checksum:
                    raise ValueError("Speech ACK integrity mismatch")
                self.archive.append("speech", {"key": key, "text": text, "sink": sink,
                                              "checksum": checksum, "ack": True})

    def state(self):
        return self.archive.state()

    def event(self, kind, payload):
        return self.archive.append(kind, payload)

    def intake(self, text, *, source="", attested=False, evidence="told"):
        """Do not trust claimed evidence classes from input text or callers."""
        if not source or not attested or evidence not in {"observed", "told", "inferred"}:
            self.event("quarantine", {"source": source or "unknown", "text": text[:500],
                                      "reason": "unattested or invalid source"})
            return False
        if source != "world" and evidence == "observed":
            self.event("quarantine", {"source": source, "text": text[:500],
                                      "reason": "untrusted observed claim"})
            return False
        tick = sum(e["kind"] == "sensed" for e in self.archive.events()) + 1
        category = Evidence.OBSERVED if evidence == "observed" else (
            Evidence.REPORTED if evidence == "told" else Evidence.INFERRED)
        percept = Percept(event_id=f"ingress-{tick}", channel="scene",
                          evidence=category, source_ref=source, tick=tick,
                          attribute="message", value=text[:1000], confidence=1.0)
        scene = self.sensus.step(tick, (percept,))
        self.event("sensed", {"tick": tick, "percepts": [{
            "event_id": percept.event_id, "channel": percept.channel,
            "evidence": percept.evidence.value, "source_ref": percept.source_ref,
            "attribute": percept.attribute, "value": percept.value,
            "confidence": percept.confidence}]})
        self.event("perception", {"text": text[:1000], "source": source,
                                  "class": evidence, "conflicts": len(scene.conflicts)})
        if "ipseity" not in self.disabled:
            signal = SourceSignal(subject_id=self.subject_id,
                                  kind=Kind.WORLD_OBJECT if evidence == "observed" else Kind.HEARD_TEXT,
                                  value=text[:1000] or "(silence)", source_ref=source,
                                  acquired=True, salience=.85)
            self.last_frame = render_frame(self.ipseity.process(
                self.subject_id, [signal]).frame)
        else:
            self.last_frame = text[:1000]
        if "noesis" not in self.disabled:
            self._noesis_input(text[:1000], source, evidence)
        # DUCK is a real planning donor but its state is an event-backed projection.
        self.duck.step(WorldEvent(kind="world", source=source, text=text[:1000],
                                   tags=("obstacle",) if "blocked" in text.lower() else (),
                                   perceived=evidence == "observed"), allow_inner_speech=False)
        self.event("duck_projection", {"state": self.duck.state.to_dict()})
        return True

    def _noesis_input(self, text, source, evidence):
        if evidence == "observed":
            cls = EvidenceClass.LIVED_OBSERVED
        elif evidence == "told":
            cls = EvidenceClass.THIRD_PARTY_CLAIM
        else:
            cls = EvidenceClass.UNVERIFIED_TEXT
        p = {"text": text, "source": source, "class": cls.value}
        self.event("noetic_input", p)
        seq = self.archive.events()[-1]["seq"]
        decision = self.noetic.step(Observation(
            origin_id=str(seq), subject_id=self.subject_id,
            text=text, source=source, evidence_class=cls))
        self.event("noetic_decision", {"action": decision["action"],
                                       "scores": decision["scores"],
                                       "source_event": seq})

    def recall(self, query, limit=4, *, include_dreams=False):
        if "mnemosyne" in self.disabled:
            return []
        terms = set(re.findall(r"\w+", query.lower()))
        scored = []
        for e in self.archive.events():
            if e["kind"] not in ({"perception", "action", "speech"} |
                                  ({"dream"} if include_dreams else set())):
                continue
            p = e["payload"]
            txt = p.get("text") or p.get("description") or ""
            source = "dreamed" if e["kind"] == "dream" else p.get("class", "lived")
            words = set(re.findall(r"\w+", txt.lower()))
            overlap = len(terms & words) / max(1, len(terms | words))
            priority = .10 if e["kind"] == "action" else .04
            score = .65 * overlap + .25 * (e["seq"] / max(1, self.archive.events()[-1]["seq"])) + priority
            if overlap or "failure" in txt.lower() or e["kind"] == "action":
                scored.append((score, e["seq"], {"event_id": e["seq"],
                                                "text": txt, "provenance": source}))
        return [r for _, _, r in sorted(scored, key=lambda x: (-x[0], -x[1]))[:limit]]

    def subjective_packet(self, latest=""):
        s = self.state()
        signals = [
            SourceSignal(self.subject_id, Kind.HUNGER, s["body"]["hunger"],
                         source_ref="body", acquired=True, salience=.7),
            SourceSignal(self.subject_id, Kind.FEAR, self.affect()["fear"],
                         source_ref="affect", acquired=True, salience=.7),
        ]
        for m in self.recall(latest or "water failure", limit=3):
            signals.append(SourceSignal(self.subject_id, Kind.RECOLLECTION,
                str(m["text"])[:950], source_ref=str(m["event_id"]), acquired=True,
                salience=.75, memory_class=MemoryClass.LIVED))
        if latest:
            signals.append(SourceSignal(self.subject_id, Kind.WORLD_OBJECT,
                latest[:900], source_ref="perception", acquired=True, salience=.9))
        return render_frame(self.ipseity.process(self.subject_id, signals).frame)

    def affect(self):
        s = self.state()
        failures = sum(e["kind"] == "action" and not e["payload"].get("success")
                       for e in self.archive.events()[-12:])
        fear = min(1., .12 + .20 * failures + .32 * s["body"]["cold"])
        curiosity = max(.05, .7 - .10 * failures - .4 * s["body"]["fatigue"])
        return {"fear": round(fear, 3), "curiosity": round(curiosity, 3),
                "fatigue": s["body"]["fatigue"]}

    def day(self):
        s = self.state()
        body = dict(s["body"])
        body["thirst"] = min(1., body["thirst"] + .17)
        body["hunger"] = min(1., body["hunger"] + .11)
        body["fatigue"] = min(1., body["fatigue"] + .09)
        if s["door"] == "open":
            body["cold"] = min(1., body["cold"] + .18)
        day = s["day"] + 1
        self.event("day", {"changes": {"day": day, "body": body}})
        if day in (2, 5):
            self.event("visitor", {"day": day, "text": "A traveler asks whether the pump is safe."})
            self.intake("A traveler asks whether the pump is safe.", source="visitor",
                        attested=True, evidence="told")
            self._goal("explain_to_visitor", "dormant", "Owe the traveler an answer",
                       "visitor visit recorded")
        self.intake("The new day begins. The water supply is finite.", source="world",
                    attested=True, evidence="observed")
        self._spontaneous_goal()
        return self.state()

    def _goal(self, goal_id, status, text, reason):
        self.event("goal", {"goal_id": goal_id, "status": status,
                            "text": text, "reason": reason, "day": self.state()["day"]})

    def _spontaneous_goal(self):
        s = self.state()
        prev = s["goals"].get("secure_water", {})
        if s["stocks"]["water"] <= 1 and prev.get("status") != "active" and "telos" not in self.disabled:
            self._goal("secure_water", "active", "Keep water available",
                       "Body need and depleted world stock")
            self.duck.form_goal("overcome", "Find a sustainable water source")
            self.event("duck_projection", {"state": self.duck.state.to_dict()})

    def world_disruption(self, *, pump="broken", spare_part=False):
        """Authoritative external intervention, never generated by the renderer."""
        self.event("change", {"changes": {"pump": pump, "spare_part": bool(spare_part)}})
        self.intake("The pump is broken and the replacement part is missing.",
                    source="world", attested=True, evidence="observed")

    def _select(self):
        s = self.state()
        body, stocks = s["body"], s["stocks"]
        if body["thirst"] > .79 and stocks["water"] > 0:
            return "drink", "urgent bodily thirst"
        if s["goals"].get("secure_water", {}).get("status") == "active":
            if s["pump"] == "working":
                return ("collect_water" if s["place"] == "spring" else "move_spring",
                        "known spring route")
            memories = self.recall("repair pump failure missing part", limit=8)
            failed = any("repair_pump" in m["text"] and "failure" in m["text"]
                         for m in memories)
            if "mnemosyne" in self.disabled:
                failed = False
            # The rain source was not a predefined branch of DUCK's repair routes.
            if failed:
                return ("collect_rain" if s["place"] == "garden" else "move_garden",
                        "new route inferred from actual failed repair memory")
            return ("repair_pump" if s["place"] == "workshop" else "move_workshop",
                    "attempt known repair")
        if body["cold"] > .65 and stocks["fuel"] > 0:
            return ("warm" if s["place"] == "cabin" else "move_cabin", "cold appraisal")
        if body["hunger"] > .70 and stocks["food"] > 0:
            return "eat", "hunger"
        if stocks["food"] < 2:
            return ("forage" if s["place"] == "garden" else "move_garden", "resupply food")
        if stocks["fuel"] < 2:
            return ("gather_wood" if s["place"] == "garden" else "move_garden", "resupply fuel")
        if body["fatigue"] > .7:
            return "rest", "fatigue"
        return "inspect", "open initiative"

    def decide(self, *, force=None):
        started = time.perf_counter()
        state_before = self.state()
        if force and force not in self.actions():
            raise ValueError("Unknown physical action")
        action, rationale = self._select() if force is None else (force, "witness forced action")
        prior = self.recall("repair pump failure missing part", limit=6)
        affect = self.affect()
        noetic_events = [e for e in self.archive.events() if e["kind"] == "noetic_decision"]
        noetic_choice = noetic_events[-1]["payload"]["action"] if noetic_events else "defer"
        # Noetic decisions influence initiative rather than rewrite the action.
        if not force and noetic_choice == "protect" and affect["fear"] > .72 and action == "inspect":
            action, rationale = "move_cabin", "Noetic protective override"
        description, success, changes = self._act(action, state_before)
        self.event("action", {"action": action, "description": description,
                              "text": action + (" success: " if success else " failure: ") + description,
                              "success": success, "changes": changes,
                              "reason": rationale, "recalled": [m["event_id"] for m in prior],
                              "affect": affect, "noetic": noetic_choice})
        self.intake(description, source="world", attested=True, evidence="observed")
        s = self.state()
        if s["goals"].get("secure_water", {}).get("status") == "active" and s["stocks"]["water"] >= 3:
            self._goal("secure_water", "kept", "Keep water available",
                       "World receipt verifies three units available")
        self._spontaneous_goal()
        output = {"day": s["day"], "action": action, "success": success,
                  "description": description, "reason": rationale,
                  "memory_ids": [m["event_id"] for m in prior], "affect": affect,
                  "noetic_action": noetic_choice, "packet": self.subjective_packet(description),
                  "latency_ms": round((time.perf_counter() - started) * 1000, 2)}
        self.last_causal = output
        return output

    @staticmethod
    def actions():
        return ("move_cabin", "move_spring", "move_garden", "move_workshop",
                "collect_water", "repair_pump", "collect_rain", "drink",
                "eat", "warm", "rest", "forage", "gather_wood",
                "close_door", "open_door", "inspect")

    def _act(self, action, s):
        stocks, body = dict(s["stocks"]), dict(s["body"])
        changes = {}
        description, success = "", True
        if action.startswith("move_"):
            place = action.removeprefix("move_")
            changes["place"] = place
            description = "I moved to the " + place + "."
        elif action == "collect_water":
            if s["place"] != "spring" or s["pump"] != "working":
                success, description = False, "The spring pump cannot provide water."
            else:
                stocks["water"] += 2
                description = "I brought two measures of water from the spring."
        elif action == "repair_pump":
            if s["place"] != "workshop" or not s["spare_part"]:
                success, description = False, "The repair failed: the spare part is missing."
            else:
                changes["spare_part"] = False
                changes["pump"] = "working"
                description = "I repaired the pump using the spare part."
        elif action == "collect_rain":
            if s["place"] != "garden" or s["rain"] <= 0:
                success, description = False, "The rain barrel is empty or out of reach."
            else:
                amount = min(2, s["rain"])
                stocks["water"] += amount
                changes["rain"] = s["rain"] - amount
                description = f"I collected {amount} measures from the rain barrel."
        elif action == "drink":
            if stocks["water"] < 1:
                success, description = False, "There is no water to drink."
            else:
                stocks["water"] -= 1
                body["thirst"] = max(.02, body["thirst"] - .58)
                description = "I drank one measure of water."
        elif action == "eat":
            if stocks["food"] < 1:
                success, description = False, "No food remains."
            else:
                stocks["food"] -= 1
                body["hunger"] = max(.02, body["hunger"] - .53)
                description = "I ate a stored ration."
        elif action == "forage":
            if s["place"] != "garden":
                success, description = False, "There is no food to forage here."
            else:
                stocks["food"] += 2
                description = "I foraged two rations in the garden."
        elif action == "gather_wood":
            if s["place"] != "garden":
                success, description = False, "There is no fuel to gather here."
            else:
                stocks["fuel"] += 2
                description = "I gathered two bundles of fuel."
        elif action == "warm":
            if s["place"] != "cabin" or stocks["fuel"] < 1:
                success, description = False, "I cannot light a fire here."
            else:
                stocks["fuel"] -= 1
                body["cold"] = max(0., body["cold"] - .5)
                description = "I burned one bundle of fuel for warmth."
        elif action == "rest":
            body["fatigue"] = max(0., body["fatigue"] - .45)
            description = "I rested and recovered some energy."
        elif action in ("open_door", "close_door"):
            changes["door"] = "open" if action == "open_door" else "closed"
            description = "I left the door " + changes["door"] + "."
        else:
            description = "I inspected the " + s["place"] + " without changing it."
        changes["stocks"] = stocks
        changes["body"] = body
        return description, success, changes

    def dream(self, seed=None):
        s = self.state()
        basis = self.recall("water travel repair", limit=4)
        fragments = [m["text"] for m in basis] or ["a room with no doors"]
        rng = random.Random(seed if seed is not None else s["day"])
        content = "A quiet room contains " + rng.choice(fragments)[:120] + " beside a silent clock."
        self.event("dream", {"text": content, "class": "dreamed", "day": s["day"],
                              "cause_event_ids": [m["event_id"] for m in basis]})
        return content

    def voice_genome(self):
        speech = [e["payload"]["text"] for e in self.archive.events() if e["kind"] == "speech"]
        words = Counter(w.lower() for t in speech for w in re.findall(r"[a-zA-Z']+", t))
        return {"samples": len(speech), "avg_words": round(sum(len(t.split()) for t in speech) /
               max(1, len(speech)), 2), "frequent": words.most_common(10)}

    def compose(self, result, *, substrate="rule"):
        """Renderer receives only the bounded subjective packet and action outcome."""
        body = result["description"]
        text = "I " + body[2:] if body.startswith("I ") else "I noticed: " + body
        if substrate == "alternate":
            text = text.replace("I noticed:", "I observed:")
        baseline = self.voice_genome()
        dist = 0.0 if baseline["samples"] == 0 else min(1., abs(
            len(text.split()) - baseline["avg_words"]) / max(1, baseline["avg_words"]))
        return text, dist

    def speak(self, result, sink, *, substrate="rule"):
        text, distance = self.compose(result, substrate=substrate)
        key = "utterance-" + str(self.archive.events()[-1]["seq"] + 1)
        self.speech.prepare(key, text, before_tick=self.state()["day"], before_neural_tick=0)
        # Native journal requires a real sink ACK before any canonical speech claim.
        receipt = self.speech.emit_once(key, sink)
        self.event("speech", {"key": key, "text": receipt.content,
                              "sink": receipt.sink_id, "checksum": receipt.content_sha256,
                              "ack": True, "substrate": substrate, "drift": distance,
                              "semantics": {"action": result["action"],
                                            "success": result["success"]}})
        return receipt

    def recount(self):
        return [{"day": e["payload"].get("day", "?"), "kind": e["kind"],
                 "event_id": e["seq"], "text": e["payload"].get(
                     "description", e["payload"].get("text", "")),
                 "provenance": ("dreamed" if e["kind"] == "dream" else
                                e["payload"].get("class", "lived"))}
                for e in self.archive.events() if e["kind"] in {
                    "action", "perception", "visitor", "dream", "speech"}]

    def budget(self):
        return {"events": len(self.archive.events()), "sqlite_bytes": sum(
            p.stat().st_size for p in self.root.glob("*.sqlite3*")),
            "note": "Latency measured per decision. RAM and replay time measured by benchmark."}

    def close(self):
        self.noetic.close()
        self.speech.close()
        self.archive.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()
