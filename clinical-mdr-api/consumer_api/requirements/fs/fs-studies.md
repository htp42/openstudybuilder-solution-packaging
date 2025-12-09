# Overview

This document describes a set of GET endpoints in the StudyBuilder Consumer API, which expose information about various entities defined in the `Studies` section of StudyBuilder.

Detailed API specification of each endpoint is found in the `consumer_api/openapi.json` file.

# Studies

## FS-ConsumerApi-Studies-Studies-Get-010 [`URS-ConsumerApi-Studies`]

Consumers must be able to retrieve a paginated list of all studies by calling the `GET /studies` endpoint.

### Request

It must be possible to filter items by study `id`.

It must be possible to sort items by `uid`, `id_prefix` and `number` fields.

### Response

Each item in the response must include basic information about a study (`uid`, `id`), together with a list of all existing study versions for each study (`version_status`, `version_number`, `version_started_at`, `version_ended_at`).

### Test coverage

| Test File                    | Test Function                              |
| ---------------------------- | ------------------------------------------ |
| tests/v1/test_api_studies.py | test_get_studies                           |
| tests/v1/test_api_studies.py | test_get_studies_pagination_sorting        |
| tests/v1/test_api_studies.py | test_get_studies_all                       |
| tests/v1/test_api_studies.py | test_get_studies_filtering                 |
| tests/v1/test_api_studies.py | test_get_studies_invalid_pagination_params |

# Study Structure

## FS-ConsumerApi-Studies-Activities-Get-010 [`URS-ConsumerApi-Studies-SoA`]

Consumers must be able to retrieve a paginated list of all study activities by calling the `GET /studies/{uid}/study-activities` endpoint.

### Request

It must be possible to filter items by `study_version_number`:

- If `study_version_number` query parameter is provided, study activities associated with the specified study version will be returned.
- Otherwise, study activities for the latest study version will be returned.

It must be possible to sort items by `uid` and `activity_name` fields.

### Response

Response must include basic information about each study activity, together with information about linked entities:

- library activity
- study SoA group
- study activity group
- study activity subgroup.

### Test coverage

| Test File                    | Test Function                                        |
| ---------------------------- | ---------------------------------------------------- |
| tests/v1/test_api_studies.py | test_get_study_activities                            |
| tests/v1/test_api_studies.py | test_get_study_activities_pagination_sorting         |
| tests/v1/test_api_studies.py | test_get_study_activities_all                        |
| tests/v1/test_api_studies.py | test_get_study_activities_all_specific_study_version |

## FS-ConsumerApi-Studies-ActivityInstances-Get-010 [`URS-ConsumerApi-Studies-SoA`]

Consumers must be able to retrieve a paginated list of all study activity instances by calling the `GET /studies/{uid}/study-activity-instances` endpoint.

### Request

It must be possible to filter items by `study_version_number`:

- If `study_version_number` query parameter is provided, study activity instances associated with the specified study version will be returned.
- Otherwise, study activity instances for the latest study version will be returned.

It must be possible to sort items by `uid`, `activity.name` and `activity_instance.name` fields.

### Response

Response must include basic information about each activity instance, together with information about linked entities:

- library activity
- library activity instance
- study SoA group
- study activity group
- study activity subgroup.

### Test coverage

| Test File                    | Test Function                                                |
| ---------------------------- | ------------------------------------------------------------ |
| tests/v1/test_api_studies.py | test_get_study_activity_instances                            |
| tests/v1/test_api_studies.py | test_get_study_activity_instances_pagination_sorting         |
| tests/v1/test_api_studies.py | test_get_study_activity_instances_all                        |
| tests/v1/test_api_studies.py | test_get_study_activity_instances_all_specific_study_version |

## FS-ConsumerApi-Studies-Visits-Get-010 [`URS-ConsumerApi-Studies-SoA`]

Consumers must be able to retrieve a paginated list of all study visits by calling the `GET /studies/{uid}/study-visits` endpoint.

### Request

It must be possible to filter items by `study_version_number`:

- If `study_version_number` query parameter is provided, study visits associated with the specified study version will be returned.
- Otherwise, study visits for the latest study version will be returned.

It must be possible to sort items by `uid`, `visit_name` and `unique_visit_number` fields.

### Response

Response must include basic information about each study visit.

### Test coverage

| Test File                    | Test Function                                    |
| ---------------------------- | ------------------------------------------------ |
| tests/v1/test_api_studies.py | test_get_study_visits                            |
| tests/v1/test_api_studies.py | test_get_study_visits_pagination_sorting         |
| tests/v1/test_api_studies.py | test_get_study_visits_all                        |
| tests/v1/test_api_studies.py | test_get_study_visits_all_specific_study_version |

## FS-ConsumerApi-Studies-SoaDetailed-Get-010 [`URS-ConsumerApi-Studies-SoA`]

Consumers must be able to retrieve a paginated list of detaild SoA items by calling the `GET /studies/{uid}/detailed-soa` endpoint.

### Request

It must be possible to filter items by `study_version_number`:

- If `study_version_number` query parameter is provided, study visits associated with the specified study version will be returned.
- Otherwise, study visits for the latest study version will be returned.

It must be possible to sort items by `visit_short_name`, `epoch_name`, `activity_name`, `activity_group_name`, `activity_subgroup_name`, `soa_group_name` fields.

### Response

Response must include basic information about study visits and activities included in the detailed SoA.

SoA items are sorted by the specified sort criteria and order.

### Test coverage

| Test File                    | Test Function                                          |
| ---------------------------- | ------------------------------------------------------ |
| tests/v1/test_api_studies.py | test_get_study_detailed_soa                            |
| tests/v1/test_api_studies.py | test_get_study_detailed_soa_pagination_sorting         |
| tests/v1/test_api_studies.py | test_get_study_detailed_soa_all                        |
| tests/v1/test_api_studies.py | test_get_study_detailed_soa_all_specific_study_version |

## FS-ConsumerApi-Studies-SoaOperational-Get-010 [`URS-ConsumerApi-Studies-SoA`]

Consumers must be able to retrieve a paginated list of operational SoA items by calling the `GET /studies/{uid}/operational-soa` endpoint.

### Request

It must be possible to filter items by `study_version_number`:

- If `study_version_number` query parameter is provided, study visits associated with the specified study version will be returned.
- Otherwise, study visits for the latest study version will be returned.

It must be possible to sort items by `activity_name`, `visit_uid`, `visit_short_name` fields.

### Response

Response must include basic information about study visits, activities and activity instances included in the operational SoA.

SoA items are sorted by the specified sort criteria and order.

### Test coverage

| Test File                    | Test Function                                             |
| ---------------------------- | --------------------------------------------------------- |
| tests/v1/test_api_studies.py | test_get_study_operational_soa                            |
| tests/v1/test_api_studies.py | test_get_study_operational_soa_pagination_sorting         |
| tests/v1/test_api_studies.py | test_get_study_operational_soa_all                        |
| tests/v1/test_api_studies.py | test_get_study_operational_soa_all_specific_study_version |


