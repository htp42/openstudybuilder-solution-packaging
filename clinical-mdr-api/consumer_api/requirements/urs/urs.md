# Overview

This document contains a set of user requirements related to StudyBuilder Consumer API.

# URS-ConsumerApi-Library-Activities

Consumers must be able to retrieve a list of all library activities and activity instances via the Consumer API.

# URS-ConsumerApi-Studies

Consumers must be able to retrieve a list of all studies that exist in StudyBuilder via the Consumer API.

# URS-ConsumerApi-Studies-SoA

Consumers must be able to retrieve the following entities related to Schedule of Activities via the Consumer API:

- Study Visits
- Study Activities
- Study Activity Instances
- Detailed SoA
- Operational SoA


# URS-ConsumerApi-Studies-Papillons

Consumers must be able to retrieve the following entities related to Schedule of Activities via the Consumer API, in a format suitable for SDTM generation:

- Detailed SoA
- Operational SoA

# URS-ConsumerApi-Studies-AuditTrail

Consumers must be able to retrieve audit trail information for studies via the Consumer API.

The audit trail must include information about actions performed on study entities, including:

- Timestamp of the action
- Study Id
- Action type (Create, Edit, Delete)
- Entity affected by the action
- Properties that were changed
- Anonymized information about the user who performed the action

The audit trail must protect user privacy by anonymizing user identifiers.


