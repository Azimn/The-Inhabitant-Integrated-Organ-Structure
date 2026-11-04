# Adjudication register

**Applies to:** [Integrated Organ Structure, draft v0.1](integrated-organ-structure-v0.1.md)  
**As of:** 2026-11-03  
**Decision authority:** Jay  
**Standing:** All five questions open. The provisional defaults in the source document are not ratifications.

This register is a place to record explicit architecture decisions, their evidence and consequences. It is **not a build queue**.

## Open decisions

| ID | Question | Alternatives under consideration | Current status |
|---|---|---|---|
| Q1 | Is the World always external, or can it be an organ in world-fused builds? | Environment only (draft default); conditional organ in fused builds | **Open** |
| Q2 | Does Telos earn organoid status independently of memory and affect? | Distinct organoid; Mnemosyne-Affectus joint structure | **Open, evidence-dependent** |
| Q3 | Does Affectus remain a full organ? | Full appraisal organ; Corpus variables plus felt-state narration | **Open, evidence-dependent** |
| Q4 | Where does recognition by others belong? | External social environment only; inhabitant-side record of being known (e.g. in Mnemosyne) | **Open** |
| Q5 | Which naming register is published? | Greek lineage (e.g. Mnemosyne, Noesis); plain-language organ labels; documented dual naming | **Open** |

## Criteria to consider before adjudication

**Q1, World custody.** Define a meaningful boundary between world state and body state. If a fused build claims the World as an organ, explain how ground-truth authority and portability survive that choice.

**Q2, Telos independence.** Preserve memory and appraisal while removing standing goals. Examine whether long-horizon commitment behavior changes in matched trials. Record formed, kept, released, broken, and superseded as distinct outcomes.

**Q3, Affectus independence.** Compare the full appraisal organ against a simple controller using preregistered endpoints. Report ties and failures as clearly as improvements. The current draft notes an earlier tie and makes no success claim.

**Q4, social recognition.** Separate another person's actual recognition from the inhabitant's belief or memory of being recognized. If adding an inhabitant-side structure, define its evidential class and correction behavior.

**Q5, nomenclature.** Choose the public-facing naming system and document a stable mapping between published names and internal terms. Avoid renaming as a proxy for architectural change.

## Decision record template

Copy this block only when Jay actually adjudicates an open question:

```markdown
### Decision QX: [brief title]
- Date (UTC, ISO 8601):
- Decided by: Jay
- Status: Ratified / Deferred / Rejected
- Selected option:
- Rationale and evidence:
- Alternatives considered:
- Consequences:
- Source discussion or evidence link:
- Changes required to draft v0.1:
```

## Governance

An answer discussed in a chat, a passing automated test, or a draft pull request is not automatically a ratification. Record the authority and evidence before updating this ledger to a settled state. Preserve prior decisions in version history rather than silently replacing them.

No work items are implied by the existence of this register.
