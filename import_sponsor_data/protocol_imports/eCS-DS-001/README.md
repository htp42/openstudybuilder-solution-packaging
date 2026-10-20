# Protocol eCS-DS-001 → OpenStudyBuilder

Loads protocol eCS-DS-001 (Lumavant in PD-L1-positive advanced NSCLC, synthetic
demonstration protocol v0.2) into OSB with the existing importers. It follows the
route in section 4 of the *Export and re-import guide*. `build_dataset.py` writes
the files that `export/` would have produced, and the `mockdatajson` step loads
them through the API. Everything is matched by name on the target, and the import
is additive and cannot be undone.

## Run

Run everything from `import_sponsor_data/`. Set `API_BASE_URL`, and the
authentication variables if OAuth is enabled, in `import.env` first.

```bash
uv sync
uv run python protocol_imports/eCS-DS-001/build_dataset.py      # --study-number to change 001
../db/export_db_backup.sh <container> <database>                # back up the target
uv run python protocol_imports/eCS-DS-001/fixups.py prepare     # add --dry-run to only read
uv run python protocol_imports/eCS-DS-001/preflight.py          # read-only; must report MISSING: 0, PREPARE: 0
uv run --env-file protocol_imports/eCS-DS-001/import.env python -m importers.run_import_compounds
uv run --env-file protocol_imports/eCS-DS-001/import.env python -m importers.run_import_mockdatajson
uv run python protocol_imports/eCS-DS-001/fixups.py finish
```

- `fixups.py prepare` creates the library content the dataset relies on: the
  `years` unit (or repairs it, e.g. one created in the UI without the
  template-parameter flag) and the Objective / Endpoint Category terms.
- The compounds step creates the Lumavant medicinal product that the study
  compound needs (`mockdatajson` cannot create it).
- `fixups.py finish` sets what the importer drops on API 3.0.x (below), marks every
  study criterion as a key criterion, attaches the SoA footnotes and sets the
  template categories. It then verifies the study (`fixups.py verify` on its own):
  every item in `exported/` must be on the study and every endpoint linked to an
  objective, since the importer only logs the items the API rejects.

Both `fixups.py` steps read first and change only what differs, so they can be
re-run.

`sh protocol_imports/import_protocols.sh eCS-DS-001` runs the same steps after
the backup, in order, and stops at the first one that fails.

## Extended database image

The `extended` variant of the database image includes this study. For that
variant, the build-and-push workflow sets the `PROTOCOL_IMPORTS` build arg to
`eCS-DS-001`. `db/Dockerfile` then runs `import_protocols.sh` against the API it
starts during the build, after the sponsor data. The build fails if the preflight
finds a missing name or the verification finds the study incomplete. The standard
image leaves `PROTOCOL_IMPORTS` empty and does not include it.

To build it locally, from the repository root:

```bash
CDISC_CT_DIR_NAME=cdisc_ct_extended PROTOCOL_IMPORTS=eCS-DS-001 docker compose build database
```

`db/` has no `.dockerignore`, so build from a clean checkout: local `.venv`
folders would otherwise be copied over the image's own.

In the import log, `Could not find …` or `Unable to find …` means a name is missing
on the target. Fix the cause, restore the backup and run again. Do not re-run
against a target that already has the study: study activities, schedules and
design cells are not de-duplicated.

## What is loaded

| Area | Content |
|---|---|
| Programme / project | Lighthouse Program / `ECS-DS` (Lumavant NSCLC) → study ID `ECS-DS-001`. OSB uppercases project numbers, so the protocol's lower-case "e" cannot be kept. |
| Study metadata | Title, interventional, Phase 2, open label, parallel, randomised, stratification factor, drug study, intent Treatment, both sexes, minimum age 18 years, no maximum age, adults only, patients |
| Population terms | SNOMED Non-small cell lung cancer, Malignant tumor of lung, Malignant neoplastic disease (added to the dictionary if missing) |
| Design | 3 epochs, 2 arms (Lumavant regimen A / B, investigational), 4 elements, design matrix |
| Visits | Screening, Cycle 1–9 Day 1 (21-day cycles), end of treatment, 30-day safety follow-up, survival follow-up |
| SoA | 66 study activities, 490 scheduled cells, from protocol section 7 |
| Library activities | 23 created in the Sponsor library (ECOG, physical examination, 12-lead ECG, ECHO/MUGA, pregnancy test, RECIST lesions and response, PK/PD samples, Lumavant administration, QoL, survival status, …), plus 12 groups and 16 subgroups. Existing baseline activities are reused (consent, demography, vital signs, labs, AE, randomisation, …). |
| Objectives / endpoints | 7 objectives (1 primary, 5 secondary, 1 exploratory), 21 endpoints with level and category |
| Criteria | 10 inclusion, 9 exclusion, all key criteria |
| Compound | Lumavant: active substance, pharmaceutical product (intravenous), compound and alias, medicinal product, study compound (investigational product) |

## Syntax templates

Where the protocol text has a variable part (the compound, the disease, an
activity, a number), it becomes a reusable **Sponsor** template with parameters,
filled in for this study. Text that is a fixed definition (PFS, ORR, the
data-reconciliation endpoints, most exclusions) stays study-specific
**User Defined** free text. The values are matched by name against
`/template-parameters/{type}/terms`.

| Template | Values |
|---|---|
| To assess antitumor activity of [Compound] by delaying progression or death | Lumavant |
| To assess tumor response and clinical benefit of [Compound] | Lumavant |
| To characterize the safety and tolerability of [Compound] | Lumavant |
| To characterize [Compound] exposure | Lumavant |
| To evaluate immune and biomarker activity of [Compound] | Lumavant |
| To evaluate health status and symptoms in participants with [DiseaseDisorder] | Non-small cell lung cancer |
| Number of participants with at least one treatment-emergent [Activity] | Adverse Event |
| Number of participants with at least one serious [Activity] | Adverse Event |
| Number of participants with at least one [Activity] of special interest, including immune-mediated events | Adverse Event |
| Number of participants with laboratory abnormalities in [ActivitySubGroup] | Haematology, Biochemistry, Coagulation Parameters and Urinalysis |
| Number of participants with dose modifications of [Compound] | Lumavant |
| Concentration-time profiles of [Compound] using protocol-defined pre-dose and post-dose timepoints | Lumavant |
| Blood-based pharmacodynamic markers measured in [Activity] | PD Blood Sample |
| Responses to [Activity] | Quality of Life Questionnaire |
| Age [NumericValue] [Age Unit] or above at the time of signing the informed consent. | 18, years (existing OSB Sponsor template, reused) |
| Histologically or cytologically confirmed advanced, unresectable, recurrent, or metastatic [DiseaseDisorder]. | Non-small cell lung cancer |
| At least [NumericValue] measurable lesion by RECIST v1.1. | 1 |
| ECOG performance status of [NumericValue] or [NumericValue] at screening, with ECOG [NumericValue] permitted only by sponsor waiver if clinically justified. | 0, 1, 2 |
| For participants of childbearing potential, negative [Activity] and agreement to use protocol-defined contraception. | Pregnancy Test |
| Prior severe hypersensitivity to checkpoint inhibitor therapy or any component of [Compound]. | Lumavant |

## SoA footnotes

The footnote templates (type *SoA Footnote*) are created by the import, with the
other templates. The importer cannot create study footnotes, so `fixups.py finish`
creates one per template and attaches it to its SoA rows, columns or epoch. A
footnote already on the study is skipped. The definitions are `FOOTNOTES` in
`build_dataset.py`: generic wording goes to the Sponsor library, protocol-specific
wording to User Defined.

| Footnote | Attached to |
|---|---|
| Update as needed during treatment. | Medical history, disease history, prior therapy and radiotherapy rows |
| Disease stage at study entry is the stratification factor: recorded in EDC Disease History, assigned independently in IRT at enrollment/randomization, and reconciled between the two sources. | Disease history and randomisation rows |
| Every [6] weeks for the first [24] weeks, then every [9] weeks. | RECIST 1.1 subgroup |
| Also at end of treatment as clinically indicated, and progression status during survival follow-up. | RECIST 1.1 subgroup |
| Images are also submitted for blinded independent central review. Central-reader results are reconciled against site-entered RECIST data (TL, NTL, TA, NL, RA). | Tumour imaging row |
| Also at selected treatment cycles. | QoL questionnaire row |
| Symptom-directed or per cycle. | Physical examination row |
| At the 30-day safety follow-up, as clinically indicated. | Haematology, biochemistry, coagulation and urinalysis subgroups |
| During treatment cycles, per local requirements. | Pregnancy test row |
| During treatment cycles, as clinically indicated. | 12-lead ECG row |
| When clinically indicated or required for cardiac assessment. | ECHO/MUGA row |
| Collected from informed consent. During survival follow-up, only serious adverse events related to study drug. | Adverse event row |
| Serious adverse events are reconciled against the external Safety system (e.g. Argus). | Adverse event row |
| During survival follow-up, as related. | Concomitant medication and procedure rows |
| At protocol-defined pre-dose and post-dose timepoints in Cycle 1, then at selected cycles and timepoints. | PK and PD sample rows |
| One visit per [21]-day cycle. Cycles continue beyond Cycle [9] until treatment discontinuation. | Treatment epoch |
| Occurs at treatment discontinuation; the timing shown is nominal. | End-of-treatment visit |
| Periodic contact; the timing shown is nominal. | Survival follow-up visit |

To add footnotes to a study imported before they existed, run the template step
only, then `finish`. The template step skips templates that already exist and
does not touch the study.

```bash
uv run --env-file protocol_imports/eCS-DS-001/import.env python -m importers.run_import_mockdatajson --limit Templates
uv run python protocol_imports/eCS-DS-001/fixups.py finish
```

## Endpoint links

Endpoints are linked to their objective by the objective's rendered text, which OSB
builds from the values' sentence-case names. `build_dataset.py` renders it the same
way, and the preflight simulation checks that every endpoint finds its objective.

## Assumptions (not stated in the protocol)

- Visit timing: Screening is set at Day -28. Cycles are modelled to Cycle 9, which
  covers the 24-week window of 6-weekly imaging. End of treatment is set at Day 189,
  and survival follow-up at end of treatment + 90 days. All of these are nominal
  and say so in the visit description. Visit windows are 0.
- The labs use the baseline library's Haematology, Biochemistry, Coagulation and
  Urinalysis panels as they are, because the protocol does not list analytes.
- "Selected cycles" or "as indicated" cells are not scheduled. That covers PK/PD
  after Cycle 1, QoL beyond Cycle 1, and ECHO/MUGA, which is on the SoA but has
  no scheduled visits.
- Randomisation is placed at Cycle 1 Day 1.
- Patient-reported outcomes are an exploratory objective, because the synopsis
  does not list them as secondary.

## Set by fixups.py finish rather than the importer

On API 3.0.x the importer sends some study fields under names the API has since
renamed (`trial_types_codes`, `disease_conditions_or_indications_codes`,
`diagnosis_groups_codes`), and its patch template has no expected participants or
short title. The study PATCH ignores these without error. `fixups.py finish` sets
them under the current names. It also resends the minimum age with its unit, since
a population patch is merged with the current values, which read the age back
without its unit.

## Not loaded

- The three data-reconciliation rows of the SoA (IRT stage, central imaging reader,
  SAE vs safety system) are not activities. They are covered by the data-integrity
  objective and by footnotes on the related rows.
- Dose, dosage form and dosing frequency, which the protocol does not specify.
