# Cyber-Extortion Exploitation State Machine Extension (`extortion`)

Narrow, machine-only extension: contributes **only** what the
[trajectories](../trajectories/) Exploitation State Machine (ESM) needs to
run on a **non-sexual, general data-breach / leak-threat** cyber extortion
offense — access/exfiltration/demand/leak-threat shaped, deliberately
**not** sextortion-shaped. No class hierarchy beyond the
`uco-action:Technique` metaclass pattern from
[attack-technique](../attack-technique/), and no bespoke taxonomy.

## Case

**United States v. Matthew D. Lane** (D. Mass.). Source: USAO-MA press
release "Worcester College Student Sentenced to Four Years in Prison for
Cyber Extortions" (2025-11-13) — the only source document available (no
affidavit-level detail); the exemplar is calibrated to exactly what that
press release states, with no invented phases, actions, amounts, or
affordances.

## Phases (`ex:PhaseScheme`)

| State | What it is |
|---|---|
| `ex:InitialAccess` | Unauthorized network access via stolen login credentials |
| `ex:Exfiltration` | Data transferred to attacker-leased infrastructure |
| `ex:Demand` | Ransom demanded (~$2.85M in Bitcoin) |
| `ex:LeakThreat` | Threat of worldwide public disclosure as leverage |

## Actions (`uco-action:Technique` classes)

| Class | techniqueID | Affordance abused |
|---|---|---|
| `ex:a_credential_theft` | `EX.T1` | Credential theft |
| `ex:a_exfiltrate` | `EX.T2` | Protected-network access |
| `ex:a_leak_threat` | `EX.T3` | Leak-as-leverage |

## Exemplar

`extortion-exemplar.ttl` is built from the second of Lane's two described
incidents (Aug.-Dec. 2024, a software/cloud-storage company serving school
systems) — the only one the press release describes with an explicit
access → exfiltration → demand → leak-threat chain. The first incident
(Apr.-May 2024, a telecommunications company) is thinner in the source
(no access/exfiltration method given) and is used only as corroborating
quoted evidence text on the Demand/LeakThreat phases, not modeled as a
separate trajectory.

Terminal polarity: `traj:terminalPolarity "completed"` — the modeled
offense chain (access → exfiltration → demand → leak-threat) finished in
the source. Later prosecution/sentencing is outside the machine and does
not count as mid-chain `disrupted`.

### `traj:enactsAction` wiring

Follows the arriving-state convention documented in
[`trajectories/README.md`](../trajectories/README.md#enactsaction-convention-arriving-state-not-leaving-state):
each transition's `enactsAction` is the action that *produces* its
`toState`.

| Transition | `enactsAction` | Produces |
|---|---|---|
| `InitialAccess -> Exfiltration` | `ex:a_exfiltrate` | `Exfiltration` |
| `Exfiltration -> Demand` | *(none)* | no cataloged technique distinct from exfiltration for the demand step itself; `traj:enactsAction` is optional, so this is conformant |
| `Demand -> LeakThreat` | `ex:a_leak_threat` | `LeakThreat` |

`ex:a_credential_theft` (produces `s0`/`InitialAccess`) is cataloged and
instantiated with performer/instrument/evidence, but — per the same
convention — is not wired to any transition: `s0` has no incoming
transition.

## Validation

```python
from case_uco.validation import validate_graph_file

validate_graph_file(
    "extensions/extortion/extortion-exemplar.ttl",
    extensions=["extortion"],
    profiles=["time", "prov-o"],
    strict_concepts=True,
    force_rdfs_inference=True,
)
```
