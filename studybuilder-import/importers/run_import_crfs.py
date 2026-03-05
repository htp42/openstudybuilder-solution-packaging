import csv
import json
from collections import defaultdict

from importers.functions.parsers import map_boolean

from .functions.utils import load_env
from .utils.importer import BaseImporter, open_file
from .utils.metrics import Metrics

# ---------------------------------------------------------------
# Env loading
# ---------------------------------------------------------------
#
API_BASE_URL = load_env("API_BASE_URL")
MDR_MIGRATION_ODM_VENDOR_NAMESPACES = load_env("MDR_MIGRATION_ODM_VENDOR_NAMESPACES")
MDR_MIGRATION_ODM_VENDOR_ATTRIBUTES = load_env("MDR_MIGRATION_ODM_VENDOR_ATTRIBUTES")
MDR_MIGRATION_ODM_STUDY_EVENTS = load_env("MDR_MIGRATION_ODM_STUDY_EVENTS")
MDR_MIGRATION_ODM_FORMS = load_env("MDR_MIGRATION_ODM_FORMS")
MDR_MIGRATION_ODM_ITEM_GROUPS = load_env("MDR_MIGRATION_ODM_ITEM_GROUPS")
MDR_MIGRATION_ODM_ITEMS = load_env("MDR_MIGRATION_ODM_ITEMS")
MDR_MIGRATION_ODM_FORMS_TO_ODM_STUDY_EVENTS = load_env(
    "MDR_MIGRATION_ODM_FORMS_TO_ODM_STUDY_EVENTS"
)
MDR_MIGRATION_ODM_ITEM_GROUPS_TO_ODM_FORMS = load_env(
    "MDR_MIGRATION_ODM_ITEM_GROUPS_TO_ODM_FORMS"
)
MDR_MIGRATION_ODM_ITEMS_TO_ODM_ITEM_GROUPS = load_env(
    "MDR_MIGRATION_ODM_ITEMS_TO_ODM_ITEM_GROUPS"
)
MDR_MIGRATION_ODM_ITEMS_TO_ACTIVITY_INSTANCES = load_env(
    "MDR_MIGRATION_ODM_ITEMS_TO_ACTIVITY_INSTANCES"
)


# name, prefix, namespace
def odm_vendor_namespace(data):
    return {
        "path": "/concepts/odms/vendor-namespaces",
        "body": {
            "name": data["name"],
            "prefix": data["prefix"],
            "url": data["url"],
        },
    }


# name, data_type, value_regex
def odm_vendor_attribute(data, vendor_namespace_uid):
    return {
        "path": "/concepts/odms/vendor-attributes",
        "body": {
            "name": data["name"],
            "compatible_types": data["compatible_types"].split("|"),
            "data_type": data["data_type"],
            "value_regex": data["value_regex"],
            "vendor_namespace_uid": vendor_namespace_uid,
        },
    }


# library,oid,name,effective_date,retired_date
def odm_study_event(data):
    return {
        "path": "/concepts/odms/study-events",
        "body": {
            "name": data["name"],
            "oid": data["oid"],
            "effective_date": data["effective_date"] or None,
            "retired_date": data["retired_date"] or None,
            "description": f"description for {data['name']}",
        },
    }


# library,oid,name,prompt,repeating,translated_texts,aliases
def odm_form(data):
    return {
        "path": "/concepts/odms/forms",
        "body": {
            "name": data["name"],
            "oid": data["oid"],
            "repeating": data["repeating"],
            "translated_texts": data.get("translated_texts", []),
            "aliases": data.get("aliases", []),
        },
    }


# library,oid,name,prompt,repeating,isreferencedata,sasdatasetname,domain,origin,purpose,comment,language,description,instruction
def odm_item_group(data, domain_uids):
    return {
        "path": "/concepts/odms/item-groups",
        "body": {
            "name": data["name"],
            "oid": data["oid"],
            "repeating": data["repeating"],
            "is_reference_data": data["is_reference_data"],
            "sas_dataset_name": data["sas_dataset_name"],
            "origin": data["origin"],
            "purpose": data["purpose"],
            "locked": "no",
            "comment": data["comment"],
            "translated_texts": data.get("translated_texts", []),
            "aliases": data.get("aliases", []),
            "sdtm_domain_uids": domain_uids,
        },
    }


# library,oid,name,prompt,datatype,length,significantdigits,codelist,term,unit,sasfieldname,sdsvarname,origin,comment,language,description,instruction
def odm_item(data, units, terms):
    try:
        length = int(data["length"])
    except ValueError:
        length = None
    try:
        significant_digits = int(data["significant_digits"])
    except ValueError:
        significant_digits = None

    return {
        "path": "/concepts/odms/items",
        "body": {
            "name": data["name"],
            "oid": data["oid"],
            "datatype": data["datatype"],
            "prompt": data["prompt"],
            "length": length,
            "significant_digits": significant_digits,
            "sas_field_name": data["sas_field_name"],
            "sds_var_name": data["sds_var_name"],
            "origin": data["origin"],
            "comment": data["comment"],
            "allows_multi_choice": False,
            "translated_texts": data.get("translated_texts", []),
            "aliases": data.get("aliases", []),
            "codelist": (
                {
                    "uid": data["codelist"]["uid"],
                    "allows_multi_choice": data["codelist"]["allows_multi_choice"],
                }
                if data["codelist"]
                else None
            ),
            "unit_definitions": units,
            "terms": terms,
        },
    }


def odm_form_to_study_event(uid, data):
    return {
        "path": f"/concepts/odms/study-events/{uid}/forms",
        "body": [
            {
                "uid": data["uid"],
                "order_number": data["order_number"],
                "mandatory": data["mandatory"],
                "locked": data["locked"],
                "collection_exception_condition_oid": data[
                    "collection_exception_condition_oid"
                ]
                or None,
            }
        ],
    }


def odm_item_group_to_form(uid, data):
    return {
        "path": f"/concepts/odms/forms/{uid}/item-groups",
        "body": [
            {
                "uid": data["uid"],
                "order_number": data["order_number"],
                "mandatory": data["mandatory"],
                "collection_exception_condition_oid": data[
                    "collection_exception_condition_oid"
                ]
                or None,
                "vendor": {"attributes": []},
            }
        ],
    }


def odm_item_to_item_group(uid, data):
    return {
        "path": f"/concepts/odms/item-groups/{uid}/items",
        "body": [
            {
                "uid": data["uid"],
                "order_number": data["order_number"],
                "mandatory": data["mandatory"],
                "key_sequence": data["key_sequence"] or None,
                "method_oid": data["method_oid"] or None,
                "imputation_method_oid": data["imputation_method_oid"] or None,
                "role": data["role"] or None,
                "role_codelist_oid": data["role_codelist_oid"] or None,
                "collection_exception_condition_oid": data[
                    "collection_exception_condition_oid"
                ]
                or None,
                "vendor": {"attributes": []},
            }
        ],
    }


def odm_item_to_activity_instance(item):
    # odm_item_to_activity_instance_relationship
    return {
        "path": "/concepts/odms/items/",
        "body": item,
    }


class Crfs(BaseImporter):
    logging_name = "crfs"

    def __init__(self, api=None, metrics_inst=None):
        super().__init__(api=api, metrics_inst=metrics_inst)

    def _fetch_codelist_terms_and_return_codelist_uid(
        self, codelists, codelist_submval
    ):
        codelist = self.api.get_codelist_uid(codelist_submval)
        if codelist not in codelists:
            new_codelist = {}
            terms = self.api.get_all_from_api(f"/ct/codelists/{codelist}/terms")
            for term in terms:
                new_codelist[term["submission_value"]] = term["term_uid"]
                codelists[codelist] = new_codelist
        return codelist

    def _transform_aliases(self, aliases: str | None):
        rs = []

        if not aliases:
            return rs

        for alias in aliases.split("||"):
            _alias = alias.split("::", maxsplit=1)
            if not _alias[0]:
                continue
            context, name = _alias
            rs.append(
                {
                    "name": name,
                    "context": context,
                }
            )

        return rs

    def _transform_translated_texts(self, translated_texts: str | None):
        rs = []

        if not translated_texts:
            return rs

        for translated_text in translated_texts.split("||"):
            _translated_text = translated_text.split("::", maxsplit=2)
            if not _translated_text[0]:
                continue
            text_type, language, text = _translated_text
            rs.append(
                {
                    "text_type": text_type,
                    "language": language,
                    "text": text,
                }
            )

        return rs

    @open_file()
    def handle_odm_vendor_namespaces(self, csvfile):
        csvdata = csv.DictReader(csvfile)
        res = []
        for row in csvdata:
            if len(row) == 0:
                continue
            self.log.info(f'Adding odm vendor namespace {row["name"]}')
            data = odm_vendor_namespace(row)

            # Create vendor namespace, and leave in draft state (no approve)
            # TODO check if it exists before posting?
            res.append(self.api.post_to_api(data))
        return res

    @open_file()
    def handle_odm_vendor_attributes(self, csvfile, vendor_namespace_uid):
        csvdata = csv.DictReader(csvfile)

        for row in csvdata:
            if len(row) == 0:
                continue
            self.log.info(f'Adding odm vendor attribute {row["name"]}')
            data = odm_vendor_attribute(row, vendor_namespace_uid)

            # Create vendor attribute, and leave in draft state (no approve)
            # TODO check if it exists before posting?
            self.api.post_to_api(data)

    @open_file()
    def handle_odm_study_events(self, csvfile):
        csvdata = csv.DictReader(csvfile)

        for row in csvdata:
            if len(row) == 0:
                continue
            self.log.info(f'Adding odm study event {row["name"]}')
            data = odm_study_event(row)

            # Create study event, and leave in draft state (no approve)
            # TODO check if it exists before posting?
            self.api.post_to_api(data)

    @open_file()
    def handle_odm_forms(self, csvfile):
        csvdata = csv.DictReader(csvfile)

        for row in csvdata:
            if len(row) == 0:
                continue
            self.log.info(f'Adding odm form {row["name"]}')

            row["aliases"] = self._transform_aliases(row["aliases"])
            row["translated_texts"] = self._transform_translated_texts(
                row["translated_texts"]
            )

            data = odm_form(row)

            # Create study event, and leave in draft state (no approve)
            # TODO check if it exists before posting?
            self.api.post_to_api(data)

    @open_file()
    def handle_odm_item_groups(self, csvfile):
        csvdata = csv.DictReader(csvfile)
        params = {
            "filters": json.dumps(
                {"name": {"v": ["SDTM Domain Abbreviation"], "op": "eq"}}
            ),
            "page_number": 1,
            "page_size": 0,
        }
        domain_cl_uid = self.api.get_all_from_api(
            "/ct/codelists/attributes", params=params
        )
        if len(domain_cl_uid) == 0:
            self.log.warning("Unable to find codelist for SDTM domain abbreviation")
            return
        cl_uid = domain_cl_uid[0]["codelist_uid"]
        domain_terms = self.api.get_all_from_api(f"/ct/codelists/{cl_uid}/terms")

        all_sdtm_domains = self.api.get_all_identifiers(
            domain_terms,
            identifier="submission_value",
            value="term_uid",
        )
        print("-----------")
        print(all_sdtm_domains)

        for row in csvdata:
            if len(row) == 0:
                continue
            self.log.info(f"Adding odm item group '{row['name']}'")

            # Look up sdtm domains
            domains = []
            for domain in row["sdtm_domains"].split("||"):
                if not domain:
                    continue
                domain_uid = all_sdtm_domains.get(domain)
                if domain_uid is not None:
                    domains.append(domain_uid)
                else:
                    self.log.warning(f"Unable to find domain '{domain}'")

            row["aliases"] = self._transform_aliases(row["aliases"])
            row["translated_texts"] = self._transform_translated_texts(
                row["translated_texts"]
            )

            data = odm_item_group(row, domains)

            # Create study event, and leave in draft state (no approve)
            # TODO check if it exists before posting?
            self.api.post_to_api(data)

    @open_file()
    def handle_odm_items(self, csvfile):
        csvdata = csv.DictReader(csvfile)
        codelists = {}

        all_units = self.api.get_all_identifiers(
            self.api.get_all_from_api("/concepts/unit-definitions"),
            identifier="name",
            value="uid",
        )

        for row in csvdata:
            if len(row) == 0:
                continue
            self.log.info(f'Adding odm item {row["name"]}')

            row["codelist"] = {}
            term_dicts = []
            codelist_submission_value = row["codelist_submission_value"]
            if codelist_submission_value != "":
                row["codelist"]["uid"] = (
                    self._fetch_codelist_terms_and_return_codelist_uid(
                        codelists, codelist_submission_value
                    )
                )
                row["codelist"]["allows_multi_choice"] = False
                terms = row["terms"]
                if terms != "":
                    for term in terms.split("||"):
                        term = term.strip().split("_")[0]
                        term_uid = codelists.get(row["codelist"]["uid"], {}).get(term)
                        if term_uid is not None:
                            term_dict = {
                                "uid": term_uid,
                                "mandatory": True,
                                "order": len(term_dicts) + 1,
                            }
                            term_dicts.append(term_dict)
                        else:
                            self.log.warning(
                                f"Unable to find term {term} in codelist {row["codelist"]["uid"]}"
                            )

            units = []
            unit_definitions = row["unit_definitions"]
            if unit_definitions != "":
                for unit in unit_definitions.split("||"):
                    unit_uid = all_units.get(unit)
                    if unit_uid is not None:
                        unit_dict = {"uid": unit_uid, "mandatory": True}
                        units.append(unit_dict)
                    else:
                        self.log.warning(f"Unable to find unit {unit}")

            row["aliases"] = self._transform_aliases(row["aliases"])
            row["translated_texts"] = self._transform_translated_texts(
                row["translated_texts"]
            )

            data = odm_item(row, units, term_dicts)

            # Create study event, and leave in draft state (no approve)
            # TODO check if it exists before posting?
            self.api.post_to_api(data)

    @open_file()
    def handle_odm_forms_to_study_events(self, csvfile):
        csvdata = csv.DictReader(csvfile)
        odm_forms = self.api.get_all_from_api("/concepts/odms/forms")
        odm_study_events = self.api.get_all_from_api("/concepts/odms/study-events")

        all_forms = {}
        for form in odm_forms:
            all_forms[form["oid"]] = form["uid"]

        all_study_events = {}
        for study_event in odm_study_events:
            all_study_events[study_event["oid"]] = study_event["uid"]

        for row in csvdata:
            if len(row) == 0:
                continue
            self.log.info(
                f"Adding odm form '{row['form_oid']}' to study event '{row['study_event_oid']}'"
            )

            if row["form_oid"] not in all_forms:
                self.log.warning(f"form '{row['form_oid']}' not found, skipping")
                continue
            if row["study_event_oid"] not in all_study_events:
                self.log.warning(
                    f"Study Event '{row['study_event_oid']}' not found, skipping"
                )
                continue

            row["uid"] = all_forms[row["form_oid"]]

            data = odm_form_to_study_event(
                all_study_events[row["study_event_oid"]], row
            )

            self.api.post_to_api(data)

    @open_file()
    def handle_odm_item_groups_to_forms(self, csvfile):
        csvdata = csv.DictReader(csvfile)
        odm_itemgroups = self.api.get_all_from_api("/concepts/odms/item-groups")
        odm_forms = self.api.get_all_from_api("/concepts/odms/forms")

        all_itemgroups = {}
        for itemgroup in odm_itemgroups:
            all_itemgroups[itemgroup["oid"]] = itemgroup["uid"]

        all_forms = {}
        for form in odm_forms:
            all_forms[form["oid"]] = form["uid"]

        for row in csvdata:
            if len(row) == 0:
                continue
            self.log.info(
                f"Adding odm item group '{row['item_group_oid']}' to form '{row['form_oid']}'"
            )

            if row["item_group_oid"] not in all_itemgroups:
                self.log.warning(
                    f"Item group '{row['item_group_oid']}' not found, skipping"
                )
                continue
            if row["form_oid"] not in all_forms:
                self.log.warning(f"Form '{row['form_oid']}' not found, skipping")
                continue

            row["uid"] = all_itemgroups[row["item_group_oid"]]

            data = odm_item_group_to_form(all_forms[row["form_oid"]], row)

            self.api.post_to_api(data)

    @open_file()
    def handle_odm_items_to_item_groups(self, csvfile):
        csvdata = csv.DictReader(csvfile)
        odm_items = self.api.get_all_from_api("/concepts/odms/items")
        odm_itemgroups = self.api.get_all_from_api("/concepts/odms/item-groups")

        all_items = {}
        for item in odm_items:
            all_items[item["oid"]] = item["uid"]

        all_itemgroups = {}
        for itemgroup in odm_itemgroups:
            all_itemgroups[itemgroup["oid"]] = itemgroup["uid"]

        for row in csvdata:
            if len(row) == 0:
                continue
            self.log.info(
                f"Adding odm item '{row['item_oid']}' to item group '{row['item_group_oid']}'"
            )

            if row["item_oid"] not in all_items:
                self.log.warning(f"Item '{row['item_oid']}' not found, skipping")
                continue
            if row["item_group_oid"] not in all_itemgroups:
                self.log.warning(
                    f"Item group '{row['item_group_oid']}' not found, skipping"
                )
                continue

            row["uid"] = all_items[row["item_oid"]]

            data = odm_item_to_item_group(all_itemgroups[row["item_group_oid"]], row)

            self.api.post_to_api(data)

    @open_file()
    def handle_odm_items_to_activity_instances(self, csvfile):
        csvdata = list(csv.DictReader(csvfile))

        item_oids = {data["item_oid"] for data in csvdata}
        item_group_oids = {data["item_group_oid"] for data in csvdata}
        form_oids = {data["form_oid"] for data in csvdata}
        activity_instance_names = {data["activity_instance_name"] for data in csvdata}

        odm_items = self.api.get_all_from_api(
            "/concepts/odms/items",
            params={"filters": json.dumps({"oid": {"v": list(item_oids)}})},
        )
        odm_item_groups = self.api.get_all_from_api(
            "/concepts/odms/item-groups",
            params={"filters": json.dumps({"oid": {"v": list(item_group_oids)}})},
        )
        odm_forms = self.api.get_all_from_api(
            "/concepts/odms/forms",
            params={"filters": json.dumps({"oid": {"v": list(form_oids)}})},
        )
        activity_instances = self.api.get_all_from_api(
            "/concepts/activities/activity-instances",
            params={
                "filters": json.dumps({"name": {"v": list(activity_instance_names)}})
            },
        )

        data_grouped_by_item = defaultdict(list)
        for row in csvdata:
            item_oid = row.get("item_oid")
            if item_oid:
                data_grouped_by_item[item_oid].append(row)

        for item_oid, rows in data_grouped_by_item.items():
            if not (
                item := next((oi for oi in odm_items if oi["oid"] == item_oid), None)
            ):
                self.log.warning("ODM Item '%s' not found, skipping", item_oid)
                continue

            activity_instances_to_add = []

            for row in rows:
                if len(row) == 0:
                    continue

                self.log.info(
                    "Connecting ODM Item '%s' of ODM Item Group '%s' of ODM Form '%s' to Activity Instance '%s' with Activity Item Class '%s'",
                    item_oid,
                    row["item_group_oid"],
                    row["form_oid"],
                    row["activity_instance_name"],
                    row["activity_item_class_name"],
                )

                if not (
                    item_group := next(
                        (
                            oig
                            for oig in odm_item_groups
                            if oig["oid"] == row["item_group_oid"]
                        ),
                        None,
                    )
                ):
                    self.log.warning(
                        "ODM Item Group '%s' not found, skipping", row["item_group_oid"]
                    )
                    continue

                if item_oid not in [oig["oid"] for oig in item_group["items"]]:
                    self.log.warning(
                        "ODM Item '%s' is not part of ODM Item Group '%s', skipping",
                        item_oid,
                        row["item_group_oid"],
                    )
                    continue

                if not (
                    form := next(
                        (of for of in odm_forms if of["oid"] == row["form_oid"]),
                        None,
                    )
                ):
                    self.log.warning(
                        "ODM Form '%s' not found, skipping", row["form_oid"]
                    )
                    continue

                if row["item_group_oid"] not in [
                    of["oid"] for of in form["item_groups"]
                ]:
                    self.log.warning(
                        "ODM Item Group '%s' is not part of ODM Form '%s', skipping",
                        row["item_group_oid"],
                        row["form_oid"],
                    )
                    continue

                if not (
                    activity_instance := next(
                        (
                            ai
                            for ai in activity_instances
                            if ai["name"] == row["activity_instance_name"]
                        ),
                        None,
                    )
                ):
                    self.log.warning(
                        "Activity Instance '%s' not found, skipping",
                        row["activity_instance_name"],
                    )
                    continue

                if not (
                    activity_item_class := next(
                        (
                            ai["activity_item_class"]
                            for ai in activity_instance["activity_items"]
                            if ai["activity_item_class"]["name"]
                            == row["activity_item_class_name"]
                        ),
                        None,
                    )
                ):
                    self.log.warning(
                        "Activity Item Class '%s' not found in Activity Instance '%s', skipping",
                        row["activity_item_class_name"],
                        row["activity_instance_name"],
                    )
                    continue

                activity_instances_to_add.append(
                    {
                        "activity_instance_uid": activity_instance["uid"],
                        "activity_item_class_uid": activity_item_class["uid"],
                        "odm_form_uid": form["uid"],
                        "odm_item_group_uid": item_group["uid"],
                        "order": row["order"] if row["order"].isdigit() else 99999,
                        "primary": map_boolean(row["primary"]),
                        "preset_response_value": row["preset_response_value"],
                        "value_condition": row["value_condition"],
                        "value_dependent_map": row["value_dependent_map"],
                    }
                )

            item["codelist"] = (
                {
                    "uid": item["codelist"].get("uid"),
                    "allows_multi_choice": item["codelist"].get(
                        "allows_multi_choice", False
                    ),
                }
                if item["codelist"]
                else None
            )

            for term in item.get("terms", []):
                term["uid"] = term["term_uid"]

            if activity_instances_to_add:
                item["activity_instances"] = activity_instances_to_add

                data = odm_item_to_activity_instance(item)

                self.api.patch_to_api(data["body"], data["path"])

    def run(self):
        self.log.info("Importing CRFs")
        vendor_namespace_res = self.handle_odm_vendor_namespaces(
            MDR_MIGRATION_ODM_VENDOR_NAMESPACES
        )
        if vendor_namespace_res:
            self.handle_odm_vendor_attributes(
                MDR_MIGRATION_ODM_VENDOR_ATTRIBUTES,
                (
                    vendor_namespace_res[0]
                    and vendor_namespace_res[0]["uid"]
                    or "OdmVendorNamespace_000001"
                ),
            )
        self.handle_odm_study_events(MDR_MIGRATION_ODM_STUDY_EVENTS)
        self.handle_odm_forms(MDR_MIGRATION_ODM_FORMS)
        self.handle_odm_item_groups(MDR_MIGRATION_ODM_ITEM_GROUPS)
        self.handle_odm_items(MDR_MIGRATION_ODM_ITEMS)
        self.handle_odm_forms_to_study_events(
            MDR_MIGRATION_ODM_FORMS_TO_ODM_STUDY_EVENTS
        )
        self.handle_odm_item_groups_to_forms(MDR_MIGRATION_ODM_ITEM_GROUPS_TO_ODM_FORMS)
        self.handle_odm_items_to_item_groups(MDR_MIGRATION_ODM_ITEMS_TO_ODM_ITEM_GROUPS)
        self.handle_odm_items_to_activity_instances(
            MDR_MIGRATION_ODM_ITEMS_TO_ACTIVITY_INSTANCES
        )
        self.log.info("Done importing CRFs")


def main():
    metr = Metrics()
    migrator = Crfs(metrics_inst=metr)
    migrator.run()
    metr.print()


if __name__ == "__main__":
    main()
