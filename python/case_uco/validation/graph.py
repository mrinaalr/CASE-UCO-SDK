"""SHACL validation wrapper around the CASE Utilities ``case_validate`` CLI.

Gives MCP callers (AI agents, Link-Look, scripts) a bounded way to validate a
produced CASE/UCO graph file before it is submitted for human review. The
wrapper invokes the locally installed ``case_validate`` tool with an argument
array (no shell), parses its conformance report, and fails honestly with
typed errors when the validator or the graph file is unavailable.

This module never fabricates validation results: if ``case_validate`` is not
installed, callers receive ``validator_unavailable`` instead of a fake pass.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from case_uco.validation.extension_paths import extension_dir as _extension_dir
from case_uco.validation.extension_paths import find_extension_dir as _find_extension_dir


def _discover_project_root() -> Path:
    """Locate the monorepo root that holds ``extensions/`` and ``ontology/``."""
    here = Path(__file__).resolve()
    candidates = [
        here.parents[3],  # .../CASE-UCO-Libraries from case_uco/validation/
        here.parents[2],
        Path.cwd(),
        *here.parents,
    ]
    for candidate in candidates:
        if (candidate / "extensions").is_dir() and (
            (candidate / "ontology").is_dir() or (candidate / "ontology").exists()
        ):
            return candidate
    return here.parents[3]


PROJECT_ROOT = _discover_project_root()
DEFAULT_BUILT_VERSION = "case-1.4.0"

VALIDATOR_NAME = "case_validate"
SUPPORTED_GRAPH_EXTENSIONS = {".json", ".jsonld", ".json-ld", ".ttl", ".turtle"}
MAX_GRAPH_BYTES = 50 * 1024 * 1024
DEFAULT_TIMEOUT_SECONDS = 180

# Markers shared with Link-Look's graph_validation.rs parser so both sides of
# the roundtrip report the same conformance semantics.
_CONFORMS_KEY = "conforms"
_VIOLATION_MARKER = "Constraint Violation"
_WARNING_MARKER = "NonExistentCDOConceptWarning"


@dataclass(frozen=True)
class GraphValidationReport:
    """Structured, redaction-safe validation result.

    ``verification_status`` is ``"complete"`` only when every required
    stage (SHACL plus, when enabled, strict concept coverage including the
    pinned upper-ontology registry) actually ran; otherwise it is
    ``"could_not_verify"`` and ``conforms`` is never ``True`` (fail-closed,
    issue #55).

    Independent stage reporting (CQ-36): ``stage_status`` lists
    ``bundle_resolution``, ``shacl_execution``, ``shacl_conformance``,
    ``coverage_execution``, and ``coverage_conformance`` separately.
    """

    conforms: bool | None
    warning_count: int
    violation_count: int
    exit_code: int
    validator_name: str
    safe_summary: str
    undeclared_concepts: tuple[str, ...] = ()
    concept_guidance: str = ""
    unknown_upper_ontology_terms: tuple[str, ...] = ()
    role_mismatches: tuple[tuple[str, str, str], ...] = ()
    profile_not_selected: tuple[dict[str, Any], ...] = ()
    verification_status: str = "complete"
    verification_errors: tuple[str, ...] = ()
    selected_profiles: tuple[str, ...] = ()
    requested_profiles: tuple[str, ...] = ()
    selected_extensions: tuple[str, ...] = ()
    bundle_fingerprint: str | None = None
    bundle_resources: tuple[dict[str, Any], ...] = ()
    compatibility_notes: tuple[str, ...] = ()
    bundle_cache_status: str | None = None
    stage_status: tuple[tuple[str, str], ...] = ()
    validator_version: str | None = None
    # Truncated case_validate stdout/stderr for negative-fixture matching
    # (expected violation / constraint identifiers). Empty when unavailable.
    validator_diagnostics: str = ""


def _validator_beside_interpreter() -> str | None:
    """case_validate installed next to the current interpreter.

    An MCP process launched by absolute path to a venv python often does not
    put that venv's bin directory on PATH, so shutil.which misses the CLI.
    """

    # Do not resolve the interpreter. A venv python is often a symlink into
    # Homebrew or the system framework, and resolving it leaves the venv bin.
    sibling = Path(sys.executable).parent / VALIDATOR_NAME
    if sibling.is_file() and os.access(sibling, os.X_OK):
        return str(sibling)
    return None


def validator_command() -> str | None:
    """Absolute path to case_validate, or None when it is not installed."""

    found = shutil.which(VALIDATOR_NAME)
    if found:
        return found
    return _validator_beside_interpreter()


def validator_available() -> bool:
    """Return True when the case_validate CLI can be executed."""

    return validator_command() is not None


def _validator_package_version() -> str | None:
    try:
        import importlib.metadata as metadata

        return metadata.version("case-utils")
    except Exception:  # noqa: BLE001
        return None


def load_extension_ontology_paths(
    ext_name: str,
    *,
    mode: str = "subset",
    project_root: Path = PROJECT_ROOT,
) -> list[Path]:
    """Return ontology graph paths for an extension.

    mode ``subset`` uses the extension's ``validation-subset.json`` when present
    (recommended for MCP / press-release KGs). mode ``full`` uses the extension
    manifest (all owl/shacl/bridge files). Extension directories are resolved
    across both vendoring roots (``extensions/`` and ``ontology/``).
    """

    ext_dir = _extension_dir(ext_name, project_root)
    paths: list[Path] = []
    if mode == "subset":
        subset_path = ext_dir / "validation-subset.json"
        if subset_path.exists():
            subset = json.loads(subset_path.read_text(encoding="utf-8"))
            for rel in subset.get("ontology_files", []):
                full = ext_dir / rel
                if full.exists():
                    paths.append(full)
            if paths:
                return paths
    manifest_path = ext_dir / "manifest.json"
    if not manifest_path.exists():
        return paths
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for key in ("owl_files", "shacl_files", "bridge_files"):
        for rel_path in manifest.get(key, []):
            full_path = ext_dir / rel_path
            if full_path.exists():
                paths.append(full_path)
    return paths


def resolve_extension_dependencies(
    extension_names: list[str],
    project_root: Path = PROJECT_ROOT,
) -> list[str]:
    """Expand an extension list with manifest ``depends_on`` entries.

    An extension whose exemplars/graphs reuse another extension's terms (e.g.
    ``rico`` builds on ``legalproc``) declares ``"depends_on": [...]`` in its
    manifest; callers then only need to name the top-level extension. The
    ``:full`` suffix on a requested name is preserved; dependencies load in
    their default (subset-preferred) mode.

    Fail-closed (issue #55) — typed ``ValueError`` instead of a silently
    partial extension set: ``extension_unknown`` (a requested extension has
    no manifest), ``extension_dependency_missing`` (a ``depends_on`` entry
    has no manifest), ``extension_manifest_malformed`` (unparseable
    manifest), ``extension_dependency_cycle`` (circular ``depends_on``).
    """

    def _manifest_for(clean: str) -> dict[str, Any] | None:
        ext_dir = _find_extension_dir(clean, project_root)
        manifest_path = None if ext_dir is None else ext_dir / "manifest.json"
        if manifest_path is None or not manifest_path.is_file():
            return None
        try:
            payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError("extension_manifest_malformed") from exc
        if not isinstance(payload, dict):
            raise ValueError("extension_manifest_malformed")
        return payload

    resolved: list[str] = []
    seen: set[str] = set()
    # (name, dependency chain from the requested root, requested directly?)
    queue: list[tuple[str, tuple[str, ...], bool]] = [
        (name, (), True) for name in extension_names
    ]
    while queue:
        name, chain, requested = queue.pop(0)
        clean = name.removesuffix(":full")
        if clean in chain:
            raise ValueError("extension_dependency_cycle")
        if clean in seen:
            continue
        manifest = _manifest_for(clean)
        if manifest is None:
            raise ValueError(
                "extension_unknown" if requested else "extension_dependency_missing"
            )
        seen.add(clean)
        resolved.append(name)
        for dep in manifest.get("depends_on", []):
            queue.append((str(dep), chain + (clean,), False))
    return resolved


def extension_has_validation_subset(ext_name: str, project_root: Path = PROJECT_ROOT) -> bool:
    """Return True when an extension publishes a validation-subset manifest."""

    ext_dir = _find_extension_dir(ext_name, project_root)
    return ext_dir is not None and (ext_dir / "validation-subset.json").is_file()


def extension_ontology_args(
    extension_names: list[str] | None,
    project_root: Path = PROJECT_ROOT,
) -> list[str]:
    """Build case_validate flags for one or more extension manifests."""

    if not extension_names:
        return []
    extension_names = resolve_extension_dependencies(extension_names, project_root)
    args: list[str] = [
        "--built-version",
        DEFAULT_BUILT_VERSION,
        "--allow-info",
    ]
    used_subset = False
    for ext_name in extension_names:
        mode = "full" if ext_name.endswith(":full") else "subset"
        clean_name = ext_name.removesuffix(":full")
        if mode == "subset" and extension_has_validation_subset(clean_name, project_root):
            used_subset = True
        rel_paths = load_extension_ontology_paths(
            clean_name, mode=mode, project_root=project_root
        )
        for full_path in rel_paths:
            args.extend(["--ontology-graph", str(full_path)])
    if used_subset:
        pass  # subset modules are self-contained; skip rdfs inference
    else:
        args.extend(["--inference", "rdfs"])
    return args


def validate_graph_file(
    graph_path: str | Path,
    allow_warning: bool = True,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    extensions: list[str] | None = None,
    project_root: Path = PROJECT_ROOT,
    strict_concepts: bool = True,
    extra_ontology_graphs: list[str | Path] | None = None,
    force_rdfs_inference: bool = False,
    profiles: list[str] | None = None,
    allow_foundational_pair: bool = False,
    bundle_manifest_path: str | Path | None = None,
) -> GraphValidationReport:
    """Validate a CASE/UCO graph file with the local case_validate tool.

    When ``profiles`` **or** ``extensions`` are set (and ``strict_concepts``
    is True), resolution goes through ``resolve_validation_bundle`` so SHACL
    and concept coverage share one fingerprinted ontology set (CQ-27/CQ-28).
    Upper-ontology terms require explicit ``profiles=[...]`` (CQ-29); recipe
    validation always supplies them.

    Independent stages are reported separately (CQ-36): bundle resolution,
    SHACL execution, SHACL conformance, coverage execution, coverage
    conformance.

    Raises ValueError with a typed message for every honest-failure path:
    ``validator_unavailable``, ``graph_missing``, ``unsupported_graph_extension``,
    ``graph_oversized``, ``validation_timeout``.
    """

    command = validator_command()
    if not command:
        raise ValueError("validator_unavailable")
    # Deployment filesystem policy: graph reads must stay inside configured
    # read roots (typed error "source_outside_read_roots" when violated).
    try:
        import workspace_policy  # optional MCP deployment policy

        graph = workspace_policy.check_read_path(
            graph_path, include_write_roots=True
        )
    except ImportError:
        graph = Path(graph_path).expanduser().resolve()
    if not graph.exists() or not graph.is_file():
        raise ValueError("graph_missing")
    if graph.suffix.lower() not in SUPPORTED_GRAPH_EXTENSIONS:
        raise ValueError("unsupported_graph_extension")
    if graph.stat().st_size > MAX_GRAPH_BYTES:
        raise ValueError("graph_oversized")

    validator_version = _validator_package_version()
    args = [command]
    if allow_warning:
        args.append("--allow-warning")

    resolved_bundle = None
    bundle_resolution_status = "skipped"
    # Construct one shared bundle whenever profiles or extensions need the
    # same resource set for SHACL + strict coverage (CQ-27/CQ-28).
    if profiles or (extensions and strict_concepts) or (
        extra_ontology_graphs and (profiles or extensions)
    ):
        from case_uco.validation.bundle import ValidationBundleError, resolve_validation_bundle

        try:
            resolved_bundle = resolve_validation_bundle(
                extensions=extensions,
                profiles=profiles,
                project_root=project_root,
                allow_foundational_pair=allow_foundational_pair,
                extra_ontology_graphs=extra_ontology_graphs,
            )
            bundle_resolution_status = "complete"
        except ValidationBundleError as exc:
            raise ValueError(str(exc)) from exc
        if bundle_manifest_path:
            resolved_bundle.write_manifest(bundle_manifest_path)
        args.extend(["--built-version", DEFAULT_BUILT_VERSION, "--allow-info"])
        for path in resolved_bundle.ontology_graph_paths():
            args.extend(["--ontology-graph", str(path)])
        if resolved_bundle.inference:
            args.extend(["--inference", resolved_bundle.inference])
        elif force_rdfs_inference:
            args.extend(["--inference", "rdfs"])
    else:
        extension_args = extension_ontology_args(extensions, project_root=project_root)
        if extension_args:
            args.extend(extension_args)
        elif extensions:
            args.extend(["--built-version", DEFAULT_BUILT_VERSION])
        if extra_ontology_graphs:
            for graph_path_extra in extra_ontology_graphs:
                args.extend(["--ontology-graph", str(graph_path_extra)])
        if force_rdfs_inference and "--inference" not in args:
            args.extend(["--inference", "rdfs"])

    args.append(str(graph))
    shacl_execution_status = "complete"
    try:
        completed = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise ValueError("validation_timeout") from exc

    combined = f"{completed.stdout}\n{completed.stderr}"
    conforms = _parse_conforms(combined)
    violation_count = combined.count(_VIOLATION_MARKER)
    warning_count = combined.count(_WARNING_MARKER)
    exit_code = completed.returncode

    if conforms is True and violation_count == 0:
        shacl_conformance_status = "conforms"
    elif conforms is False or violation_count > 0:
        shacl_conformance_status = "nonconformant"
    else:
        shacl_conformance_status = "unknown"
        shacl_execution_status = "failed"

    if exit_code == 0 and conforms is not False and violation_count == 0:
        if warning_count > 0:
            summary = (
                f"Graph conforms with {warning_count} validator warning(s); "
                "review warnings before relying on extension concepts."
            )
        elif extensions:
            mode_note = ""
            if any(not ext.endswith(":full") for ext in extensions):
                mode_note = " (validation-subset)"
            summary = (
                f"Graph conforms to CASE/UCO SHACL shapes with extension(s): "
                f"{', '.join(extensions)}.{mode_note}"
            )
        else:
            summary = "Graph conforms to CASE/UCO SHACL shapes."
    elif conforms is False or violation_count > 0:
        summary = (
            f"Graph does not conform: {violation_count} constraint violation(s). "
            "Fix the graph before submitting it for review."
        )
    else:
        summary = (
            "Validator could not produce a conformance result; "
            "the graph content may be malformed."
        )

    undeclared: tuple[str, ...] = ()
    concept_guidance = ""
    unknown_upper: tuple[str, ...] = ()
    role_mismatches: tuple[tuple[str, str, str], ...] = ()
    profile_not_selected: tuple[dict[str, Any], ...] = ()
    verification_status = "complete"
    verification_errors: tuple[str, ...] = ()
    coverage_execution_status = "skipped"
    coverage_conformance_status = "skipped"

    if strict_concepts:
        coverage_execution_status = "complete"
        try:
            from case_uco.validation.coverage import check_graph_concepts

            coverage = check_graph_concepts(
                graph,
                project_root=project_root,
                extensions=extensions if resolved_bundle is None else None,
                selected_profiles=(
                    list(resolved_bundle.profiles) if resolved_bundle is not None else []
                ),
                bundle=resolved_bundle,
            )
        except Exception as exc:  # honest failure: never fake coverage
            conforms = None
            verification_status = "could_not_verify"
            verification_errors = (f"concept_coverage_failed:{type(exc).__name__}",)
            coverage_execution_status = "failed"
            coverage_conformance_status = "could_not_verify"
            summary = (
                f"{summary} Additionally, the concept coverage check could "
                f"not run ({type(exc).__name__}); treat the result as "
                "unverified."
            )
        else:
            verification_status = coverage.verification_status
            verification_errors = coverage.verification_errors
            if coverage.verification_status != "complete":
                conforms = False
                coverage_conformance_status = "could_not_verify"
            elif coverage.ok:
                coverage_conformance_status = "ok"
            else:
                coverage_conformance_status = "failed"
            if not coverage.ok:
                undeclared = coverage.undeclared_classes + coverage.undeclared_properties
                unknown_upper = coverage.unknown_upper_ontology_terms
                role_mismatches = coverage.role_mismatches
                profile_not_selected = tuple(
                    {
                        "iri": item.iri,
                        "required_profile": item.required_profile,
                        "used_as": item.used_as,
                        "selected_profiles": list(item.selected_profiles),
                    }
                    for item in coverage.profile_not_selected
                )
                concept_guidance = coverage.guidance
                shacl_passed = conforms is not False and violation_count == 0
                conforms = False
                parts: list[str] = []
                if undeclared:
                    shown = ", ".join(undeclared[:8])
                    more = f" (+{len(undeclared) - 8} more)" if len(undeclared) > 8 else ""
                    parts.append(
                        f"Graph uses {len(undeclared)} class/property term(s) not declared "
                        f"in CASE/UCO or supported extension ontologies: {shown}{more}."
                    )
                if unknown_upper:
                    shown = ", ".join(unknown_upper[:8])
                    parts.append(
                        f"Graph uses {len(unknown_upper)} term(s) inside profiled "
                        f"upper-ontology namespaces that the pinned ontology releases "
                        f"do not declare: {shown}."
                    )
                if profile_not_selected:
                    shown = ", ".join(
                        f"{p['iri']} (needs {p['required_profile']})"
                        for p in profile_not_selected[:4]
                    )
                    parts.append(
                        f"Graph uses {len(profile_not_selected)} upper-ontology "
                        f"term(s) whose profile was not selected: {shown}."
                    )
                if role_mismatches:
                    shown = "; ".join(
                        f"{iri} (declared as {declared_role}, used as {used_as})"
                        for iri, declared_role, used_as in role_mismatches[:4]
                    )
                    parts.append(
                        f"Graph uses {len(role_mismatches)} declared term(s) in the "
                        f"wrong RDF role: {shown}."
                    )
                if verification_errors:
                    parts.append(
                        f"Required verification stage(s) could not run "
                        f"({', '.join(verification_errors)}); the result is "
                        "unverified, not conformant."
                    )
                else:
                    parts.append(
                        "Draft a change proposal or add the concept(s) to an extension "
                        "ontology, then re-validate."
                    )
                concept_summary = " ".join(parts)
                summary = concept_summary if shacl_passed else f"{summary} {concept_summary}"

    # CQ-36: independent stage reporting.
    stage_status: list[tuple[str, str]] = [
        ("bundle_resolution", bundle_resolution_status),
        ("shacl_execution", shacl_execution_status),
        ("shacl_conformance", shacl_conformance_status),
        ("coverage_execution", coverage_execution_status),
        ("coverage_conformance", coverage_conformance_status),
    ]

    # Cap diagnostics so reports stay bounded while still exposing SHACL
    # Source Shape / Constraint Component identifiers for negative fixtures.
    _diag_limit = 16_384
    diagnostics = combined.strip()
    if len(diagnostics) > _diag_limit:
        diagnostics = diagnostics[:_diag_limit] + "\n…[truncated]"

    return GraphValidationReport(
        conforms=conforms,
        warning_count=warning_count,
        violation_count=violation_count,
        exit_code=exit_code,
        validator_name=VALIDATOR_NAME,
        safe_summary=summary,
        undeclared_concepts=undeclared,
        concept_guidance=concept_guidance,
        unknown_upper_ontology_terms=unknown_upper,
        role_mismatches=role_mismatches,
        profile_not_selected=profile_not_selected,
        verification_status=verification_status,
        verification_errors=verification_errors,
        selected_profiles=tuple(resolved_bundle.profiles) if resolved_bundle else (),
        requested_profiles=(
            tuple(resolved_bundle.requested_profiles) if resolved_bundle else tuple(profiles or ())
        ),
        selected_extensions=(
            tuple(resolved_bundle.extensions) if resolved_bundle else tuple(extensions or ())
        ),
        bundle_fingerprint=resolved_bundle.fingerprint if resolved_bundle else None,
        bundle_resources=tuple(resolved_bundle.to_manifest(portable=True)["resources"])
        if resolved_bundle
        else (),
        compatibility_notes=tuple(resolved_bundle.compatibility_notes) if resolved_bundle else (),
        bundle_cache_status=resolved_bundle.cache_status if resolved_bundle else None,
        stage_status=tuple(stage_status),
        validator_version=validator_version,
        validator_diagnostics=diagnostics,
    )


def report_to_dict(report: GraphValidationReport) -> dict[str, Any]:
    """Serialize a report into the MCP tool result shape."""

    payload: dict[str, Any] = {
        "conforms": report.conforms,
        "warning_count": report.warning_count,
        "violation_count": report.violation_count,
        "exit_code": report.exit_code,
        "validator_name": report.validator_name,
        "safe_summary": report.safe_summary,
        "verification_status": report.verification_status,
    }
    if report.validator_version:
        payload["validator_version"] = report.validator_version
    if report.verification_errors:
        payload["verification_errors"] = list(report.verification_errors)
    if report.undeclared_concepts:
        payload["undeclared_concepts"] = list(report.undeclared_concepts)
    if report.unknown_upper_ontology_terms:
        payload["unknown_upper_ontology_terms"] = list(
            report.unknown_upper_ontology_terms
        )
    if report.profile_not_selected:
        payload["profile_not_selected"] = list(report.profile_not_selected)
    if report.role_mismatches:
        payload["role_mismatches"] = [
            {"iri": iri, "declared_role": declared_role, "used_as": used_as}
            for iri, declared_role, used_as in report.role_mismatches
        ]
    if report.concept_guidance:
        payload["concept_guidance"] = report.concept_guidance
    if report.selected_profiles:
        payload["selected_profiles"] = list(report.selected_profiles)
    if report.requested_profiles:
        payload["requested_profiles"] = list(report.requested_profiles)
    if report.selected_extensions:
        payload["selected_extensions"] = list(report.selected_extensions)
    if report.bundle_fingerprint:
        payload["bundle_fingerprint"] = report.bundle_fingerprint
    if report.bundle_resources:
        payload["bundle_resources"] = list(report.bundle_resources)
    if report.compatibility_notes:
        payload["compatibility_notes"] = list(report.compatibility_notes)
    if report.bundle_cache_status:
        payload["bundle_cache_status"] = report.bundle_cache_status
    if report.stage_status:
        payload["stage_status"] = [
            {"stage": stage, "status": status} for stage, status in report.stage_status
        ]
    return payload


def _parse_conforms(output: str) -> bool | None:
    for line in output.splitlines():
        key, sep, value = line.partition(":")
        if not sep or key.strip().lower() != _CONFORMS_KEY:
            continue
        normalized = value.strip().lower()
        if normalized == "true":
            return True
        if normalized == "false":
            return False
    return None

__all__ = [
    "DEFAULT_BUILT_VERSION",
    "DEFAULT_TIMEOUT_SECONDS",
    "MAX_GRAPH_BYTES",
    "PROJECT_ROOT",
    "SUPPORTED_GRAPH_EXTENSIONS",
    "VALIDATOR_NAME",
    "GraphValidationReport",
    "extension_has_validation_subset",
    "extension_ontology_args",
    "load_extension_ontology_paths",
    "report_to_dict",
    "resolve_extension_dependencies",
    "validate_graph_file",
    "validator_available",
    "_parse_conforms",
]
