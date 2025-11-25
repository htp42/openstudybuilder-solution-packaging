import csv

from .functions.utils import load_env
from .utils.importer import BaseImporter, open_file
from .utils.metrics import Metrics

# ---------------------------------------------------------------
# Env loading
# ---------------------------------------------------------------
#
API_BASE_URL = load_env("API_BASE_URL")

MDR_COMPLEXITY_BURDENS = load_env("MDR_COMPLEXITY_BURDENS")
MDR_COMPLEXITY_ACTIVITY_BURDENS_MAPPING = load_env(
    "MDR_COMPLEXITY_ACTIVITY_BURDENS_MAPPING"
)
ACTIVITY_SUBGROUPS_PATH = "/concepts/activities/activity-sub-groups"


class ComplexityBurdens(BaseImporter):
    logging_name = "complexity_burdens"

    @open_file()
    def import_complexity_burdens(self, file):
        r = csv.DictReader(file)
        for line in r:
            data = dict(line.items())
            data["median_cost_usd"] = (
                float(data["median_cost_usd"]) if data.get("median_cost_usd") else None
            )
            self.log.info(f"Adding complexity burden '{data['burden_id']}'")
            self.api.simple_post_to_api(
                body=data, path="admin/complexity-scores/burdens"
            )

    @open_file()
    def import_complexity_activity_burdens_mapping(self, file):
        all_subgroups = self.api.get_all_from_api(ACTIVITY_SUBGROUPS_PATH)

        existing_subgroups = {}
        for item in all_subgroups:
            existing_subgroups[item["name"].strip().lower()] = {
                "uid": item["uid"],
            }

        r = csv.DictReader(file)
        for line in r:
            data = dict(line.items())

            if data["burden_id"] and data["burden_id"].strip().lower() != "null":
                activity_subgroup_uid = None
                matched_subgroup = existing_subgroups.get(
                    data["activity_subgroup_name"].strip().lower()
                )
                if matched_subgroup:
                    activity_subgroup_uid = matched_subgroup["uid"]
                    self.log.info(
                        f"Mapping Activity Subgroup '{data['activity_subgroup_name']}' to Burden '{data['burden_id']}'"
                    )
                else:
                    self.log.warning(
                        f"Activity Subgroup '{data['activity_subgroup_name']}' not found, skipping..."
                    )
                    continue

                url = f"admin/complexity-scores/burdens/activity-burdens/{activity_subgroup_uid}"
                path = "admin/complexity-scores/activity-burdens"
                self.api.simple_put(data, url, path)

    def run(self):
        self.log.info("Importing complexity score burdens")
        self.import_complexity_burdens(MDR_COMPLEXITY_BURDENS)
        self.import_complexity_activity_burdens_mapping(
            MDR_COMPLEXITY_ACTIVITY_BURDENS_MAPPING
        )
        self.log.info("Done importing complexity score burdens")


def main():
    metr = Metrics()
    migrator = ComplexityBurdens(metrics_inst=metr)
    migrator.run()
    metr.print()


if __name__ == "__main__":
    main()
