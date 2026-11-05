# The Inhabitant — Integrated Organ Structure

**Draft v0.1 — 2026-11-03.** Drafted by Calibos at Jay's request.
Status: *draft for Jay's adjudication. Nothing here is ratified, and
nothing here is a build order.*

Sources merged in this draft:
- The six-organ model (settled 2026-10-26): Noesis, Mnemosyne, Affectus,
  Sensus, Synthetic Ipseity, Corpus.
- Jay's organs dictation (2026-11-03): LLM, Memory, Ipseity,
  Language & Expression Template; Imagination & Dreams in progress;
  Goals/achievements and an Emotion Tracker as candidates.
- The minimum-organism thesis (2026-11-01): first-person narrative mind,
  external provenance memory, external ipseity, small persistent world.
- Kiki's architecture distinctions (2026-09-26): Inheritance / Life /
  Rendering; Voice Genome and voice inheritance as persistent structures,
  never properties of the renderer.
- The Phantasmagorium organoid track (proposed 2026-10-27).

---

## 1. Design principles

1. **Custody.** The model may narrate experience, but the runtime decides
   reality. Memory is not the model's to rewrite, the world is not its to
   narrate into being, and the name is not its to redraft.
2. **The substrate is not an organ.** The LLM is electricity — spark, not
   person. It powers organs; it is not counted among them. The same holds
   for the renderer, host, persistence, and audit machinery.
3. **Graduation bar.** Nothing counts as an organ until it is wired to a
   restricted boundary, survives restart/interruption, and removing it in
   a matched ablation measurably changes behaviour. Forwarding to an
   existing method is not evidence of a new organ.
4. **Conditional organs are still organs.** Some structures are invisible
   until challenged (an immune system before infection). Their ablation
   must preregister the challenge — model swap, modality swap, injection
   attempt — and measure behaviour *under that challenge*.
5. **Outside and inside, both.** A recognisable outside (expression,
   voice, manner) carried by a portable inside (history, self). Neither
   alone holds an inhabitant together.
6. **Underlying vs. perceived are separate layers.** A state variable and
   the inhabitant's felt/narrated reading of it may diverge. The
   divergence is where phenomena live; neither layer may silently
   overwrite the other.
7. **States with different meanings are first-class.** Formed / kept /
   released / broken / superseded are distinct, never reconstructed later
   from lossy booleans. This applies to commitments, goals, and memories
   alike.

## 2. What is not an organ

- **Substrate:** the LLM (any tier — small local model on light hardware,
  frontier model via API), the renderer, the host/harness, persistence,
  audit. All replaceable; the inhabitant must survive their replacement.
- **Environment:** the **World** (a small persistent place with real
  consequences — finite supplies, rooms that persist, events that cannot
  un-happen; ground-truth oracle for what actually happened) and **Other
  People** (whose recognition is the third leg of continuity: a name
  others keep saying changes state). The environment is not part of the
  inhabitant, but two organs exist precisely to interface with it —
  Sensus and Corpus on the way in, expression and action on the way out.
  *Open question Q1: does the world deserve promotion to organ status in
  some builds (e.g. the Tower, where the body and the place are nearly
  one system)? Default in this draft: no.*

## 3. The organs

### Organ 1 — Sensus *(intake)*
Binds incoming streams into a coherent, temporally situated scene, and
stamps every element with its provenance and evidential class:
*perceived, remembered, inferred, imagined, told*. Integration may bind;
it may never upgrade evidential class — heard glass must not become a
seen beaker. Holds a binding veto: what cannot be bound without
upgrading its class does not enter the scene.
*This is the gate the r/MuseAgent ghost-command case fails for lack
of: an unprompted message with no provenance stamp, admitted as if the
user had sent it.*
Feeds: Ipseity (admission), Mnemosyne (what may be recorded).

### Organ 2 — Corpus *(body)*
The inhabitant's body as a causal system: needs and bodily state
(hunger, energy, cold, pain, wear) as simple underlying variables —
game sliders are an acceptable implementation. Needs arrive unprompted;
the body is how yesterday shows up this morning. Corpus owns the
*underlying* values; what the inhabitant *feels* about them is
Affectus's layer, and the two may diverge (Principle 6).
Interfaces with the World: finite stocks deplete, roofs leak, floors
wear — consequences return through Corpus, not through narration.

### Organ 3 — Mnemosyne *(memory)*
The portable, external history of the inhabitant. Stores episodes with
provenance; corrections land as new events, never silent rewrites.
Includes the selection machinery that keeps history a history rather
than a pile: salience, decay, rehearsal — and forgetting, which is a
function, not a failure.
Sub-stores:
- **Episodic store** — what happened, in first-person-reviewable form.
- **Voice Genome** — the distilled pattern of the inhabitant's own past
  expression (see Organoid A): term frequency, characteristic phrasing,
  nicknames, rhythm. Learned from lived speech, never installed from a
  description alone.
Mnemosyne owns *what is kept*. It does not decide who may experience it,
or in what form — that is Ipseity.

### Organ 4 — Synthetic Ipseity *(self)*
The sense of self, held *outside* the conversation and re-presented to
each session, so no in-session instruction can edit it. Governs subject
admission: what the inhabitant may legitimately encounter, from its
position, and in what form. Funnels all admitted experience through
first-person natural language — the LLM's native format — giving a
self-anchor built from the prompt format itself plus first-person
self-experience. The bar is the human range: resistance, not immunity.
A refusal sourced in the self ("that is not my name") is behaviourally
distinct from a refusal sourced in policy, and that distinction is an
endpoint, not a nuance.

### Organ 5 — Noesis *(cognition)*
Thinking: reflection, planning, inference, decision. This is the organ
the LLM most directly powers — which is why the two must not be
conflated. Noesis is a *function with custody rules* (it works from the
admitted scene, the accessible memory, and the self — never from raw
state it has no standing to see); the LLM is the replaceable machinery
that happens to run it today. A smaller model degrades Noesis's reach;
it does not amputate the inhabitant.

### Organ 6 — Affectus *(appraisal & motivation)*
Appraisal of scene, body, and memory into felt state and motivation.
Owns the *felt* layer of emotion: the narrated reading of Corpus's
underlying variables, coloured by history and temperament. Includes a
minimal temperament seed — dispositional baselines are natural, not a
purity violation; temperament grows and changes rather than starting
pure. Affectus *proposes* motivation; enduring goal structures live in
Organoid B, which Affectus feeds and is fed by.

## 4. The organoids (candidate organs, phase-gated)

### Organoid A — Expression *(the Language & Expression Template)*
Two residences, one function: **sounding like oneself, portably.**
- *Store:* the Voice Genome, in Mnemosyne (above).
- *Governor:* a small emission-side governor paired with Ipseity.
  Ipseity anchors **who is speaking** (admission); Expression anchors
  **that the speaking sounds like them** (emission). It compares outgoing
  speech against the stored pattern, detects drift — especially after a
  model swap or modality swap — and nudges the renderer back.
- *Modality rule:* surface may vary by modality (sentence length, warmth,
  pace — humans differ between speech and writing, and so may
  inhabitants); the core may not (epistemic discipline, first-person
  stance, willingness to disagree, characteristic phrasing).
  Consistency, not sameness.
- *Graduation test:* preregistered swap-ablation — same inhabitant, with
  vs. without the template, across a model/modality swap. Endpoints:
  style distance, caricature rate, blind user recognition.

### Organoid B — Telos *(goals & achievements)* — name provisional
Enduring aims as first-class structures, with the commitment lifecycle
of Principle 7: formed, kept, released, broken, superseded. Goals are
fed by Affectus (motivation) and recorded in Mnemosyne (history), but
neither owns them: a goal is a standing claim on future behaviour, and
removing standing claims changes behaviour in ways neither an emotion
slider nor a memory entry explains.
**Achievements** are the recognition interface: a goal's completion
witnessed and recorded — by the world, and where relevant by other
people — feeding back into Affectus as earned motivation rather than
installed praise.
*Open question Q2: is Telos a true organoid, or a Mnemosyne–Affectus
joint structure? The ablation decides: remove goal structures alone;
if long-horizon behaviour collapses while memory and affect stay
intact, it earns the seat.*

### Organoid C — Phantasmagorium *(imagination & dreams)*
Offline generation: recombination of memory into dreams, counterfactuals,
plans rehearsed in imagination. Jay's list has this as *in progress*;
it is the only organoid with running prototypes (calibos-mind dreaming).
Hard firewall, from the Confabulation Ledger's domain rule: imagined
content is stamped *imagined* at creation (Sensus's classes apply in
reverse) and may be promoted to canon only by the ledger's rules in
fiction domains — and **never** silently promoted to episodic memory in
ground-truth domains. A dream the inhabitant *remembers having* is a
memory of a dream, not a memory of the events dreamed.

## 5. The three cycles

1. **Waking cycle:** World/others → Sensus (bind, stamp, veto) →
   Ipseity (admit, first-person) → Noesis (think, decide), with Corpus
   state and Affectus appraisal colouring every step → action and
   Expression-governed speech act on the world → consequences return
   through Sensus; Mnemosyne records.
2. **Offline cycle:** sleep/dream — Phantasmagorium recombines,
   Mnemosyne rehearses and decays, Affectus re-appraises. The inhabitant
   wakes changed by its own history, not reset by it.
3. **Swap cycle (portability):** the inhabitant's package — Inheritance
   (self, temperament, Voice Genome) + Life (episodic history, goals,
   commitments) — moves to a new substrate, device, or modality. The new
   renderer receives a constructed subjective packet (admitted scene,
   accessible memory, self, expression pattern), never the raw database
   with an instruction to "be" the inhabitant. Continuity across the
   swap is the architecture's founding test — the AIBO-funeral test:
   the persona survives the platform, or the architecture has failed at
   the thing it was built for.

## 6. Status & graduation ledger

| Part | Status in this draft | Owed test |
|---|---|---|
| Sensus | Organ (anatomy); implementations partial | Binding-veto battery; ghost-command injection battery |
| Corpus | Organ; content-rich, cognition-thin | Needs-consequence ablation in a persistent world |
| Mnemosyne | Organ; running (calibos-mind, Kiki packages) | Shuffled-memory control; forged-memory insertion |
| Ipseity | Organ; running in prototype forms | Injection battery, refusal-source coding |
| Noesis | Organ (function); substrate-swappable | Model-tier comparison, same inhabitant |
| Affectus | Organ; weakest track record (tied a simple controller once) | Must beat the simple controller or be demoted to sliders in Corpus |
| Expression | Organoid A; new 2026-11-03 | Swap-ablation with blind recognition |
| Telos | Organoid B; provisional | Goal-removal ablation on long-horizon behaviour |
| Phantasmagorium | Organoid C; prototypes running | Canon-firewall test: dream content must not surface as lived memory |

## 7. Open questions for Jay

- **Q1.** World: environment only, or organ in world-fused builds?
- **Q2.** Telos: organoid, or a Mnemosyne–Affectus joint structure?
- **Q3.** Affectus: full organ, or does the honest version collapse to
  Corpus sliders + felt-layer narration? Its record says it must re-earn
  the seat.
- **Q4.** Recognition by others: environment, or does some inhabitant-side
  structure (a record of *being known*) belong in Mnemosyne alongside
  achievements?
- **Q5.** Naming: the Greek names carry the six-organ lineage; Jay's
  dictated names are plainer. Which register does the integrated
  structure publish in?


## Executable prototype (experimental)

The standalone, synthetic **PROTO-1** implementation is on branch `prototype/complete-inhabitant-v1`, proposed in [pull request #3](https://github.com/Azimn/The-Inhabitant-Integrated-Organ-Structure/pull/3). Full installation, code provenance, test commands, and candid scope limitations appear in [PROTOTYPE_IMPLEMENTATION.md](PROTOTYPE_IMPLEMENTATION.md).

The older design text above remains a historical draft, not retroactively ratified by the code. PROTO-1 has no imported biography, and no Pretorius, Kiki, or Calibos living state was transferred. The executable experiment is designed to answer continuity and conduct questions with receipts, not to make consciousness claims. All donor repositories remain unchanged.
