"""Command line laboratory for the integrated inhabitant."""
import argparse
import json
from pathlib import Path
try:
    import resource
except ImportError:
    resource = None  # Windows has no Unix resource module.
import time
import tracemalloc

from .engine import Inhabitant
from .renderers import OllamaRenderer, OpenAICompatibleRenderer, OllamaReasoner
from vendor.doctor_lives.speech_emission import SpeechSinkAck, digest


def console_sink(text, key):
    print("PROTO-1:", text, flush=True)
    return SpeechSinkAck(delivery_key=key, sink_id="stdout", content_sha256=digest(text))


def simulate(root, days=7, *, speak=False, disabled=()):
    t0 = time.perf_counter()
    tracemalloc.start()
    decisions = []
    with Inhabitant(root, disabled=disabled) as creature:
        for index in range(days):
            creature.day()
            if creature.state()["day"] == 1:
                # The obstacle was NOT included in Telos's initial plan.
                creature.world_disruption(pump="broken", spare_part=False)
            for _ in range(5):
                response = creature.decide()
                decisions.append(response)
                if speak and response["action"] in ("repair_pump", "collect_rain"):
                    creature.speak(response, console_sink)
            creature.dream()
        creature.archive.verify()
        world = creature.state()
        report = {
            "subject": world["name"], "days": world["day"],
            "place": world["place"], "stocks": world["stocks"],
            "body": world["body"], "goals": world["goals"],
            "decisions": len(decisions), "failed_actions": [
                x["action"] for x in decisions if not x["success"]],
            "actions": [x["action"] for x in decisions],
            "dreams": sum(x["kind"] == "dream" for x in creature.archive.events()),
            "quarantines": sum(x["kind"] == "quarantine" for x in creature.archive.events()),
            "memory_changed_route": any("new route inferred" in x["reason"] for x in decisions),
            "donor_noetic_used": all("noetic_action" in x for x in decisions),
            "donor_duck_goals": len(creature.duck.plans()),
            "ledger_verified": True,
            "budget": creature.budget(),
            "elapsed_ms": round((time.perf_counter() - t0) * 1000, 2),
            "peak_python_bytes": tracemalloc.get_traced_memory()[1],
            "peak_rss_kib": (resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
                             if resource is not None else None),
            "worst_decision_ms": max(x["latency_ms"] for x in decisions),
            "recount_receipts": len(creature.recount()),
        }
    tracemalloc.stop()
    return report


def main():
    parser = argparse.ArgumentParser(description="Integrated Inhabitant laboratory")
    parser.add_argument("command", choices=["simulate", "day", "act", "status", "recount", "verify", "dream", "speak"])
    parser.add_argument("--root", default=".inhabitant-state")
    parser.add_argument("--days", type=int, default=7)
    parser.add_argument("--action", default="")
    parser.add_argument("--backend", choices=["rule", "ollama", "compatible"], default="rule")
    parser.add_argument("--model", default="")
    parser.add_argument("--url", default="")
    parser.add_argument("--disable", action="append", default=[])
    args = parser.parse_args()
    if args.command == "simulate":
        result = simulate(args.root, args.days, disabled=args.disable, speak=False)
    else:
        with Inhabitant(args.root, disabled=args.disable) as c:
            if args.command == "day":
                result = c.day()
            elif args.command == "act":
                reasoner = (OllamaReasoner(args.model or "qwen3:14b",
                           args.url or "http://127.0.0.1:11434")
                           if args.backend == "ollama" and not args.action else None)
                result = c.decide(force=args.action or None, reasoner=reasoner)
            elif args.command == "status":
                result = {"world": c.state(), "affect": c.affect(),
                          "voice_genome": c.voice_genome(), "budget": c.budget()}
            elif args.command == "recount":
                result = c.recount()
            elif args.command == "verify":
                result = {"ledger_verified": c.archive.verify()}
            elif args.command == "dream":
                result = {"dream": c.dream()}
            elif args.command == "speak":
                outcome = c.decide()
                if args.backend == "ollama":
                    renderer = OllamaRenderer(args.model or "qwen3:14b",
                                              args.url or "http://127.0.0.1:11434")
                elif args.backend == "compatible":
                    renderer = OpenAICompatibleRenderer(args.model, args.url)
                else:
                    renderer = None
                receipt = c.speak(outcome, console_sink, renderer=renderer)
                result = {"emission": receipt.delivery_key, "acknowledged": True}
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
