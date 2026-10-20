"""Build OpenStudyBuilder import files for protocol eCS-DS-001.

Protocol: "A Phase II, Multicenter, Open-label Study of Lumavant in Participants
with PD-L1-positive Advanced Non-small Cell Lung Cancer Who Have Progressed on
Standard Therapy" (synthetic demonstration protocol, v0.2, 06-Jul-2026).

The files reproduce the layout written by the export/ component, so they can be
loaded with the existing importers (see README.md next to this script):

* exported/  -> input for `importers.run_import_mockdatajson`
* compounds/ -> input for `importers.run_import_compounds`

Every name in here is matched by name on the target, so it must be spelled
exactly as the target library spells it. Run preflight.py before importing.

Usage:
    python build_dataset.py [--study-number 001]
"""

import argparse
import json
import re
import shutil
from pathlib import Path
from typing import NamedTuple

HERE = Path(__file__).resolve().parent
EXPORT_DIR = HERE / "exported"
COMPOUNDS_DIR = HERE / "compounds"

# Exported uid. Only used to name files and link them together; the target
# assigns its own uids.
STUDY_UID = "Study_ECSDS001"

PROGRAMME = "Lighthouse Program"
# The API uppercases project numbers on create but matches them as given when
# a study is created, so the study ID becomes ECS-DS-001.
PROJECT_NUMBER = "ECS-DS"
PROJECT_NAME = "Lumavant NSCLC"
PROJECT_DESCRIPTION = (
    "Lumavant, a novel immune checkpoint inhibitor, in PD-L1-positive advanced "
    "non-small cell lung cancer"
)

STUDY_TITLE = (
    "A Phase II, Multicenter, Open-label Study of Lumavant in Participants with "
    "PD-L1-positive Advanced Non-small Cell Lung Cancer Who Have Progressed on "
    "Standard Therapy"
)
# Not carried by the mockdatajson study patch, kept for completeness.
STUDY_SHORT_TITLE = (
    "A Phase II, multicenter, open-label study evaluating the safety and efficacy "
    "of Lumavant in participants with PD-L1-positive advanced NSCLC who have "
    "progressed after standard therapy."
)

USER_DEFINED = "User Defined"
SPONSOR = "Sponsor"

EXPECTED_SUBJECTS = 50
MINIMUM_AGE = (18, "year")
# Set by fixups.py after the import: the importer sends trial types under a
# field name the API no longer uses.
TRIAL_TYPES = [
    "Efficacy Study",
    "Safety Study",
    "Tolerability Study",
    "Pharmacokinetic Study",
    "Pharmacodynamic Study",
    "Multi-centre",
]

# --------------------------------------------------------------------------
# Population: SNOMED terms. Created in the SNOMED dictionary when missing.
# --------------------------------------------------------------------------
SNOMED_TERMS = [
    # dictionary_id, name, definition
    (
        "254637007",
        "Non-small cell lung cancer",
        "Non-small cell lung cancer (disorder)",
    ),
    ("363358000", "Malignant tumor of lung", "Malignant tumor of lung (disorder)"),
    (
        "363346000",
        "Malignant neoplastic disease",
        "Malignant neoplastic disease (disorder)",
    ),
]
THERAPEUTIC_AREA = "Malignant neoplastic disease"
DIAGNOSIS_GROUP = "Malignant tumor of lung"
INDICATION = "Non-small cell lung cancer"

# --------------------------------------------------------------------------
# Epochs. Names are what the API generates from the subtype: one epoch per
# subtype keeps them un-numbered, so visits can find them by name.
# --------------------------------------------------------------------------
# Codelist spellings on the target. They vary between CT versions: the repo's
# baseline CSVs say "Follow-up" and "Primary Endpoint", recent CDISC CT says
# "Follow-Up" and "Primary Outcome Measure". preflight.py flags a mismatch.
FOLLOW_UP_EPOCH = "Follow-Up"
PRIMARY_ENDPOINT = "Primary Outcome Measure"
SECONDARY_ENDPOINT = "Secondary Outcome Measure"
EXPLORATORY_ENDPOINT = "Exploratory Outcome Measure"

EPOCHS = [
    {
        "subtype": "Screening",
        "description": "Screening: informed consent, eligibility and baseline assessments",
        "start_rule": "Informed consent signed",
        "end_rule": "Eligibility confirmed and participant enrolled/randomized in IRT",
        "color_hash": "#CFD8DCFF",
    },
    {
        "subtype": "Treatment",
        "description": "Lumavant treatment in 21-day cycles, up to and including end of treatment",
        "start_rule": "First dose of Lumavant (Cycle 1 Day 1)",
        "end_rule": (
            "Treatment discontinuation: disease progression, unacceptable toxicity, "
            "withdrawal of consent, death, investigator decision, pregnancy, "
            "protocol-defined discontinuation or study termination"
        ),
        "color_hash": "#90CAF9FF",
    },
    {
        "subtype": FOLLOW_UP_EPOCH,
        "description": "30-day safety follow-up and long-term survival follow-up",
        "start_rule": "End of treatment",
        "end_rule": "Death, withdrawal of consent or end of study",
        "color_hash": "#A5D6A7FF",
    },
]

# --------------------------------------------------------------------------
# Visits, in chronological order. Day 0 = Cycle 1 Day 1 (global anchor).
# Non-manual visits are named "Visit N" by the API in this order, and the
# activity schedule finds visits by that name.
# --------------------------------------------------------------------------
CYCLE_DAYS = 21
LAST_MODELLED_CYCLE = 9  # covers the q6w imaging window (24 weeks)


def _visit(
    key, description, epoch, visit_type, time_ref, day, contact="On Site Visit", **extra
):
    return {
        "key": key,
        "description": description,
        "epoch": epoch,
        "visit_type": visit_type,
        "time_reference": time_ref,
        "time_value": day,
        "contact_mode": contact,
        "is_global_anchor_visit": extra.get("anchor", False),
        "is_soa_milestone": extra.get("milestone", False),
    }


VISITS = [
    _visit(
        "SCR",
        "Screening (nominal Day -28)",
        "Screening",
        "Screening",
        "Global anchor visit",
        -28,
    ),
    _visit(
        "C1",
        "Cycle 1 Day 1",
        "Treatment",
        "Start of treatment",
        "Global anchor visit",
        0,
        anchor=True,
        milestone=True,
    ),
]
for _cycle in range(2, LAST_MODELLED_CYCLE + 1):
    VISITS.append(
        _visit(
            f"C{_cycle}",
            f"Cycle {_cycle} Day 1",
            "Treatment",
            "Treatment",
            "Global anchor visit",
            CYCLE_DAYS * (_cycle - 1),
        )
    )
VISITS += [
    _visit(
        "EOT",
        "End of treatment (nominal timing; occurs at treatment discontinuation)",
        "Treatment",
        "End of treatment",
        "Global anchor visit",
        CYCLE_DAYS * LAST_MODELLED_CYCLE,
        milestone=True,
    ),
    _visit(
        "SFU",
        "30-day safety follow-up (approximately 30 days after last dose)",
        FOLLOW_UP_EPOCH,
        "Follow-up",
        "End of treatment",
        30,
    ),
    _visit(
        "SURV",
        "Survival follow-up contact (nominal timing; periodic)",
        FOLLOW_UP_EPOCH,
        "Follow-up",
        "End of treatment",
        90,
        contact="Phone Contact",
    ),
]

CYCLES = [f"C{n}" for n in range(1, LAST_MODELLED_CYCLE + 1)]
# Tumour imaging every 6 weeks for 24 weeks = every 2nd 21-day cycle.
IMAGING = [f"C{n}" for n in range(3, LAST_MODELLED_CYCLE + 1, 2)]
SCR_CYCLES_EOT = ["SCR", *CYCLES, "EOT"]
SCR_TO_SFU = [*SCR_CYCLES_EOT, "SFU"]

# --------------------------------------------------------------------------
# Arms, elements, design matrix
# --------------------------------------------------------------------------
ARMS = [
    {
        "name": "Lumavant Regimen A",
        "short_name": "Regimen A",
        "code": "A",
        "randomization_group": "A",
        "description": "Lumavant regimen A (DRUG_1 in the EDC)",
        "arm_colour": "#90CAF9FF",
        "arm_type": "Investigational Arm",
    },
    {
        "name": "Lumavant Regimen B",
        "short_name": "Regimen B",
        "code": "B",
        "randomization_group": "B",
        "description": "Lumavant regimen B or alternate dose/schedule cohort (DRUG_2 in the EDC)",
        "arm_colour": "#CE93D8FF",
        "arm_type": "Investigational Arm",
    },
]

ELEMENTS = [
    {
        "name": "Screening",
        "short_name": "Screening",
        "subtype": "Screening",
        "start_rule": "Informed consent signed",
        "end_rule": "Enrolment/randomization",
        "element_colour": "#CFD8DCFF",
    },
    {
        "name": "Lumavant Regimen A",
        "short_name": "Regimen A",
        "subtype": "Treatment",
        "start_rule": "First dose of Lumavant regimen A",
        "end_rule": "Treatment discontinuation",
        "element_colour": "#90CAF9FF",
    },
    {
        "name": "Lumavant Regimen B",
        "short_name": "Regimen B",
        "subtype": "Treatment",
        "start_rule": "First dose of Lumavant regimen B",
        "end_rule": "Treatment discontinuation",
        "element_colour": "#CE93D8FF",
    },
    {
        "name": "Follow-up",
        "short_name": "Follow-up",
        "subtype": "Follow-up",
        "start_rule": "End of treatment",
        "end_rule": "Death, withdrawal of consent or end of study",
        "element_colour": "#A5D6A7FF",
    },
]

# arm -> {epoch: element}
DESIGN_MATRIX = {
    "Lumavant Regimen A": {
        "Screening": "Screening",
        "Treatment": "Lumavant Regimen A",
        FOLLOW_UP_EPOCH: "Follow-up",
    },
    "Lumavant Regimen B": {
        "Screening": "Screening",
        "Treatment": "Lumavant Regimen B",
        FOLLOW_UP_EPOCH: "Follow-up",
    },
}

# --------------------------------------------------------------------------
# Activities and Schedule of Activities (protocol section 7)
# --------------------------------------------------------------------------
# New activity groups / subgroups (existing ones are skipped by the importer).
NEW_ACTIVITY_GROUPS = [
    ("Disease Characteristics", "disease characteristics"),
    ("Prior and Subsequent Cancer Therapy", "prior and subsequent cancer therapy"),
    ("Substance Use", "substance use"),
    ("Performance Status", "performance status"),
    ("Physical Examination", "physical examination"),
    ("ECG", "ECG"),
    ("Cardiac Function", "cardiac function"),
    ("Tumour Assessment", "tumour assessment"),
    ("Pharmacokinetics", "pharmacokinetics"),
    ("Pharmacodynamics", "pharmacodynamics"),
    (
        "Concomitant Medications and Procedures",
        "concomitant medications and procedures",
    ),
    ("Survival Follow-up", "survival follow-up"),
]
NEW_ACTIVITY_SUBGROUPS = [
    ("Disease History", "disease history"),
    ("Prior Cancer Therapy", "prior cancer therapy"),
    ("Subsequent Anticancer Therapy", "subsequent anticancer therapy"),
    ("Smoking History", "smoking history"),
    ("ECOG Performance Status", "ECOG performance status"),
    ("Physical Examination", "physical examination"),
    ("12-Lead ECG", "12-lead ECG"),
    ("ECHO/MUGA", "ECHO/MUGA"),
    ("Pregnancy Test", "pregnancy test"),
    ("RECIST 1.1", "RECIST 1.1"),
    ("PK Sampling", "PK sampling"),
    ("PD Sampling", "PD sampling"),
    ("Concomitant Medication", "concomitant medication"),
    ("Concomitant Procedure", "concomitant procedure"),
    ("Quality of Life", "quality of life"),
    ("Survival Status", "survival status"),
]

# Library activities to create when missing: name -> (sentence case, definition)
NEW_ACTIVITIES = {
    "Disease History": (
        "disease history",
        "Baseline disease characterization including disease stage at study entry "
        "(protocol stratification factor: Stage IIIB/IIIC vs Stage IV)",
    ),
    "Prior Systemic Anticancer Therapy": ("prior systemic anticancer therapy", None),
    "Prior Radiotherapy": ("prior radiotherapy", None),
    "Subsequent Anticancer Therapy": ("subsequent anticancer therapy", None),
    "Smoking History": ("smoking history", None),
    "ECOG Performance Status": ("ECOG performance status", None),
    "Physical Examination": ("physical examination", None),
    "12-Lead ECG": (
        "12-lead ECG",
        "Date/time, heart rate, PR, QRS, QT, QTc, correction formula and interpretation",
    ),
    "ECHO/MUGA": (
        "ECHO/MUGA",
        "Left ventricular ejection fraction by echocardiogram or MUGA scan, when "
        "clinically indicated or required",
    ),
    "Pregnancy Test": ("pregnancy test", "For participants of childbearing potential"),
    "Tumour Imaging": (
        "tumour imaging",
        "CT or MRI of disease sites, using the same modality when feasible; images "
        "are also submitted for blinded independent central review",
    ),
    "Target Lesions": ("target lesions", "RECIST v1.1 target lesions (EDC domain TL)"),
    "Non-target Lesions": (
        "non-target lesions",
        "RECIST v1.1 non-target lesions (EDC domain NTL)",
    ),
    "New Lesions": ("new lesions", "RECIST v1.1 new lesions (EDC domain NL)"),
    "Overall Tumour Response": (
        "overall tumour response",
        "RECIST v1.1 overall response (EDC domains TA and RA)",
    ),
    "Lumavant PK Blood Sample": ("Lumavant PK blood sample", None),
    "PD Blood Sample": ("PD blood sample", "Blood-based pharmacodynamic markers"),
    "Lumavant Administration": (
        "Lumavant administration",
        "Intravenous infusion of Lumavant, regimen A or B",
    ),
    "Study Drug Dispensation": (
        "study drug dispensation",
        "Kit dispensation and redispensation",
    ),
    "Concomitant Medication": ("concomitant medication", None),
    "Concomitant Procedure": ("concomitant procedure", None),
    "Quality of Life Questionnaire": (
        "quality of life questionnaire",
        "Instrument to be configured per final CRF library (QS domain)",
    ),
    "Survival Status": (
        "survival status",
        "Survival status, disease progression, subsequent anticancer therapy and "
        "date/cause of death where applicable",
    ),
}

# Study activities, in SoA order: (activity, group, subgroup, SoA group, visits)
_DEMOGRAPHY = ["Date of Birth", "Sex", "Race", "Ethnicity"]
_VITAL_SIGNS = [
    "Systolic Blood Pressure",
    "Diastolic Blood Pressure",
    "Pulse Rate",
    "Respiratory Rate",
    "Temperature",
]
_HAEMATOLOGY = ["Erythrocytes", "Leukocytes", "Platelets", "Eosinophils"]
_BIOCHEMISTRY = [
    "Alanine Aminotransferase",
    "Aspartate Aminotransferase",
    "Alkaline Phosphatase",
    "Bilirubin",
    "Gamma Glutamyl Transferase",
    "Albumin",
    "Protein",
    "Creatinine",
    "Glomerular Filtration Rate, Estimated",
    "Sodium",
    "Potassium",
    "Amylase",
    "Lipase",
    "C Reactive Protein",
]
_COAGULATION = ["Prothrombin Time", "Prothrombin Intl. Normalized Ratio"]
_URINALYSIS = [
    "pH",
    "Protein",
    "Glucose",
    "Erythrocytes",
    "Leukocytes",
    "Nitrite",
    "Bilirubin",
    "Urobilinogen",
]

STUDY_ACTIVITIES = [
    (
        "Informed Consent Obtained",
        "Informed Consent",
        "Informed Consent",
        "INFORMED CONSENT",
        ["SCR"],
    ),
    (
        "Eligibility Criteria Met",
        "Eligibility Criteria",
        "Eligibility Criteria",
        "ELIGIBILITY AND OTHER CRITERIA",
        ["SCR"],
    ),
    *[
        (a, "Demography", "Demography", "SUBJECT RELATED INFORMATION", ["SCR"])
        for a in _DEMOGRAPHY
    ],
    (
        "Medical History/Concomitant Illness",
        "Medical History/Concomitant Illness",
        "Medical History/Concomitant Illness",
        "SUBJECT RELATED INFORMATION",
        ["SCR"],
    ),
    (
        "Disease History",
        "Disease Characteristics",
        "Disease History",
        "SUBJECT RELATED INFORMATION",
        ["SCR"],
    ),
    (
        "Prior Systemic Anticancer Therapy",
        "Prior and Subsequent Cancer Therapy",
        "Prior Cancer Therapy",
        "SUBJECT RELATED INFORMATION",
        ["SCR"],
    ),
    (
        "Prior Radiotherapy",
        "Prior and Subsequent Cancer Therapy",
        "Prior Cancer Therapy",
        "SUBJECT RELATED INFORMATION",
        ["SCR"],
    ),
    (
        "Smoking History",
        "Substance Use",
        "Smoking History",
        "SUBJECT RELATED INFORMATION",
        ["SCR"],
    ),
    (
        "Randomized",
        "Randomisation",
        "Randomisation",
        "SUBJECT RELATED INFORMATION",
        ["C1"],
    ),
    (
        "Tumour Imaging",
        "Tumour Assessment",
        "RECIST 1.1",
        "EFFICACY",
        ["SCR", *IMAGING],
    ),
    (
        "Target Lesions",
        "Tumour Assessment",
        "RECIST 1.1",
        "EFFICACY",
        ["SCR", *IMAGING],
    ),
    (
        "Non-target Lesions",
        "Tumour Assessment",
        "RECIST 1.1",
        "EFFICACY",
        ["SCR", *IMAGING],
    ),
    ("New Lesions", "Tumour Assessment", "RECIST 1.1", "EFFICACY", IMAGING),
    ("Overall Tumour Response", "Tumour Assessment", "RECIST 1.1", "EFFICACY", IMAGING),
    (
        "Quality of Life Questionnaire",
        "Clinical Outcome Assessments",
        "Quality of Life",
        "EFFICACY",
        ["SCR", "C1", "EOT"],
    ),
    ("Survival Status", "Survival Follow-up", "Survival Status", "EFFICACY", ["SURV"]),
    (
        "ECOG Performance Status",
        "Performance Status",
        "ECOG Performance Status",
        "SAFETY",
        SCR_CYCLES_EOT,
    ),
    (
        "Physical Examination",
        "Physical Examination",
        "Physical Examination",
        "SAFETY",
        SCR_CYCLES_EOT,
    ),
    *[
        (a, "Vital Signs", "Vital Signs", "SAFETY", SCR_CYCLES_EOT)
        for a in _VITAL_SIGNS
    ],
    *[
        (a, "Laboratory Assessments", "Haematology", "SAFETY", SCR_CYCLES_EOT)
        for a in _HAEMATOLOGY
    ],
    *[
        (a, "Laboratory Assessments", "Biochemistry", "SAFETY", SCR_CYCLES_EOT)
        for a in _BIOCHEMISTRY
    ],
    *[
        (
            a,
            "Laboratory Assessments",
            "Coagulation Parameters",
            "SAFETY",
            SCR_CYCLES_EOT,
        )
        for a in _COAGULATION
    ],
    *[
        (a, "Laboratory Assessments", "Urinalysis", "SAFETY", SCR_CYCLES_EOT)
        for a in _URINALYSIS
    ],
    (
        "Pregnancy Test",
        "Laboratory Assessments",
        "Pregnancy Test",
        "SAFETY",
        ["SCR", "C1", "EOT"],
    ),
    ("12-Lead ECG", "ECG", "12-Lead ECG", "SAFETY", ["SCR", "C1", "EOT"]),
    ("ECHO/MUGA", "Cardiac Function", "ECHO/MUGA", "SAFETY", []),  # as indicated only
    ("Adverse Event", "Adverse Event", "Adverse Event", "SAFETY", SCR_TO_SFU),
    (
        "Concomitant Medication",
        "Concomitant Medications and Procedures",
        "Concomitant Medication",
        "SAFETY",
        SCR_TO_SFU,
    ),
    (
        "Concomitant Procedure",
        "Concomitant Medications and Procedures",
        "Concomitant Procedure",
        "SAFETY",
        SCR_TO_SFU,
    ),
    (
        "Subsequent Anticancer Therapy",
        "Prior and Subsequent Cancer Therapy",
        "Subsequent Anticancer Therapy",
        "SAFETY",
        ["EOT", "SFU", "SURV"],
    ),
    (
        "Lumavant PK Blood Sample",
        "Pharmacokinetics",
        "PK Sampling",
        "PHARMACOKINETICS",
        ["C1"],
    ),
    ("PD Blood Sample", "Pharmacodynamics", "PD Sampling", "PHARMACODYNAMICS", ["C1"]),
    (
        "Lumavant Administration",
        "Administration of IMP",
        "Administration of IMP",
        "TRIAL MATERIAL",
        CYCLES,
    ),
    (
        "Study Drug Dispensation",
        "Administration of IMP",
        "Administration of IMP",
        "TRIAL MATERIAL",
        CYCLES,
    ),
    (
        "Last Date on Trial Product",
        "End of IMP Treatment",
        "End of IMP Treatment",
        "SUBJECT RELATED INFORMATION",
        ["EOT"],
    ),
]


# --------------------------------------------------------------------------
# Syntax template parameter values. Each is matched by name against
# /template-parameters/{type}/terms on the target. OSB writes the value's
# sentence-case name into the instance text, and endpoints find their
# objective by that text, so the sentence case has to match the target.
# --------------------------------------------------------------------------
class Value(NamedTuple):
    type: str
    name: str
    sentence_case: str


def number(value):
    return Value("NumericValue", str(value), str(value))


LUMAVANT = Value("Compound", "Lumavant", "Lumavant")
NSCLC = Value(
    "DiseaseDisorder", "Non-small cell lung cancer", "non-small cell lung cancer"
)
ADVERSE_EVENT = Value("Activity", "Adverse Event", "adverse event")
PREGNANCY_TEST = Value("Activity", "Pregnancy Test", "pregnancy test")
PD_BLOOD_SAMPLE = Value("Activity", "PD Blood Sample", "PD blood sample")
QOL_QUESTIONNAIRE = Value(
    "Activity", "Quality of Life Questionnaire", "quality of life questionnaire"
)
LAB_PANELS = [
    Value("ActivitySubGroup", name, name.lower())
    for name in ("Haematology", "Biochemistry", "Coagulation Parameters", "Urinalysis")
]
# Units fixups.py prepare creates when missing, as a copy of an existing one:
# OSB shows a duration above 1 only with a plural unit in the Study Time
# subset, and the age criterion below needs "years" as an Age Unit.
UNITS_TO_CREATE = {"years": "year"}
YEARS = Value("Age Unit", "years", "years")


class Syntax(NamedTuple):
    """Template text with [Parameter] placeholders, and one list of values per
    placeholder, in order. Several values in one placeholder are joined with
    the conjunction. Text with placeholders becomes a reusable Sponsor
    template; text without stays study-specific User Defined free text."""

    text: str
    values: tuple = ()
    conjunction: str = "and"
    forced_library: str | None = None

    @property
    def placeholders(self):
        return re.findall(r"\[([^\]]+)\]", self.text)

    @property
    def library(self):
        if self.forced_library:
            return self.forced_library
        return SPONSOR if self.values else USER_DEFINED

    def rendered(self):
        """The instance text as OSB generates it from the template."""
        return render(self.text, self.values, [self.conjunction] * len(self.values))


def render(text, values, conjunctions):
    """Fill [Parameter] placeholders the way OSB names an instance: the values'
    sentence-case names, comma-separated, with the conjunction before the last."""
    for placeholder, group, conjunction in zip(
        re.findall(r"\[([^\]]+)\]", text), values, conjunctions
    ):
        names = [value.sentence_case for value in group]
        joined = names[0]
        if len(names) > 1:
            joined = ", ".join(names[:-1]) + f" {conjunction} " + names[-1]
        text = text.replace(f"[{placeholder}]", f"[{joined}]", 1)
    return text


def syntax(text, *values, conjunction="and", library=None):
    """library=SPONSOR marks generic text without parameters as reusable."""
    item = Syntax(
        text,
        tuple(v if isinstance(v, list) else [v] for v in values),
        conjunction,
        library,
    )
    types = [values[0].type for values in item.values]
    assert (
        item.placeholders == types
    ), f"placeholders {item.placeholders} != {types}: {text}"
    # OSB capitalises an instance that starts with a parameter; avoid it so
    # rendered() stays exact.
    assert not text.startswith("["), text
    return item


# --------------------------------------------------------------------------
# Objectives and endpoints (protocol sections 1 and 3)
# --------------------------------------------------------------------------
OBJECTIVES = [
    {
        "text": syntax(
            "To assess antitumor activity of [Compound] by delaying progression or death",
            LUMAVANT,
        ),
        "level": "Primary Objective",
        "category": "Efficacy",
        "endpoints": [
            (
                syntax(
                    "Progression-free survival (PFS), defined as time from first exposure or "
                    "randomization/enrollment to first documented disease progression by "
                    "RECIST v1.1 or death from any cause"
                ),
                PRIMARY_ENDPOINT,
                "Efficacy",
            ),
        ],
    },
    {
        "text": syntax(
            "To assess tumor response and clinical benefit of [Compound]", LUMAVANT
        ),
        "level": "Secondary Objective",
        "category": "Efficacy",
        "endpoints": [
            (
                syntax("Objective response rate (ORR) by RECIST v1.1"),
                SECONDARY_ENDPOINT,
                "Efficacy",
            ),
            (syntax("Duration of response (DOR)"), SECONDARY_ENDPOINT, "Efficacy"),
            (syntax("Disease control rate (DCR)"), SECONDARY_ENDPOINT, "Efficacy"),
            (syntax("Best overall response"), SECONDARY_ENDPOINT, "Efficacy"),
            (syntax("Time to response"), SECONDARY_ENDPOINT, "Efficacy"),
            (
                syntax(
                    "Overall survival (OS), defined as time from first dose or "
                    "randomization/enrollment to death from any cause"
                ),
                SECONDARY_ENDPOINT,
                "Efficacy",
            ),
        ],
    },
    {
        "text": syntax(
            "To characterize the safety and tolerability of [Compound]", LUMAVANT
        ),
        "level": "Secondary Objective",
        "category": "Safety",
        "endpoints": [
            (
                syntax(
                    "Number of participants with at least one treatment-emergent [Activity]",
                    ADVERSE_EVENT,
                ),
                SECONDARY_ENDPOINT,
                "Safety",
            ),
            (
                syntax(
                    "Number of participants with at least one serious [Activity]",
                    ADVERSE_EVENT,
                ),
                SECONDARY_ENDPOINT,
                "Safety",
            ),
            (
                syntax(
                    "Number of participants with at least one [Activity] of special "
                    "interest, including immune-mediated events",
                    ADVERSE_EVENT,
                ),
                SECONDARY_ENDPOINT,
                "Safety",
            ),
            (syntax("Deaths"), SECONDARY_ENDPOINT, "Safety"),
            (
                syntax(
                    "Number of participants with laboratory abnormalities in [ActivitySubGroup]",
                    LAB_PANELS,
                ),
                SECONDARY_ENDPOINT,
                "Safety",
            ),
            (
                syntax(
                    "Number of participants with dose modifications of [Compound]",
                    LUMAVANT,
                ),
                SECONDARY_ENDPOINT,
                "Safety",
            ),
            (
                syntax("EDC-to-Safety system SAE reconciliation status"),
                SECONDARY_ENDPOINT,
                "Safety",
            ),
        ],
    },
    {
        "text": syntax("To characterize [Compound] exposure", LUMAVANT),
        "level": "Secondary Objective",
        "category": "Pharmacokinetics",
        "endpoints": [
            (
                syntax(
                    "Concentration-time profiles of [Compound] using protocol-defined "
                    "pre-dose and post-dose timepoints",
                    LUMAVANT,
                ),
                SECONDARY_ENDPOINT,
                "Pharmacokinetics",
            ),
        ],
    },
    {
        "text": syntax(
            "To evaluate immune and biomarker activity of [Compound]", LUMAVANT
        ),
        "level": "Secondary Objective",
        "category": "Pharmacodynamics",
        "endpoints": [
            (
                syntax(
                    "Blood-based pharmacodynamic markers measured in [Activity]",
                    PD_BLOOD_SAMPLE,
                ),
                SECONDARY_ENDPOINT,
                "Pharmacodynamics",
            ),
            (
                syntax("Exploratory biopsy/molecular analyses where enabled"),
                EXPLORATORY_ENDPOINT,
                "Pharmacodynamics",
            ),
        ],
    },
    {
        "text": syntax(
            "To confirm consistency of key efficacy, population-defining and "
            "safety-reporting data across EDC, IRT, central imaging reader and "
            "external Safety system sources"
        ),
        "level": "Secondary Objective",
        "category": None,
        "endpoints": [
            (
                syntax(
                    "Disease stage stratification match status between EDC Disease "
                    "History and IRT"
                ),
                SECONDARY_ENDPOINT,
                None,
            ),
            (
                syntax(
                    "Central-reader versus site-entered RECIST response match status"
                ),
                SECONDARY_ENDPOINT,
                None,
            ),
            (
                syntax(
                    "SAE match status between EDC AE/Safety Report forms and external "
                    "Safety system records"
                ),
                SECONDARY_ENDPOINT,
                None,
            ),
        ],
    },
    {
        # Not listed among the secondary objectives in the synopsis.
        "text": syntax(
            "To evaluate health status and symptoms in participants with [DiseaseDisorder]",
            NSCLC,
        ),
        "level": "Exploratory Objective",
        "category": None,
        "endpoints": [
            (
                syntax("Responses to [Activity]", QOL_QUESTIONNAIRE),
                EXPLORATORY_ENDPOINT,
                None,
            ),
        ],
    },
]

# --------------------------------------------------------------------------
# Eligibility criteria (protocol sections 5.1 and 5.2)
# --------------------------------------------------------------------------
INCLUSION_CRITERIA = [
    (
        # Same text as the Sponsor template shipped with OSB demo data, which
        # the import then reuses instead of creating a new one.
        syntax(
            "Age [NumericValue] [Age Unit] or above at the time of signing the informed consent.",
            number(18),
            YEARS,
        ),
        "Demography",
    ),
    (
        syntax(
            "Histologically or cytologically confirmed advanced, unresectable, "
            "recurrent, or metastatic [DiseaseDisorder].",
            NSCLC,
        ),
        "Diseases",
    ),
    (
        syntax(
            "Advanced disease stage consistent with the protocol-defined stratification "
            "factor, with stage captured in the EDC Disease History form and assigned in "
            "IRT at enrollment/randomization."
        ),
        "Diseases",
    ),
    (
        syntax(
            "Tumor PD-L1 positivity documented by a validated local or central assay "
            "according to sponsor-defined threshold."
        ),
        "Diseases",
    ),
    (
        syntax(
            "Documented disease progression during or after standard therapy appropriate "
            "for tumor histology and molecular status."
        ),
        "Diseases",
    ),
    (
        syntax("At least [NumericValue] measurable lesion by RECIST v1.1.", number(1)),
        "Diseases",
    ),
    (
        syntax(
            "ECOG performance status of [NumericValue] or [NumericValue] at screening, with "
            "ECOG [NumericValue] permitted only by sponsor waiver if clinically justified.",
            number(0),
            number(1),
            number(2),
        ),
        "Physical Findings",
    ),
    (
        syntax("Adequate hematologic, hepatic, renal, and coagulation function."),
        "Laboratory Parameters",
    ),
    (
        syntax(
            "For participants of childbearing potential, negative [Activity] and agreement "
            "to use protocol-defined contraception.",
            PREGNANCY_TEST,
        ),
        "Lifestyle Factors",
    ),
    (
        syntax(
            "Ability to understand and sign informed consent and comply with study procedures."
        ),
        "GCP Related",
    ),
]
EXCLUSION_CRITERIA = [
    (
        syntax(
            "Prior severe hypersensitivity to checkpoint inhibitor therapy or any component "
            "of [Compound].",
            LUMAVANT,
        ),
        "Medications",
    ),
    (
        syntax(
            "Active or history of clinically significant autoimmune disease requiring "
            "systemic immunosuppression within the protocol-defined window."
        ),
        "Diseases",
    ),
    (
        syntax(
            "Active interstitial lung disease, pneumonitis requiring systemic steroids, or "
            "clinically significant pulmonary fibrosis."
        ),
        "Diseases",
    ),
    (syntax("Untreated or unstable central nervous system metastases."), "Diseases"),
    (syntax("Active infection requiring systemic therapy."), "Diseases"),
    (
        syntax(
            "Clinically significant cardiac disease, uncontrolled arrhythmia, or reduced "
            "left ventricular ejection fraction where cardiac assessment is required."
        ),
        "Diseases",
    ),
    (
        syntax(
            "Use of prohibited concomitant medications, including high-dose systemic "
            "corticosteroids or other immunosuppressants, within the protocol-defined "
            "washout period."
        ),
        "Medications",
    ),
    (syntax("Pregnancy or breastfeeding."), "Lifestyle Factors"),
    (
        syntax(
            "Any condition that, in the investigator judgment, would interfere with "
            "participant safety, protocol compliance, or interpretation of results."
        ),
        "Diseases",
    ),
]


# --------------------------------------------------------------------------
# SoA footnotes: the qualifiers in the protocol's SoA cells (section 7) and
# the notes the SoA needs to be read correctly. The import creates the
# templates; fixups.py finish attaches them to the study's SoA rows (study
# activities or subgroups), columns (visits) and epochs.
# --------------------------------------------------------------------------
FOOTNOTE_TYPE = "SoA Footnote"
VISIT_DESCRIPTIONS = {visit["key"]: visit["description"] for visit in VISITS}


def on_activities(*names):
    return [("StudyActivity", name) for name in names]


def on_subgroups(*names):
    return [("StudyActivitySubGroup", name) for name in names]


def on_visits(*keys):
    return [("StudyVisit", VISIT_DESCRIPTIONS[key]) for key in keys]


def on_epochs(*names):
    return [("StudyEpoch", name) for name in names]


FOOTNOTES = [
    (
        syntax("Update as needed during treatment.", library=SPONSOR),
        on_activities(
            "Medical History/Concomitant Illness",
            "Disease History",
            "Prior Systemic Anticancer Therapy",
            "Prior Radiotherapy",
        ),
    ),
    (
        syntax(
            "Disease stage at study entry is the stratification factor: recorded in EDC "
            "Disease History, assigned independently in IRT at enrollment/randomization, "
            "and reconciled between the two sources."
        ),
        on_activities("Disease History", "Randomized"),
    ),
    (
        syntax(
            "Every [NumericValue] weeks for the first [NumericValue] weeks, then every "
            "[NumericValue] weeks.",
            number(6),
            number(24),
            number(9),
        ),
        on_subgroups("RECIST 1.1"),
    ),
    (
        syntax(
            "Also at end of treatment as clinically indicated, and progression status "
            "during survival follow-up."
        ),
        on_subgroups("RECIST 1.1"),
    ),
    (
        syntax(
            "Images are also submitted for blinded independent central review. "
            "Central-reader results are reconciled against site-entered RECIST data "
            "(TL, NTL, TA, NL, RA)."
        ),
        on_activities("Tumour Imaging"),
    ),
    (
        syntax("Also at selected treatment cycles.", library=SPONSOR),
        on_activities("Quality of Life Questionnaire"),
    ),
    (
        syntax("Symptom-directed or per cycle.", library=SPONSOR),
        on_activities("Physical Examination"),
    ),
    (
        syntax("At the 30-day safety follow-up, as clinically indicated."),
        on_subgroups(
            "Haematology", "Biochemistry", "Coagulation Parameters", "Urinalysis"
        ),
    ),
    (
        syntax("During treatment cycles, per local requirements.", library=SPONSOR),
        on_activities("Pregnancy Test"),
    ),
    (
        syntax("During treatment cycles, as clinically indicated.", library=SPONSOR),
        on_activities("12-Lead ECG"),
    ),
    (
        syntax(
            "When clinically indicated or required for cardiac assessment.",
            library=SPONSOR,
        ),
        on_activities("ECHO/MUGA"),
    ),
    (
        syntax(
            "Collected from informed consent. During survival follow-up, only serious "
            "adverse events related to study drug."
        ),
        on_activities("Adverse Event"),
    ),
    (
        syntax(
            "Serious adverse events are reconciled against the external Safety system "
            "(e.g. Argus)."
        ),
        on_activities("Adverse Event"),
    ),
    (
        syntax("During survival follow-up, as related."),
        on_activities("Concomitant Medication", "Concomitant Procedure"),
    ),
    (
        syntax(
            "At protocol-defined pre-dose and post-dose timepoints in Cycle 1, then at "
            "selected cycles and timepoints.",
            library=SPONSOR,
        ),
        on_activities("Lumavant PK Blood Sample", "PD Blood Sample"),
    ),
    (
        syntax(
            "One visit per [NumericValue]-day cycle. Cycles continue beyond Cycle "
            "[NumericValue] until treatment discontinuation.",
            number(CYCLE_DAYS),
            number(LAST_MODELLED_CYCLE),
        ),
        on_epochs("Treatment"),
    ),
    (
        syntax("Occurs at treatment discontinuation; the timing shown is nominal."),
        on_visits("EOT"),
    ),
    (syntax("Periodic contact; the timing shown is nominal."), on_visits("SURV")),
]

# A footnote on an activity must name one SoA row.
_activity_rows = [activity for activity, *_ in STUDY_ACTIVITIES]
for _item, _refs in FOOTNOTES:
    for _type, _key in _refs:
        if _type == "StudyActivity":
            assert (
                _activity_rows.count(_key) == 1
            ), f"ambiguous or unknown activity: {_key}"


def syntax_items():
    """Every syntax item in the dataset as (template kind, item, category)."""
    for objective in OBJECTIVES:
        yield "objective", objective["text"], objective["category"]
        for endpoint, _level, category in objective["endpoints"]:
            yield "endpoint", endpoint, category
    for item, category in [*INCLUSION_CRITERIA, *EXCLUSION_CRITERIA]:
        yield "criteria", item, category
    for item, _refs in FOOTNOTES:
        yield "footnote", item, None


# --------------------------------------------------------------------------
# Investigational product (protocol section 6)
# --------------------------------------------------------------------------
COMPOUND_NAME = "Lumavant"
SUBSTANCE_ID = "LUMAVANT"
ROUTE = "Intravenous"


def html(text):
    return f"<p>{text}</p>"


def sponsor_name(name):
    return {"sponsor_preferred_name": name}


def build_organisation():
    return {
        "clinical-programmes.json": [{"name": PROGRAMME}],
        "projects.json": [
            {
                "clinical_programme": {"name": PROGRAMME},
                "project_number": PROJECT_NUMBER,
                "name": PROJECT_NAME,
                "description": PROJECT_DESCRIPTION,
            }
        ],
    }


def build_study_metadata(study_number):
    study_id = f"{PROJECT_NUMBER}-{study_number}"
    identification = {
        "study_number": study_number,
        "study_acronym": None,
        "study_id": study_id,
        "project_number": PROJECT_NUMBER,
        "project_name": PROJECT_NAME,
        "clinical_programme_name": PROGRAMME,
        "description": None,
    }
    metadata = {
        "identification_metadata": identification,
        "high_level_study_design": {
            "study_type_code": {"name": "Interventional"},
            "trial_phase_code": {"name": "Phase 2"},
            # trial_types_codes is left out on purpose: the importer passes its
            # term_uids through unresolved, so they must not come from here.
            "is_extension_trial": False,
            "is_adaptive_design": False,
            "post_auth_indicator": False,
        },
        "study_population": {
            "therapeutic_area_codes": [{"name": THERAPEUTIC_AREA}],
            "disease_conditions_or_indications_codes": [{"name": INDICATION}],
            "diagnosis_groups_codes": [{"name": DIAGNOSIS_GROUP}],
            "sex_of_participants_code": {"name": "Both"},
            "rare_disease_indicator": False,
            "healthy_subject_indicator": False,
            "planned_minimum_age_of_subjects": {
                "duration_value": MINIMUM_AGE[0],
                "duration_unit_code": {"name": MINIMUM_AGE[1]},
            },
            "planned_maximum_age_of_subjects_null_value_code": {
                "name": "Not applicable"
            },
            "pediatric_study_indicator": False,
            "pediatric_postmarket_study_indicator": False,
            "pediatric_investigation_plan_indicator": False,
            # Not in the importer's patch template, kept for reference.
            "number_of_expected_subjects": EXPECTED_SUBJECTS,
        },
        "study_intervention": {
            "intervention_type_code": {"name": "Pharmacologic Substance"},
            "add_on_to_existing_treatments": False,
            "intervention_model_code": {"name": "Parallel"},
            "is_trial_randomised": True,
            "stratification_factor": (
                "Disease stage at study entry (Stage IIIB/IIIC vs Stage IV), captured "
                "in EDC Disease History and supplied independently by IRT"
            ),
            "trial_blinding_schema_code": {"name": "Open Label"},
            "drug_study_indication": True,
            "trial_intent_types_codes": [{"name": "Treatment"}],
        },
        "study_description": {
            "study_title": STUDY_TITLE,
            "study_short_title": STUDY_SHORT_TITLE,
        },
    }
    study = {"uid": STUDY_UID, "current_metadata": metadata, "study_status": "DRAFT"}
    listing = {
        "uid": STUDY_UID,
        "current_metadata": {"identification_metadata": identification},
    }
    return {"studies.json": [listing], f"studies.{STUDY_UID}.json": study}


def build_epochs():
    return [
        {
            "uid": f"StudyEpoch_{order}",
            "epoch_name": epoch["subtype"],
            "epoch_subtype_name": epoch["subtype"],
            "order": order,
            "description": epoch["description"],
            "start_rule": epoch["start_rule"],
            "end_rule": epoch["end_rule"],
            "color_hash": epoch["color_hash"],
            "duration": None,
            "duration_unit": None,
        }
        for order, epoch in enumerate(EPOCHS, start=1)
    ]


def visit_uid(key):
    return f"StudyVisit_{key}"


def build_visits():
    visits = []
    for number, visit in enumerate(VISITS, start=1):
        visits.append(
            {
                "uid": visit_uid(visit["key"]),
                "visit_name": f"Visit {number}",
                "visit_short_name": f"{'P' if visit['contact_mode'] == 'Phone Contact' else 'V'}{number}",
                "visit_number": number,
                "unique_visit_number": number * 100,
                "visit_class": "SINGLE_VISIT",
                "visit_subclass": "SINGLE_VISIT",
                "description": visit["description"],
                "study_epoch_name": visit["epoch"],
                "visit_type": sponsor_name(visit["visit_type"]),
                "time_reference": sponsor_name(visit["time_reference"]),
                "time_value": visit["time_value"],
                "time_unit_name": "days",
                "visit_window_unit_name": "days",
                "min_visit_window_value": 0,
                "max_visit_window_value": 0,
                "visit_contact_mode": sponsor_name(visit["contact_mode"]),
                "is_global_anchor_visit": visit["is_global_anchor_visit"],
                "is_soa_milestone": visit["is_soa_milestone"],
                "show_visit": True,
                "consecutive_visit_group": None,
                "visit_sublabel_reference": None,
                "start_rule": None,
                "end_rule": None,
            }
        )
    return visits


def build_arms():
    return [
        {
            "name": arm["name"],
            "short_name": arm["short_name"],
            "code": arm["code"],
            "description": arm["description"],
            "arm_colour": arm["arm_colour"],
            "randomization_group": arm["randomization_group"],
            "number_of_subjects": None,
            "arm_type": sponsor_name(arm["arm_type"]),
        }
        for arm in ARMS
    ]


def build_elements():
    return [
        {
            "name": element["name"],
            "short_name": element["short_name"],
            "code": None,
            "description": None,
            "planned_duration": None,
            "start_rule": element["start_rule"],
            "end_rule": element["end_rule"],
            "element_colour": element["element_colour"],
            "element_subtype": sponsor_name(element["subtype"]),
        }
        for element in ELEMENTS
    ]


def build_design_cells():
    cells = []
    for arm, cells_by_epoch in DESIGN_MATRIX.items():
        for epoch, element in cells_by_epoch.items():
            cells.append(
                {
                    "study_arm_name": arm,
                    "study_branch_arm_name": None,
                    "study_epoch_name": epoch,
                    "study_element_name": element,
                    "transition_rule": None,
                    "order": len(cells) + 1,
                }
            )
    return cells


def _named(name, sentence_case):
    return {
        "name": name,
        "name_sentence_case": sentence_case,
        "definition": None,
        "abbreviation": None,
        "library_name": SPONSOR,
    }


def build_library_activities():
    groupings = {}
    for activity, group, subgroup, _soa_group, _visits in STUDY_ACTIVITIES:
        if activity in NEW_ACTIVITIES:
            groupings.setdefault(activity, [])
            pair = {"activity_group_name": group, "activity_subgroup_name": subgroup}
            if pair not in groupings[activity]:
                groupings[activity].append(pair)
    activities = []
    for name, (sentence_case, definition) in NEW_ACTIVITIES.items():
        item = _named(name, sentence_case)
        item["definition"] = definition
        item["activity_groupings"] = groupings[name]
        activities.append(item)
    return {
        "concepts.activities.activity-groups.json": [
            _named(n, s) for n, s in NEW_ACTIVITY_GROUPS
        ],
        "concepts.activities.activity-sub-groups.json": [
            _named(n, s) for n, s in NEW_ACTIVITY_SUBGROUPS
        ],
        "concepts.activities.activities.json": activities,
    }


def study_activity_uid(index):
    return f"StudyActivity_{index:03d}"


def build_study_activities():
    activities, schedules = [], []
    for index, (activity, group, subgroup, soa_group, visits) in enumerate(
        STUDY_ACTIVITIES, start=1
    ):
        uid = study_activity_uid(index)
        activities.append(
            {
                "study_activity_uid": uid,
                "activity": {"name": activity},
                "study_activity_group": {"activity_group_name": group},
                "study_activity_subgroup": {"activity_subgroup_name": subgroup},
                "study_soa_group": {"soa_group_term_name": soa_group},
            }
        )
        for key in visits:
            schedules.append(
                {
                    "study_activity_uid": uid,
                    "study_visit_uid": visit_uid(key),
                    "note": None,
                }
            )
    return activities, schedules


def _template(item, category, **extra):
    # No sub-categories: the importer resolves endpoint sub-categories against
    # no codelist at all, so they could match a same-named term anywhere.
    template = {
        "name": html(item.text),
        "guidance_text": None,
        "library": {"name": item.library},
        "indications": None,
        "categories": [{"name": sponsor_name(category)}] if category else None,
        "default_parameter_terms": None,
    }
    template.update(extra)
    return template


def parameter_terms(item):
    """API parameter_terms for an instance of the item, uids unresolved. The
    importer resolves each term by type and name, and only for terms that
    have a "uid" key."""
    return [
        {
            "conjunction": item.conjunction if len(values) > 1 else "",
            "value": None,
            "terms": [
                {"index": index, "name": value.name, "type": value.type, "uid": None}
                for index, value in enumerate(values, start=1)
            ],
        }
        for values in item.values
    ]


def _instance(item):
    return {
        "name": html(item.rendered()),
        "template": {"name": html(item.text)},
        "library": {"name": item.library},
        "parameter_terms": parameter_terms(item),
    }


def build_objectives_and_endpoints():
    objective_templates, endpoint_templates = [], []
    study_objectives, study_endpoints = [], []
    for objective in OBJECTIVES:
        objective_templates.append(
            _template(
                objective["text"], objective["category"], is_confirmatory_testing=False
            )
        )
        study_objectives.append(
            {
                "objective": _instance(objective["text"]),
                "objective_level": sponsor_name(objective["level"]),
            }
        )
        for item, level, category in objective["endpoints"]:
            endpoint_templates.append(_template(item, category))
            study_endpoints.append(
                {
                    "endpoint": _instance(item),
                    "endpoint_level": sponsor_name(level),
                    "endpoint_sublevel": None,
                    "study_objective": {
                        "objective": {"name": html(objective["text"].rendered())}
                    },
                    "timeframe": None,
                }
            )
    return {
        "objective-templates.json": objective_templates,
        "endpoint-templates.json": endpoint_templates,
        f"studies.{STUDY_UID}.study-objectives.json": study_objectives,
        f"studies.{STUDY_UID}.study-endpoints.json": study_endpoints,
    }


def build_criteria():
    templates, study_criteria = [], []
    for criteria_type, rows in (
        ("Inclusion Criteria", INCLUSION_CRITERIA),
        ("Exclusion Criteria", EXCLUSION_CRITERIA),
    ):
        for item, category in rows:
            templates.append(
                _template(item, category, type={"name": sponsor_name(criteria_type)})
            )
            study_criteria.append({"criteria": _instance(item)})
    return {
        "criteria-templates.json": templates,
        f"studies.{STUDY_UID}.study-criteria.json": study_criteria,
    }


def build_footnote_templates():
    return {
        "footnote-templates.json": [
            _template(item, None, type={"name": sponsor_name(FOOTNOTE_TYPE)})
            for item, _refs in FOOTNOTES
        ]
    }


def build_study_compounds():
    return [
        {
            "compound": {"name": COMPOUND_NAME},
            "compound_alias": {"name": COMPOUND_NAME},
            "medicinal_product": {"name": COMPOUND_NAME},
            "type_of_treatment": {"name": "Investigational Product"},
            "reason_for_missing_null_value": None,
            "other_info": (
                "Regimen A (DRUG_1) and regimen B (DRUG_2); intravenous infusion in "
                "21-day cycles"
            ),
        }
    ]


def build_compounds_step():
    """Input for importers.run_import_compounds, which creates the medicinal
    product a study compound needs (mockdatajson does not)."""
    return {
        "active_substances.json": [
            {
                "external_id": SUBSTANCE_ID,
                "analyte_number": None,
                "short_number": None,
                "long_number": None,
                "inn": COMPOUND_NAME,
                "library_name": SPONSOR,
                "unii": None,
            }
        ],
        "pharmaceutical_products.json": [
            {
                "external_id": SUBSTANCE_ID,
                "library_name": SPONSOR,
                "dosage_forms": [],
                "routes_of_administration": [{"name": ROUTE}],
                "formulations": [
                    {
                        "external_id": "A",
                        "ingredients": [
                            {
                                "external_id": "IA",
                                "formulation_name": "A",
                                "active_substance": {"external_id": SUBSTANCE_ID},
                            }
                        ],
                    }
                ],
            }
        ],
        "compounds.json": [
            {
                "name": COMPOUND_NAME,
                "name_sentence_case": COMPOUND_NAME,
                "definition": "Novel immune checkpoint inhibitor",
                "abbreviation": None,
                "library_name": SPONSOR,
                "external_id": SUBSTANCE_ID,
                "analyte_number": None,
                "nnc_short_number": None,
                "nnc_long_number": None,
                "is_name_inn": False,
            }
        ],
        "medicinal_products.json": [
            {
                "external_id": SUBSTANCE_ID,
                "name": COMPOUND_NAME,
                "name_sentence_case": COMPOUND_NAME,
                "library_name": SPONSOR,
                "dose_values": [],
                "dose_frequencies": [],
                "delivery_device": None,
                "dispenser": None,
                "compound": {"name": COMPOUND_NAME},
                "pharmaceutical_products": [{"external_id": SUBSTANCE_ID}],
            }
        ],
    }


# Files the importer opens that this protocol does not populate. Writing them
# empty keeps "file not found" errors out of the import log. Sections that are
# switched off in import.env (units, value concepts, activity instances,
# compounds, brands) need no file.
EMPTY_FILES = [
    "dictionaries.UNII.json",
    "dictionaries.MED-RT.json",
    "dictionaries.UCUM.json",
    "timeframe-templates.json",
    "activity-instruction-templates.json",
    "objective-pre-instances.json",
    "criteria-pre-instances.json",
    "endpoint-pre-instances.json",
    "activity-instruction-pre-instances.json",
    "footnote-pre-instances.json",
    f"studies.{STUDY_UID}.study-branch-arms.json",
    f"studies.{STUDY_UID}.study-cohorts.json",
]


def build(study_number):
    files = {}
    files.update(build_organisation())
    files.update(build_study_metadata(study_number))
    files["dictionaries.SNOMED.json"] = [
        {
            "dictionary_id": dictionary_id,
            "name": name,
            "name_sentence_case": name[0].lower() + name[1:],
            "abbreviation": None,
            "definition": definition,
            "library_name": "SNOMED",
        }
        for dictionary_id, name, definition in SNOMED_TERMS
    ]
    files.update(build_library_activities())
    files.update(build_objectives_and_endpoints())
    files.update(build_criteria())
    files.update(build_footnote_templates())
    files[f"studies.{STUDY_UID}.study-epochs.json"] = build_epochs()
    files[f"studies.{STUDY_UID}.study-visits.json"] = build_visits()
    files[f"studies.{STUDY_UID}.study-arms.json"] = build_arms()
    files[f"studies.{STUDY_UID}.study-elements.json"] = build_elements()
    files[f"studies.{STUDY_UID}.study-design-cells.json"] = build_design_cells()
    activities, schedules = build_study_activities()
    files[f"studies.{STUDY_UID}.study-activities.json"] = activities
    files[f"studies.{STUDY_UID}.study-activity-schedules.json"] = schedules
    files[f"studies.{STUDY_UID}.study-compounds.json"] = build_study_compounds()
    for name in EMPTY_FILES:
        files.setdefault(name, [])
    return files, build_compounds_step()


def write_dir(directory, files):
    if directory.exists():
        shutil.rmtree(directory)
    directory.mkdir(parents=True)
    for name, content in sorted(files.items()):
        with open(directory / name, "w", encoding="utf-8") as handle:
            json.dump(content, handle, indent=2, ensure_ascii=False)
            handle.write("\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument(
        "--study-number",
        default="001",
        help="Study number, up to 4 digits and unique on the target (default: 001)",
    )
    args = parser.parse_args()
    if not (args.study_number.isdigit() and len(args.study_number) <= 4):
        parser.error("--study-number must be 1 to 4 digits")

    exported, compounds = build(args.study_number)
    write_dir(EXPORT_DIR, exported)
    write_dir(COMPOUNDS_DIR, compounds)
    print(
        f"Study {PROJECT_NUMBER}-{args.study_number}: wrote {len(exported)} files to "
        f"{EXPORT_DIR.name}/ and {len(compounds)} files to {COMPOUNDS_DIR.name}/"
    )


if __name__ == "__main__":
    main()
