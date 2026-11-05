# PROTO-1: integrated Inhabitant laboratory

Working implementation, November 4, 2026. This is a new fictional subject with no inherited biography. Source repositories were not modified. The runtime uses a canonical append-only SQLite life ledger, not model narration, to decide what happened.

## Quick start

Requires Python 3.11 or newer. The default runtime needs no third-party packages. Run the following from the checkout:

    git checkout prototype/complete-inhabitant-v1
    python -m unittest discover -s tests -v
    python -m inhabitant.cli simulate --root .local-proto --days 7
    python -m inhabitant.cli verify --root .local-proto
    python -m inhabitant.cli recount --root .local-proto

For incremental life in a separate directory:

    python -m inhabitant.cli day --root .local-living
    python -m inhabitant.cli act --root .local-living
    python -m inhabitant.cli status --root .local-living

The simulator executes seven synthetic days, not seven real elapsed days. Reusing a state directory continues the existing life. For matched trials use a fresh directory.

## Real local models and replaceable substrates

With a running local Ollama service and an installed model:

    python -m inhabitant.cli speak --root .local-living --backend ollama --model qwen3:14b
    python -m inhabitant.cli act --root .local-living --backend ollama --model qwen3:14b

The model receives only an Ipseity-projected first-person packet. It cannot directly rewrite the world, self, past, or commitments. For speech, the output must pass the Expression governor and be acknowledged by the sink. For actions, Noesis accepts a constrained model proposal only on suitable non-urgent turns. Unsupported proposals are rejected. The native model path requires local Ollama and is not exercised by GitHub-hosted CI.

For a compatible cloud chat-completions speech endpoint, set environment variable INHABITANT_API_KEY and pass the complete API endpoint via --backend compatible --url, with --model. No credentials are included in the repository.

## The world and the experiment

The world has a cabin, spring, garden, and workshop with real locations and a finite food, water, fuel, and rain inventory. A physical body experiences thirst, hunger, fatigue, and cold. There is a door and a scripted visitor. On day one a genuine external intervention breaks a pump and removes its spare part. The inhabitant initially does not know why the pump is broken. Failed repair creates an event-backed autobiographical memory. A bounded planner searches known action affordances, explores when it cannot find a route, perceives the rain barrel when physically at the garden, and derives an alternative sequence. This is symbolic world-model search, not an arbitrary general-purpose planner.

## Six organs and three organoids

Sensus invokes the actual Sensus-Communis-Artificialis binding code, behind a new provenance gate. It refuses unattested messages and evidence upgrades. Corpus controls legal physical consequences and stock/need changes, written for this new world. Mnemosyne retrieves ledger episodes with provenance, lexical relevance, recency, and salience. DUCK v0.9 also runs natively as an event-backed advisory memory/goal projection. Synthetic Ipseity invokes the original first-person source-access kernel. Noesis invokes the original transactional Noetic Engine and a new world-model planning layer, plus a constrained optional model action port. Affectus computes a felt-layer appraisal and changes approach selection after failures.

Telos owns canonical event-sourced active goals and dormant obligations. The DUCK donor can propose and exercise plans but cannot declare a canonical promise or world goal completed independently. Phantasmagorium recombines archived fragments, tags its resulting dream as dreamed rather than lived, and invokes Calibos's native dream-isolation assertion to forbid world mutation. Expression measures speech-derived voice characteristics, checks identity and first-person emission, and invokes Pretorius's two-phase speech-delivery journal. Autobiographical speech is recorded only when the sink confirms exact delivery.

## What source code actually came from the other projects

The vendor folder pins selected source files from DUCK, The-Noetic-Engine, Sensus-Communis-Artificialis, synthetic-ipseity, The-Doctor-Lives, calibos-mind, and Pretorius-Connectome. DONORS.lock.json gives original file paths, blob hashes, and source tree hashes. Direct donor imports are used for DUCK, Noetic, Sensus, Ipseity, acknowledged speech, and Calibos dream-isolation. Connectome associative search and Calibos mood residues are preserved but remain research candidates, not claimed functional ports. PersonaConsole AETHER multi-band memory and Gelatinblob admission-gated learning are not yet integrated because their comparative effects are not established; simply copying them into another authoritative state store would not be valid integration.

## Evidence and limits

CI runs compilation, unit tests, and a seven-day simulation. Tests cover restart persistence, hash-chain mutation detection, spontaneous water goals, unexpected environmental change, missing-part discovery, behavioral memory and affect ablations, admission/quarantine, dreams, bounded model proposals, identity spoofing, model-surface changes, and two-phase speech ACK.

The ledger is the sole canonical world, identity, and promise history. Donor internal state is reconstructed or advisory. Its hash chain provides tamper evidence against accidental changes, not security against a fully privileged malicious host.

Not yet demonstrated: a real frontier-to-local model swap, microphone or speech modality, human blind-recognition ratings, seven wall-clock days, all donor families' causally necessary behavior, external AETHER semantic superiority, Gelatinblob learning advantage, or Connectome graph-induced conduct changes. Those are honest non-graduated capabilities.

Run a fresh benchmark with:

    python -m inhabitant.cli simulate --root .benchmark-fresh --days 7

The report includes tests' causal outcomes, decision latency, process RSS, Python allocation, ledger bytes, and recount receipts. All measurements are machine-specific, and the subject's data is not automatically published.
