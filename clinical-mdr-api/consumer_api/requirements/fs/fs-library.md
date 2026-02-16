# Overview

This document describes a set of GET endpoints in the OpenStudyBuilder Consumer API, which expose information about various entities defined in the `Library` section of OpenStudyBuilder.

Detailed API specification of each endpoint is found in the `consumer_api/openapi.json` file.

# Library Activities

## FS-ConsumerApi-Library-Activities-Get-010 [`URS-ConsumerApi-Library-Activities`]

Consumers must be able to retrieve a paginated list of all library activities by calling the `GET /library/activities` endpoint.

### Request

It must be possible to filter items by `library` and `status`.

It must be possible to sort items by `uid` and `name` fields.

### Response

Response must include basic information about each activity, together with linked activity group(s) and activity subgroup(s).

### Test coverage

| Test File                    | Test Function                                         |
| ---------------------------- | ----------------------------------------------------- |
| tests/v1/test_api_library.py | test_get_library_activities                           |
| tests/v1/test_api_library.py | test_get_library_activities_pagination_sorting        |
| tests/v1/test_api_library.py | test_get_library_activities_all                       |
| tests/v1/test_api_library.py | test_get_library_activities_filtering                 |
| tests/v1/test_api_library.py | test_get_library_activities_invalid_pagination_params |

## FS-ConsumerApi-Library-ActivityInstances-Get-010 [`URS-ConsumerApi-Library-Activities`]

Consumers must be able to retrieve a paginated list of all library activity instances by calling the `GET /library/activity-instances` endpoint.

### Request

It must be possible to filter items by `library`, `status` and `activity_uid`.

It must be possible to sort items by `uid` and `name` fields.

### Response

Response must include basic information about each activity instance, together with linked activity, activity group(s) and activity subgroup(s).

### Test coverage

| Test File                    | Test Function                                                 |
| ---------------------------- | ------------------------------------------------------------- |
| tests/v1/test_api_library.py | test_get_library_activity_instances                           |
| tests/v1/test_api_library.py | test_get_library_activity_instances_pagination_sorting        |
| tests/v1/test_api_library.py | test_get_library_activity_instances_all                       |
| tests/v1/test_api_library.py | test_get_library_activity_instances_filtering                 |
| tests/v1/test_api_library.py | test_get_library_activity_instances_invalid_pagination_params |


