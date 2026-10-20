"""Preflight for the eCS-DS-001 import. Writes nothing to the target.

1. Simulation (offline): runs the real mockdatajson importer over exported/
   against a recording stub API. Every handler runs, so a malformed file shows
   up as an importer error here. Every name the importer resolves on the
   target is recorded.
2. Target check (read-only, skipped with --offline): resolves each recorded
   name on the target with the importer's own lookup functions, and reports
   what is missing and not created by this import.

Run from import_sponsor_data/ (settings come from import.env; variables
already set in the environment take precedence):
    uv run python protocol_imports/eCS-DS-001/preflight.py [--offline]

Exit code: 0 when nothing is missing, 1 otherwise, 2 when the target is unreachable.
"""

import argparse
import json
import logging
import os
import sys
from collections import Counter
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent
EXPORT_DIR = HERE / "exported"
COMPOUNDS_DIR = HERE / "compounds"


def _load_env_file(path):
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"'))


# The importer modules read their settings at import time.
_load_env_file(HERE / "import.env")
os.environ["IMPORT_PROJECTS"] = str(EXPORT_DIR / "projects.json")
sys.path.insert(0, str(HERE.parents[1]))
sys.path.insert(0, str(HERE))

import build_dataset  # noqa: E402

from importers import run_import_mockdatajson  # noqa: E402
from importers.run_import_mockdatajson import MockdataJson  # noqa: E402
from importers.utils.metrics import Metrics  # noqa: E402

SEP = "|"

# Sentence case of every parameter value, to render instance names.
SENTENCE_CASE = {
    (value.type, value.name): value.sentence_case
    for _kind, item, _category in build_dataset.syntax_items()
    for group in item.values
    for value in group
}

# Where a parameter value comes from, when this import creates it.
PARAMETER_SOURCES = {
    "Activity": ("concept", "activities/activities"),
    "ActivitySubGroup": ("concept", "activities/activity-sub-groups"),
    "Compound": ("concept", "compounds"),
    "DiseaseDisorder": ("dictionary", "SNOMED"),
}

# Template categories: a name missing here is dropped from the template, and
# nothing else fails.
OPTIONAL_CODELISTS = {"Objective Category", "Endpoint Category", "Criteria Category"}

STATUS_NOTES = {
    "MISSING": " (skipped by the importer, or fails the study PATCH)",
    "EXISTS": " (re-running adds duplicates)",
    "PREPARE": " (run fixups.py prepare before the import)",
    "OPTIONAL": " (template category dropped, nothing else affected)",
    "CREATED": " (created by this import)",
}


def _name_from_fake_uid(uid):
    return uid.rsplit(SEP, 1)[-1] if isinstance(uid, str) else None


class _Collector(logging.Handler):
    def __init__(self):
        super().__init__(level=logging.WARNING)
        self.records = []

    def emit(self, record):
        self.records.append((record.levelname, record.getMessage()))


class RecordingApi:
    """Stands in for ApiBinding. Keeps just enough study state for the
    importer's read-after-write lookups to behave like a real target."""

    def __init__(self):
        self.posts = []
        self.patches = []
        self.programmes, self.projects = [], []
        self.study = None
        self.epochs, self.visits, self.arms, self.elements = [], [], [], []
        self.study_activities, self.instances = [], {}
        self.templates = {}
        self.endpoints_without_objective = []

    def update_headers(self, _headers):
        pass

    def get_all_identifiers(self, responses, identifier, value=None):
        responses = responses or []
        if value is None:
            return [item[identifier] for item in responses]
        return {item[identifier]: item[value] for item in responses}

    def get_all_from_api_paged(
        self, path, params=None, items_only=True, page_size=1000
    ):
        return []

    def get_all_from_api(self, path, params=None, items_only=True):
        if path.startswith("/concepts/unit-definitions"):
            return [
                {"name": "days", "uid": "UNIT|days"},
                {"name": "weeks", "uid": "UNIT|weeks"},
            ]
        if path == "/clinical-programmes":
            return self.programmes
        if path == "/projects":
            return self.projects
        if path.endswith("/study-arms"):
            return self.arms
        if path.endswith("/study-elements"):
            return self.elements
        if path.endswith("/study-epochs"):
            return self.epochs
        if path.endswith("/study-visits"):
            return [
                {
                    "description": v["description"],
                    "visit_type": {"sponsor_preferred_name": v["visit_type"]},
                    "time_value": v["time_value"],
                    "time_unit_name": "days",
                }
                for v in self.visits
            ]
        return []

    def _epoch_name(self, subtype):
        same = [e for e in self.epochs if e["epoch_subtype_name"] == subtype]
        return subtype if not same else f"{subtype} {len(same) + 1}"

    def visit_names(self):
        days = {}
        for visit in self.visits:
            if visit["time_reference"] == "Global anchor visit":
                days[visit["uid"]] = visit["time_value"]
            else:
                ref = next(
                    v for v in self.visits if v["visit_type"] == visit["time_reference"]
                )
                days[visit["uid"]] = days[ref["uid"]] + visit["time_value"]
        epoch_order = {e["uid"]: e["order"] for e in self.epochs}
        ordered = sorted(
            self.visits, key=lambda v: (epoch_order[v["epoch_uid"]], days[v["uid"]])
        )
        return {f"Visit {i}": v["uid"] for i, v in enumerate(ordered, start=1)}

    def simple_post_to_api(self, path, body, simple_path=None, params=None):
        self.posts.append((path, body))
        uid = f"SIM{SEP}{len(self.posts)}"
        if path == "/clinical-programmes":
            self.programmes.append({"name": body["name"], "uid": uid})
        elif path == "/projects":
            self.projects.append({"project_number": body["project_number"], "uid": uid})
        elif path == "/studies":
            study_id = f"{body['project_number']}-{body['study_number']}"
            self.study = {
                "uid": "Study_SIM",
                "current_metadata": {"identification_metadata": {"study_id": study_id}},
            }
            return self.study
        elif path.endswith("/study-epochs/preview"):
            subtype = _name_from_fake_uid(body["epoch_subtype"])
            return {
                "epoch": body["epoch_subtype"],
                "order": len(self.epochs) + 1,
                "epoch_name": self._epoch_name(subtype),
            }
        elif path.endswith("/study-epochs"):
            subtype = _name_from_fake_uid(body["epoch_subtype"])
            self.epochs.append(
                {
                    "uid": uid,
                    "epoch_name": self._epoch_name(subtype),
                    "epoch_subtype_name": subtype,
                    "description": body["description"],
                    "order": body["order"],
                }
            )
        elif path.endswith("/study-visits"):
            self.visits.append(
                {
                    "uid": uid,
                    "epoch_uid": body["study_epoch_uid"],
                    "visit_type": _name_from_fake_uid(body["visit_type"]["term_uid"]),
                    "time_reference": _name_from_fake_uid(
                        body["time_reference"]["term_uid"]
                    ),
                    "time_value": body["time_value"],
                    "description": body["description"],
                }
            )
        elif path.endswith("/study-arms"):
            self.arms.append({"name": body["name"], "arm_uid": uid})
        elif path.endswith("/study-elements"):
            self.elements.append({"name": body["name"], "element_uid": uid})
        elif path.endswith("/study-activities"):
            self.study_activities.append(
                (
                    _name_from_fake_uid(body["activity_uid"]),
                    _name_from_fake_uid(body["activity_group_uid"]),
                    _name_from_fake_uid(body["activity_subgroup_uid"]),
                    uid,
                )
            )
        elif (
            "/study-objectives" in path
            or "/study-endpoints" in path
            or "/study-criteria" in path
        ):
            kind = path.rsplit("/study-", 1)[-1].split("?")[0]
            kind = {"objectives": "objective", "endpoints": "endpoint"}.get(kind, kind)
            data = body[f"{kind}_data"]
            parameters = data.get("parameter_terms") or []
            # Name the instance the way the API does, from the resolved values.
            name = build_dataset.render(
                _name_from_fake_uid(data[f"{kind}_template_uid"]),
                [
                    [
                        build_dataset.Value(
                            term["type"],
                            term["name"],
                            SENTENCE_CASE.get(
                                (term["type"], term["name"]), term["name"]
                            ),
                        )
                        for term in parameter["terms"]
                    ]
                    for parameter in parameters
                ],
                [parameter.get("conjunction") or "and" for parameter in parameters],
            )
            self.instances.setdefault(kind, {})[name] = uid
            if kind == "endpoint" and not body.get("study_objective_uid"):
                self.endpoints_without_objective.append(name)
        elif path.endswith("-templates"):
            kind = path.strip("/")[: -len("-templates")].replace("-", "_")
            uid = f"TPL{SEP}{kind}{SEP}{body['name']}"
            self.templates.setdefault(kind, {})[body["name"]] = uid
        return {"uid": uid, "term_uid": uid}

    def patch_to_api(self, body, path):
        self.patches.append((path, body))
        return body

    def post_to_api(self, obj, body=None, path=None):
        self.posts.append((path or obj.get("path"), body or obj.get("body")))
        return {"uid": f"SIM{SEP}{len(self.posts)}"}

    def approve_item(self, uid, url):
        return True


def simulate():
    """Run the importer against RecordingApi; return (lookups, api, log records)."""
    lookups = []
    collector = _Collector()
    logging.getLogger(MockdataJson.logging_name).addHandler(collector)

    api = RecordingApi()
    importer = MockdataJson(api=api, metrics_inst=Metrics())

    def record(kind, *key):
        lookups.append((kind, *key))

    def ct(codelist, value, key="sponsor_preferred_name", uid_key="term_uid"):
        record("ct", codelist, value)
        return f"CT{SEP}{codelist}{SEP}{value}"

    def codelist_term(codelist, name):
        record("codelist", codelist, name)
        return f"CT{SEP}{codelist}{SEP}{name}"

    def concept(name, endpoint, subset=None, library=None, only_final=False):
        record("concept", endpoint, name, library, only_final)
        return f"CONCEPT{SEP}{endpoint}{SEP}{name}"

    def unit(name, subset=None):
        record("unit", subset, name)
        return f"UNIT{SEP}{name}"

    def dictionary_term(dictionary, name):
        record("dictionary", dictionary, name)
        return f"DICT{SEP}{dictionary}{SEP}{name}"

    def template(name, template_type, subtype=None, log=True, shortname=None):
        return api.templates.get(template_type, {}).get(name)

    real_caseless = importer.caseless_dict_lookup

    def caseless(input_dict, key):
        if input_dict is importer.all_study_times:
            record("study_time_unit", key)
        return real_caseless(input_dict, key)

    def study_by_key(key, value, silent=False):
        if (
            api.study
            and key.endswith("study_id")
            and value
            == (api.study["current_metadata"]["identification_metadata"]["study_id"])
        ):
            return api.study
        return None

    def study_epoch(study_uid, epoch_name):
        return next(
            (e["uid"] for e in api.epochs if e["epoch_name"] == epoch_name), None
        )

    def study_visit(study_uid, visit_name):
        return api.visit_names().get(visit_name)

    def study_activity(study_uid, activity_name, group_name=None, subgroup_name=None):
        for name, group, subgroup, uid in api.study_activities:
            if (name, group, subgroup) == (activity_name, group_name, subgroup_name):
                return uid
        return None

    def study_instance(name, study_uid, template_type):
        return api.instances.get(template_type, {}).get(name)

    def parameter_value(value):
        record("parameter", value.get("type"), value.get("name"))
        return f"PARAM{SEP}{value.get('type')}{SEP}{value.get('name')}"

    overrides = {
        "lookup_ct_term_uid": ct,
        "lookup_codelist_term_uid": codelist_term,
        "lookup_concept_uid": concept,
        "lookup_unit_uid": unit,
        "lookup_dictionary_term_uid": dictionary_term,
        "lookup_dictionary_uid": lambda name: f"DICTIONARY{SEP}{name}",
        "fetch_dictionary_terms": lambda name: [],
        "fetch_all_activities": lambda: {},
        "fetch_all_activity_groups": lambda: {},
        "fetch_all_activity_subgroups": lambda: {},
        "lookup_template_uid": template,
        "lookup_preinstance_uid": lambda *a, **k: None,
        "lookup_timeframe": lambda name: None,
        "caseless_dict_lookup": caseless,
        "get_study_by_key": study_by_key,
        "lookup_study_epoch_uid": study_epoch,
        "lookup_study_visit_uid": study_visit,
        "lookup_study_activity_uid": study_activity,
        "lookup_study_template_instance_uid": study_instance,
        "fetch_study_compounds": lambda study_uid: [],
        "lookup_or_create_parameter_value_uid": parameter_value,
    }
    for attr, func in overrides.items():
        setattr(importer, attr, func)

    importer.run()
    logging.getLogger(MockdataJson.logging_name).removeHandler(collector)
    return lookups, api, collector.records


def _load(directory, name):
    with open(directory / name, encoding="utf-8") as handle:
        return json.load(handle)


def created_by_import():
    """Names this import creates itself, per lookup target."""
    names = {
        ("concept", "activities/activities"): {
            a["name"] for a in _load(EXPORT_DIR, "concepts.activities.activities.json")
        },
        ("concept", "activities/activity-groups"): {
            g["name"]
            for g in _load(EXPORT_DIR, "concepts.activities.activity-groups.json")
        },
        ("concept", "activities/activity-sub-groups"): {
            s["name"]
            for s in _load(EXPORT_DIR, "concepts.activities.activity-sub-groups.json")
        },
        ("dictionary", "SNOMED"): {
            t["name"] for t in _load(EXPORT_DIR, "dictionaries.SNOMED.json")
        },
    }
    compounds = {c["name"] for c in _load(COMPOUNDS_DIR, "compounds.json")}
    names[("concept", "compounds")] = compounds
    names[("concept", "compound-aliases")] = compounds  # default alias per compound
    names[("concept", "medicinal-products")] = {
        m["name"] for m in _load(COMPOUNDS_DIR, "medicinal_products.json")
    }
    return names


def prepared_by_fixups():
    """Names fixups.py prepare creates; it runs before the import."""
    objective_categories = {o["category"] for o in build_dataset.OBJECTIVES} - {None}
    endpoint_categories = {
        category
        for objective in build_dataset.OBJECTIVES
        for _item, _level, category in objective["endpoints"]
    } - {None}
    return {
        ("parameter", "Age Unit"): set(build_dataset.UNITS_TO_CREATE),
        ("codelist", "Objective Category"): objective_categories,
        ("codelist", "Endpoint Category"): endpoint_categories,
    }


def check_target(lookups, study_activities, target=None):
    """Resolve every recorded lookup on the target. Returns rows of
    (status, kind, where, name)."""
    if target is None:
        target = MockdataJson(metrics_inst=Metrics())
    created = created_by_import()
    prepared = prepared_by_fixups()
    existing_activities = set(target.fetch_all_activities())
    existing_groups = set(target.fetch_all_activity_groups())
    existing_subgroups = set(target.fetch_all_activity_subgroups())
    loose = {
        "activities/activities": existing_activities,
        "activities/activity-groups": existing_groups,
        "activities/activity-sub-groups": existing_subgroups,
    }

    rows = []
    for lookup in dict.fromkeys(lookups):  # unique, in order
        kind = lookup[0]
        if kind == "ct":
            _, where, name = lookup
            found = target.lookup_ct_term_uid(where, name)
        elif kind == "codelist":
            _, where, name = lookup
            found = target.lookup_codelist_term_uid(where, name)
        elif kind == "concept":
            _, where, name, library, only_final = lookup
            found = target.lookup_concept_uid(
                name, where, library=library, only_final=only_final
            )
        elif kind == "unit":
            _, where, name = lookup
            found = target.lookup_unit_uid(name, subset=where)
        elif kind == "dictionary":
            _, where, name = lookup
            found = target.lookup_dictionary_term_uid(where, name)
        elif kind == "study_time_unit":
            where, name = "Study Time units", lookup[1]
            found = any(k.lower() == name.lower() for k in target.all_study_times)
        elif kind == "parameter":
            _, where, name = lookup
            if where in run_import_mockdatajson.TEMPLATE_PARAM_MAP:
                # Simple values such as numbers are created when used.
                rows.append(("CREATED", kind, where, name))
                continue
            terms = target.get_template_parameters(where) or []
            found = any(t["name"] == name or t["name"].lower() == name for t in terms)
            if not found and name in created.get(PARAMETER_SOURCES.get(where), set()):
                rows.append(("CREATED", kind, where, name))
                continue
        else:
            continue
        if found:
            status = "OK"
        elif name in prepared.get((kind, where), set()):
            status = "PREPARE"
        elif name in created.get((kind, where), set()):
            # The importer only creates what does not exist under any status.
            status = "MISSING" if name in loose.get(where, set()) else "CREATED"
        elif kind == "codelist" and where in OPTIONAL_CODELISTS:
            status = "OPTIONAL"
        else:
            status = "MISSING"
        rows.append((status, kind, where, name))

    # Existing activities must carry the grouping the study activity uses.
    by_activity = {}
    for activity, group, subgroup, _uid in study_activities:
        by_activity.setdefault(activity, set()).add((group, subgroup))
    for activity, pairs in by_activity.items():
        items = target.api.get_all_from_api(
            "/concepts/activities/activities",
            params={"filters": json.dumps({"name": {"v": [activity], "op": "eq"}})},
        )
        if not items:
            continue
        have = {
            (g.get("activity_group_name"), g.get("activity_subgroup_name"))
            for item in items
            for g in item.get("activity_groupings") or []
        }
        for group, subgroup in sorted(pairs - have):
            rows.append(("MISSING", "grouping", activity, f"{group} / {subgroup}"))

    # The study itself.
    metadata = _load(EXPORT_DIR, "studies.json")[0]["current_metadata"][
        "identification_metadata"
    ]
    if target.lookup_study_uid_from_id(metadata["study_id"]):
        rows.append(("EXISTS", "study", "study_id", metadata["study_id"]))
    elif target.get_study_by_key(
        "current_metadata.identification_metadata.study_number",
        metadata["study_number"],
        silent=True,
    ):
        rows.append(
            ("MISSING", "study", "study_number already used", metadata["study_number"])
        )
    return rows


def main():
    parser = argparse.ArgumentParser(description="Preflight for the eCS-DS-001 import")
    parser.add_argument(
        "--offline", action="store_true", help="only run the simulation"
    )
    args = parser.parse_args()

    print("== Simulation (no network) ==")
    lookups, api, log_records = simulate()
    posts = Counter(
        path.split("?")[0].replace("Study_SIM", "{study}") for path, _ in api.posts
    )
    for path, count in sorted(posts.items()):
        print(f"  POST {path:60s} x{count}")
    print(f"  PATCH study metadata x{len(api.patches)}")
    problems = [(lvl, msg) for lvl, msg in log_records if lvl == "ERROR"]
    problems += [
        ("ERROR", f"endpoint not linked to an objective: {n}")
        for n in api.endpoints_without_objective
    ]
    for level, message in log_records:
        if level == "WARNING":
            print(f"  warning: {message}")
    for level, message in problems:
        print(f"  {level}: {message}")
    print(f"  {len(set(lookups))} distinct names resolved on the target")
    if problems:
        print("Simulation found problems in the import files.")
        return 1

    if args.offline:
        return 0

    # The compounds step runs separately; its only terminology lookups are these.
    for product in _load(COMPOUNDS_DIR, "pharmaceutical_products.json"):
        for route in product["routes_of_administration"]:
            lookups.append(("codelist", "Route of Administration", route["name"]))
        for form in product["dosage_forms"]:
            lookups.append(("codelist", "Pharmaceutical Dosage Form", form["name"]))

    print(f"\n== Target check: {run_import_mockdatajson.API_BASE_URL} (read-only) ==")
    sys.stdout.flush()
    try:
        rows = check_target(lookups, api.study_activities)
    except (requests.exceptions.RequestException, SystemExit) as exc:
        # ApiBinding exits when the API is down or CT packages are missing,
        # after logging why.
        print(f"  Target not usable ({exc!r}); see the log message above.")
        return 2
    for status in ("MISSING", "PREPARE", "EXISTS", "OPTIONAL", "CREATED", "OK"):
        selected = [r for r in rows if r[0] == status]
        print(f"  {status}: {len(selected)}{STATUS_NOTES.get(status, '')}")
        if status != "OK":
            for _, kind, where, name in selected:
                print(f"    {kind:16s} {where:40s} {name}")
    if any(r[0] in ("MISSING", "PREPARE") for r in rows):
        print(
            "Missing names would be skipped by the importer (or fail the study PATCH)."
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
