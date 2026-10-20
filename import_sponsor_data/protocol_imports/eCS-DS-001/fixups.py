"""Fix-ups for the eCS-DS-001 import, through the API.

Sets what the import tooling cannot carry on API 3.0.x. Every step reads the
target first and changes only what differs, so the script is safe to re-run.

  prepare  before the import: library content the dataset relies on
           - unit definitions in build_dataset.UNITS_TO_CREATE ("years"),
             copied from an existing unit
           - Objective Category and Endpoint Category terms the templates use.
             A term already in one category codelist is added to the other
             rather than duplicated.
  finish   after the import: the study and its templates
           - study metadata the importer drops: trial types, indication,
             diagnosis group, expected participants, short title
           - key-criteria flag on every study criteria
           - SoA footnotes (build_dataset.FOOTNOTES): an instance of each
             footnote template, attached to its SoA rows, columns or epochs
           - categories on the objective, endpoint and criteria templates
           - then verify
  verify   read-only: the study holds every item exported/ lists, and every
           endpoint is linked to an objective. Fails otherwise, since the
           importer only logs the items the API rejects.
  all      prepare and finish, in that order

Run from import_sponsor_data/ (settings come from import.env; variables
already set in the environment take precedence):
    uv run python protocol_imports/eCS-DS-001/fixups.py prepare|finish|all [--dry-run]
"""

import argparse
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def _load_env_file(path):
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"'))


_load_env_file(HERE / "import.env")
sys.path.insert(0, str(HERE.parents[1]))
sys.path.insert(0, str(HERE))

import build_dataset  # noqa: E402

from importers.run_import_mockdatajson import MockdataJson  # noqa: E402
from importers.utils.metrics import Metrics  # noqa: E402

SPONSOR = build_dataset.SPONSOR
CATEGORY_CODELISTS = {
    "objective": "Objective Category",
    "endpoint": "Endpoint Category",
    "criteria": "Criteria Category",
}
TRIAL_TYPE_SUBMISSION_VALUE = "TTYPE"
# Study collections the import fills, each listed in exported/ under the same name.
STUDY_COLLECTIONS = [
    "study-epochs",
    "study-visits",
    "study-arms",
    "study-elements",
    "study-design-cells",
    "study-activities",
    "study-activity-schedules",
    "study-objectives",
    "study-endpoints",
    "study-criteria",
    "study-compounds",
]


def _filter(**fields):
    return {
        "filters": json.dumps({k: {"v": [v], "op": "eq"} for k, v in fields.items()})
    }


def _uids(items, key="term_uid"):
    return [item.get(key) or item.get("uid") for item in items or []]


class Fixups(MockdataJson):
    """Reuses the importer's lookups, including how it resolves (and, for
    numbers, creates) template parameter values."""

    logging_name = "fixups"

    def __init__(self, dry_run):
        super().__init__(metrics_inst=Metrics())
        self.dry_run = dry_run
        self.failures = 0

    # -- helpers -------------------------------------------------------------

    def get(self, path, **params):
        return self.api.get_all_from_api(path, params=params or None) or []

    def change(self, description, action):
        """Run a write, or only describe it in a dry run."""
        if self.dry_run:
            print(f"  would {description}")
            return None
        result = action()
        if result in (None, False):
            print(f"  FAILED to {description} (see the log above)")
            self.failures += 1
        else:
            print(f"  {description}")
        return result

    def post(self, path, body):
        return self.api.simple_post_to_api(path, body)

    def patch(self, path, body):
        return self.api.simple_patch(body, path, path)

    def find_unit(self, name):
        units = self.get("/concepts/unit-definitions", **_filter(name=name))
        return next((u for u in units if u["name"] == name), None)

    def find_codelist(self, name):
        codelists = self.get("/ct/codelists", **_filter(**{"name.name": name}))
        return codelists[0] if codelists else None

    def codelist_terms(self, codelist_uid):
        return {
            term["name"]["sponsor_preferred_name"]: term
            for term in self.get("/ct/terms", codelist_uid=codelist_uid)
        }

    # -- prepare -------------------------------------------------------------

    @staticmethod
    def unit_body(unit, name):
        """The writable fields of a unit, renamed."""
        return {
            "name": name,
            "convertible_unit": unit["convertible_unit"],
            "display_unit": unit["display_unit"],
            "master_unit": unit["master_unit"],
            "us_conventional_unit": unit["us_conventional_unit"],
            "use_complex_unit_conversion": unit.get(
                "use_complex_unit_conversion", False
            ),
            "use_molecular_weight": unit.get("use_molecular_weight", False),
            "ct_units": sorted(_uids(unit.get("ct_units"))),
            "unit_subsets": sorted(_uids(unit.get("unit_subsets"))),
            "ucum": (unit.get("ucum") or {}).get("term_uid"),
            "unit_dimension": (unit.get("unit_dimension") or {}).get("term_uid"),
            "conversion_factor_to_master": unit.get("conversion_factor_to_master"),
            "comment": unit.get("comment"),
            "order": unit.get("order"),
            "definition": unit.get("definition"),
            "template_parameter": unit.get("template_parameter", False),
        }

    def ensure_units(self):
        """Create each unit as a copy of its source unit, or repair an existing
        one that differs from it (e.g. created in the UI without the
        template-parameter flag, so templates cannot use it)."""
        print("Units")
        path = "/concepts/unit-definitions"
        for name, source_name in build_dataset.UNITS_TO_CREATE.items():
            source = self.find_unit(source_name)
            if source is None:
                print(f"  FAILED: no unit '{source_name}' to copy '{name}' from")
                self.failures += 1
                continue
            wanted = self.unit_body(source, name)
            existing = self.find_unit(name)
            if existing is None:
                body = {**wanted, "library_name": source["library_name"]}
                self.change(
                    f"create and approve unit '{name}' as a copy of '{source_name}'",
                    lambda body=body: (res := self.post(path, body))
                    and self.api.approve_item(res["uid"], path),
                )
                continue
            current = self.unit_body(existing, name)
            # Keep the unit's own definition and ordering; align the rest.
            for field in ("comment", "order", "definition"):
                wanted[field] = current[field]
            differences = sorted(f for f in wanted if wanted[f] != current[f])
            if not differences:
                print(f"  ok: unit '{name}' matches '{source_name}'")
                continue
            uid = existing["uid"]
            # A unit PATCH replaces every field, so the body is complete.
            body = {
                **wanted,
                "change_description": f"Align with '{source_name}': {', '.join(differences)}",
            }

            def repair(uid=uid, body=body):
                if existing["status"] != "Draft" and not self.post(
                    f"{path}/{uid}/versions", {}
                ):
                    return None
                return self.patch(f"{path}/{uid}", body) and self.api.approve_item(
                    uid, path
                )

            self.change(
                f"align unit '{name}' with '{source_name}' (new version): {', '.join(differences)}",
                repair,
            )

    def ensure_category_terms(self):
        print("Category terms")
        wanted = {CATEGORY_CODELISTS[kind]: set() for kind in ("objective", "endpoint")}
        for kind, _item, category in build_dataset.syntax_items():
            if category and CATEGORY_CODELISTS[kind] in wanted:
                wanted[CATEGORY_CODELISTS[kind]].add(category)

        codelists = {name: self.find_codelist(name) for name in wanted}
        for name, codelist in codelists.items():
            if codelist is None:
                print(f"  FAILED: no codelist '{name}' on the target")
                self.failures += 1
                return
        terms = {
            name: self.codelist_terms(cl["codelist_uid"])
            for name, cl in codelists.items()
        }

        def next_order(codelist_name):
            orders = [
                entry.get("order") or 0
                for term in terms[codelist_name].values()
                for entry in term.get("codelists") or []
                if entry.get("codelist_uid") == codelists[codelist_name]["codelist_uid"]
            ]
            return max(orders, default=0) + 1

        for category in sorted(set().union(*wanted.values())):
            missing_in = [
                cl
                for cl, names in wanted.items()
                if category in names and category not in terms[cl]
            ]
            if not missing_in:
                print(
                    f"  ok: '{category}' in {sorted(cl for cl in wanted if category in wanted[cl])}"
                )
                continue
            existing = next(
                (terms[cl][category] for cl in terms if category in terms[cl]), None
            )
            if existing:
                for cl in missing_in:
                    body = {
                        "term_uid": existing["term_uid"],
                        "submission_value": category,
                        "order": next_order(cl),
                    }
                    path = f"/ct/codelists/{codelists[cl]['codelist_uid']}/terms"
                    self.change(
                        f"add existing term '{category}' ({existing['term_uid']}) to '{cl}'",
                        lambda path=path, body=body: self.post(path, body),
                    )
            else:
                catalogues = sorted(
                    {
                        c
                        for cl in missing_in
                        for c in codelists[cl].get("catalogue_names") or []
                    }
                )
                body = {
                    "catalogue_names": catalogues,
                    "codelists": [
                        {
                            "codelist_uid": codelists[cl]["codelist_uid"],
                            "submission_value": category,
                            "order": next_order(cl),
                        }
                        for cl in missing_in
                    ],
                    "nci_preferred_name": None,
                    "definition": category,
                    "sponsor_preferred_name": category,
                    "sponsor_preferred_name_sentence_case": category.lower(),
                    "library_name": SPONSOR,
                }
                self.change(
                    f"create and approve term '{category}' in {missing_in}",
                    lambda body=body: (res := self.post("/ct/terms", body))
                    and self.api.approve_item_names_and_attributes(
                        res["term_uid"], "/ct/terms"
                    ),
                )

    # -- finish --------------------------------------------------------------

    def find_study(self):
        listing = json.loads((build_dataset.EXPORT_DIR / "studies.json").read_text())
        study_id = listing[0]["current_metadata"]["identification_metadata"]["study_id"]
        studies = self.get(
            "/studies",
            **_filter(
                **{"current_metadata.identification_metadata.study_id": study_id}
            ),
        )
        if not studies:
            print(f"Study {study_id} not found on the target; import it first.")
            return None
        print(f"Study {study_id} ({studies[0]['uid']})")
        return studies[0]["uid"]

    def patch_study_metadata(self, study_uid):
        print("Study metadata")
        sections = ["high_level_study_design", "study_population", "study_description"]
        metadata = self.api.get_all_from_api(
            f"/studies/{study_uid}", params={"include_sections": sections}
        )["current_metadata"]
        design, population = (
            metadata["high_level_study_design"],
            metadata["study_population"],
        )

        def key(section, *names):
            # Field names changed between API versions; use the one present.
            return next((n for n in names if n in section), names[0])

        def term_refs(uids_by_name, names):
            refs = []
            for name in names:
                if uids_by_name.get(name):
                    refs.append({"term_uid": uids_by_name[name], "name": name})
                else:
                    print(f"  FAILED: '{name}' not found on the target")
                    self.failures += 1
            return refs

        patch = {}
        trial_type_key = key(design, "trial_type_codes", "trial_types_codes")
        codelist_uid = self.get_codelist_uid_from_submval(TRIAL_TYPE_SUBMISSION_VALUE)
        trial_types = (
            {
                name: term["term_uid"]
                for name, term in self.codelist_terms(codelist_uid).items()
            }
            if codelist_uid
            else {}
        )
        wanted = term_refs(trial_types, build_dataset.TRIAL_TYPES)
        if set(_uids(design.get(trial_type_key))) != set(_uids(wanted)):
            patch.setdefault("high_level_study_design", {})[trial_type_key] = wanted

        snomed = {
            name: self.lookup_dictionary_term_uid("SNOMED", name)
            for name in (build_dataset.INDICATION, build_dataset.DIAGNOSIS_GROUP)
        }
        for names, field in (
            (
                [build_dataset.INDICATION],
                key(
                    population,
                    "disease_condition_or_indication_codes",
                    "disease_conditions_or_indications_codes",
                ),
            ),
            (
                [build_dataset.DIAGNOSIS_GROUP],
                key(population, "diagnosis_group_codes", "diagnosis_groups_codes"),
            ),
        ):
            wanted = term_refs(snomed, names)
            if set(_uids(population.get(field))) != set(_uids(wanted)):
                patch.setdefault("study_population", {})[field] = wanted
        if (
            population.get("number_of_expected_subjects")
            != build_dataset.EXPECTED_SUBJECTS
        ):
            patch.setdefault("study_population", {})[
                "number_of_expected_subjects"
            ] = build_dataset.EXPECTED_SUBJECTS
        if "study_population" in patch:
            # A population patch is merged with the current values, which read
            # the minimum age back without its unit; resend it in full.
            value, unit_name = build_dataset.MINIMUM_AGE
            unit_uid = self.lookup_unit_uid(unit_name)
            patch["study_population"]["planned_minimum_age_of_subjects"] = {
                "duration_value": value,
                "duration_unit_code": {"uid": unit_uid, "name": unit_name},
            }

        description = metadata.get("study_description") or {}
        if description.get("study_short_title") != build_dataset.STUDY_SHORT_TITLE:
            patch["study_description"] = {
                "study_title": description.get("study_title")
                or build_dataset.STUDY_TITLE,
                "study_short_title": build_dataset.STUDY_SHORT_TITLE,
            }

        if not patch:
            print("  ok: nothing to change")
            return
        fields = sorted(f for section in patch.values() for f in section)
        self.change(
            f"patch study metadata: {', '.join(fields)}",
            lambda: self.patch(f"/studies/{study_uid}", {"current_metadata": patch}),
        )

    def mark_key_criteria(self, study_uid):
        print("Key criteria")
        criteria = self.get(f"/studies/{study_uid}/study-criteria")
        pending = [c for c in criteria if not c.get("key_criteria")]
        print(
            f"  {len(criteria) - len(pending)} of {len(criteria)} already key criteria"
        )
        for item in pending:
            name = (item.get("criteria") or {}).get("name_plain") or item[
                "study_criteria_uid"
            ]
            self.change(
                f"mark key criteria: {name[:70]}",
                lambda item=item: self.patch(
                    f"/studies/{study_uid}/study-criteria/{item['study_criteria_uid']}/key-criteria",
                    {"key_criteria": True},
                ),
            )

    def study_soa_items(self, study_uid):
        """SoA items a footnote can reference, keyed by (item type, name)."""
        items = {}
        for activity in self.get(f"/studies/{study_uid}/study-activities"):
            items[("StudyActivity", activity["activity"]["name"])] = activity[
                "study_activity_uid"
            ]
            subgroup = activity.get("study_activity_subgroup") or {}
            items[("StudyActivitySubGroup", subgroup.get("activity_subgroup_name"))] = (
                subgroup.get("study_activity_subgroup_uid")
            )
            group = activity.get("study_activity_group") or {}
            items[("StudyActivityGroup", group.get("activity_group_name"))] = group.get(
                "study_activity_group_uid"
            )
        for visit in self.get(f"/studies/{study_uid}/study-visits"):
            items[("StudyVisit", visit.get("description"))] = visit["uid"]
        for epoch in self.get(f"/studies/{study_uid}/study-epochs"):
            items[("StudyEpoch", epoch["epoch_name"])] = epoch["uid"]
        return items

    def attach_footnotes(self, study_uid):
        print("SoA footnotes")
        path = f"/studies/{study_uid}/study-soa-footnotes"
        existing = {
            (f.get("footnote") or {}).get("name")
            or (f.get("template") or {}).get("name")
            for f in self.get(path)
        }
        items = self.study_soa_items(study_uid)
        for item, references in build_dataset.FOOTNOTES:
            label = item.rendered()[:60]
            if build_dataset.html(item.rendered()) in existing:
                print(f"  ok: {label}")
                continue
            referenced = [
                {"item_uid": items.get(ref), "item_name": ref[1], "item_type": ref[0]}
                for ref in references
            ]
            missing = [r["item_name"] for r in referenced if not r["item_uid"]]
            templates = self.get(
                "/footnote-templates", **_filter(name=build_dataset.html(item.text))
            )
            if missing or not templates:
                reason = (
                    f"no SoA item {missing}"
                    if missing
                    else "no footnote template; import first"
                )
                print(f"  FAILED: {label}: {reason}")
                self.failures += 1
                continue

            def create(
                item=item, template_uid=templates[0]["uid"], referenced=referenced
            ):
                terms = build_dataset.parameter_terms(item)
                for parameter in terms:
                    for term in parameter["terms"]:
                        term["uid"] = self.lookup_or_create_parameter_value_uid(term)
                        if term["uid"] is None:
                            return None
                body = {
                    "footnote_data": {
                        "footnote_template_uid": template_uid,
                        "parameter_terms": terms,
                        "library_name": item.library,
                    },
                    "referenced_items": referenced,
                }
                return self.api.simple_post_to_api(
                    path, body, params={"create_footnote": "true"}
                )

            targets = ", ".join(r["item_name"] for r in referenced)
            self.change(f"add footnote on {targets}: {label}", create)
        print(f"  {len(build_dataset.FOOTNOTES)} footnotes defined")

    def assign_template_categories(self):
        print("Template categories")
        done = set()
        for kind, item, category in build_dataset.syntax_items():
            if not category:
                continue
            path = f"/{kind}-templates"
            name = build_dataset.html(item.text)
            templates = self.get(path, **_filter(name=name))
            if not templates:
                print(f"  FAILED: {kind} template not found: {item.text[:70]}")
                self.failures += 1
                continue
            template = templates[0]
            if template["uid"] in done:
                continue
            done.add(template["uid"])
            category_uid = self.lookup_codelist_term_uid(
                CATEGORY_CODELISTS[kind], category
            )
            if category_uid is None:
                print(
                    f"  FAILED: no '{category}' term in {CATEGORY_CODELISTS[kind]}; run prepare"
                )
                self.failures += 1
                continue
            current = _uids(template.get("categories"))
            if category_uid in current:
                continue
            body = {
                "indication_uids": _uids(template.get("indications")),
                "category_uids": [*current, category_uid],
            }
            if kind == "objective":
                body["is_confirmatory_testing"] = bool(
                    template.get("is_confirmatory_testing")
                )
            else:
                body["sub_category_uids"] = _uids(template.get("sub_categories"))
            self.change(
                f"set {kind} template category '{category}': {item.text[:60]}",
                lambda path=path, uid=template["uid"], body=body: self.patch(
                    f"{path}/{uid}/indexings", body
                ),
            )
        print(f"  {len(done)} templates checked")

    def report_unlinked_endpoints(self, study_uid):
        endpoints = self.get(f"/studies/{study_uid}/study-endpoints")
        unlinked = [e for e in endpoints if not e.get("study_objective")]
        print(
            f"Endpoints: {len(endpoints) - len(unlinked)} of {len(endpoints)} linked to an objective"
        )
        for endpoint in unlinked:
            print(f"  not linked: {(endpoint.get('endpoint') or {}).get('name_plain')}")
        return len(unlinked)

    # -- verify --------------------------------------------------------------

    def verify(self, study_uid):
        """The importer logs a rejected item and carries on, so check that the
        study holds everything exported/ asked for."""
        print("Study contents")
        exported_uid = json.loads(
            (build_dataset.EXPORT_DIR / "studies.json").read_text()
        )[0]["uid"]
        for collection in STUDY_COLLECTIONS:
            path = (
                build_dataset.EXPORT_DIR / f"studies.{exported_uid}.{collection}.json"
            )
            expected = len(json.loads(path.read_text()))
            actual = len(self.get(f"/studies/{study_uid}/{collection}"))
            if actual < expected:
                print(f"  FAILED: {collection}: {actual} of {expected}")
                self.failures += 1
            else:
                print(f"  {collection}: {actual}")
        self.failures += self.report_unlinked_endpoints(study_uid)

    # -- entry points --------------------------------------------------------

    def prepare(self):
        self.ensure_units()
        self.ensure_category_terms()

    def finish(self):
        study_uid = self.find_study()
        if study_uid is None:
            self.failures += 1
            return
        self.patch_study_metadata(study_uid)
        self.mark_key_criteria(study_uid)
        self.attach_footnotes(study_uid)
        self.assign_template_categories()
        self.verify(study_uid)


def main():
    parser = argparse.ArgumentParser(description="Fix-ups for the eCS-DS-001 import")
    parser.add_argument("step", choices=["prepare", "finish", "verify", "all"])
    parser.add_argument(
        "--dry-run", action="store_true", help="read only; print planned changes"
    )
    args = parser.parse_args()

    fixups = Fixups(dry_run=args.dry_run)
    if args.step in ("prepare", "all"):
        fixups.prepare()
    if args.step in ("finish", "all"):
        fixups.finish()
    if args.step == "verify":
        study_uid = fixups.find_study()
        if study_uid is None:
            fixups.failures += 1
        else:
            fixups.verify(study_uid)
    if fixups.failures:
        print(f"{fixups.failures} step(s) failed")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
