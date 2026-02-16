# Study Data Specifications

## Study Activity Instances

A Study activity instance is a related package that is linked to the activity provided from the library. The package consists of codes needed for the downstream processing of data, like data collection, SDTM and ADaM. These codes are required for submissions and the intention is to standardize deliveries, so Health authorities can perform the review of the submission faster.
The Study Activity Instances page provides an overview of activities and related instances, connecting metadata end-to-end from protocol to analysis and CSR.

## Study Activity Instance Table Content: 

When you open this tab, you will see a table containing all study activities, related instances, and attached attributes. The table has the following column headers:

| Header  | Short explanation   |
|---------|---------------------|
| State/Action | This column indicates the current status of an activity or activity instance, or the action required. Possible states/actions are: Review not needed, Review needed, Reviewed, Add instance, Remove instance, Not applicable, Reviewed |
| Library | Will usually be ‘Sponsor’ |
| SoA Group | The selected SoA group from the Study Activity |
| Activity Group | The Activity Group, that the selected study activity belongs to, e.g. AE Requiring Additional Data |
| Activity Subgroup | The Activity Subgroup, that the selected study activity belongs to, e.g. Laboratory assessment |
| Activity | The Study Activity in the study, e.g. Albumin |
| Data Collection | Yes or No. No will only be used for reminders or system operators or triggers |
| Activity Instance | The name of the Activity Instance, e.g. Albumin Urine |
| Topic Code | Code used to convert collected data to SDTM, e.g. ALBUMIN_N_URINE |
| Test name code | Displays the test name code item linked to the activity instance |
| Specimen | Displays the specimen activity item linked to the activity instance |
| Standard unit | Displays the standar unit item linked to the activity instance |
| ADaM param Code | The code used in ADaM e.g. ALBU |
| Important | An activity–activity instance pair can be marked as Important by editing the Activity–Instance relationship or by switching the table to edit mode. |
| Baseline visits | Link an activity–activity instance pair to baseline visits by editing the Activity–Instance relationship or by switching the table to edit mode. |
| Data Supplier | Link an activity–activity instance pair to a Data Supplier by editing the Activity–Instance relationship or by switching the table to edit mode. |
| Origin Type | The Origin Type for an activity–activi-ty instance is prefilled with the default value linked to a specific Data Supplier in the library. Change it by editing the Activity–Instance relationship or switching the table to edit mode. |
| Origin Source | The Origin Source for an activity–activi-ty instance is prefilled with the default value linked to a specific Data Supplier in the library. Change it by editing the Activity–Instance relationship or switching the table to edit mode. |

## Investigating the table

There is one row per activity-instance relation.

If an activity has more than one required activity instance related, then one row will be available for each activity instance related to the activity.

This means that some activities, such as the Patient Health Questionnaire (PHQ-9), will appear in multiple rows because a single activity may contain several questions (activity instances).

<figure style="text-align:left"> <a href="../../../images/user_guides/data_specifications_01.png"> <img src="~@source/images/user_guides/data_specifications_01.png" alt="Activity Instance table" /> </a> <figcaption>Table 1 One row per required activity Instance</figcaption> </figure>


## Explanation of the State/Actions column:
- <font style="background-color:green;">Green</font>: Review not needed - requires no action from the user
- <font style="background-color:yellow;">Yellow</font>: Review needed - requires attention from the user; user must verify that the activity–activity instance pair satisfies the study requirements
- <font style="background-color:green;">Green</font>: Reviewed - no additional action is required by the user, as the activity–activity instance pair has been confirmed as reviewed
- <font style="background-color:red;">Red</font>: Add instance - requires action from the user; the activity is expected to be linked with an activity instance
- <font style="background-color:red;">Red</font>: Remove Instance - requires user action; the activity may be linked to only a single instance at the study level
- <font style="background-color:grey;">Grey</font>: Not applicable - requires no action from the user; the activity is not expected to be linked with an activity instance

Independent of the state or actions, it is advisable to check all content for a study to make sure that all needs are covered.

## Rules for populating activity instance relations

Most activity-instance relations are auto-selected and auto-published by basic rules:

[![Activity Instance rules](~@source/images/user_guides/data_specifications_02.png)](../../../images/user_guides/data_specifications_02.png)

*<p style="text-align: left;">Table 2 State/Actions rules</p>*

## Edit relationship and define Important and Baseline flags and Data Supplier attributes

In the Row Actions to the left (the 3 dots) several options are available:
- Edit Activity‑Instance relationship: opens a form to edit the relationship. Only activity instances that are available for the activity can be selected. You can mark an activity instance as Important, and a Baseline flag may be added to it. An activity instance can be linked to a Data Supplier, and an Origin Type and Source can be selected if different from the defaults.
> Important and Baseline flags, as well as the Data Supplier (including Origin Type and Source), can also be set via table edit mode, which you open by clicking the pencil icon at the top right above the table. 
- Delete Activity-Instance relationship: deletes the relationship, with a warning before deletion
- Update Instance to new version: only available when a new version of the activity instance is available in the library. A small form will ask if you wish to update, with the option to select Yes, No, or Cancel.
- Row History: shows all changes

Currently you cannot request new activity instances from inside OpenStudyBuilder. If needed, this must go through the study Standards Developer.

It is possible to download the Study Activity Instances as .csv, .json, .xml and excel, where excel is very easy to filter on.  

## Study Data Supplier, Origin Source and Origin Type 

Data suppliers must first be defined on the Study Data Supplier page (under Manage Study). 
If no suppliers are defined at the study level, 'No data available' will be displayed in the Data Supplier dropdown on the Study Activity Instances page. 
Data suppliers are usually linked with a default Origin Type and Origin Source. Selecting a supplier on the Study Activity Instances page populates Origin Type and Origin Source with the supplier's defaults, however, these can be changed manually.

In the tables below, you can find short descriptions of origin types and sources.

| Origin Type | Short definition   |
|---------|---------------------|
| Assigned Value | Data that is either: Determined by individual judgment as provided by an evaluator, or Coded terms supplied as part of a coding process, or Values set independently of any subject-related data value in order to complete a dataset. |
| Collected value | A value that is actually observed and recorded by a person or obtained by an instrument. Note that a collected entry translated to a synonymous controlled term still has a type Collected. |
| Copied value | A field populated by copying a variable from another dataset. |
| Derived value | A value that is calculated by an algorithm or reproducible rule, and which is dependent upon other data values, including data values available within the dataset or externally provided data values. MethodDef must be used to document the algorithm or rule used for a derived value. |
| Protocol value | Data that is defined as part of the study protocol, investigator instructions, standard operating procedures or trial design preparation. |
| Not available | Used when the origin is not available and cannot be determined. Sponsors should specify additional details that may be helpful to the reviewer in the Comments section of the data definition file. |
| Other | Other |

| Origin Source | Short definition   |
|---------|---------------------|
| Clinical Study Sponsor | Clinical data that were actually observed or recorded by study Sponor. |
| Investigator | Clinical data that were actually observed or recorded by Investigator. |
| Study Subject | Clinical data that were actually observed or recorded by Study Subject. |
| Vendor | Clinical data that were actually observed or recorded by Vendor. |

## Purpose of the Operational SoA table

The table contains all the information from the Study Activities tab, the detailed SoA tab and the Activity Instances tab. 

The table is intended for QC of Protocol (similar to the Protocol Metadata Document (PMD)), CRF content, SDTM and ADaM generation and for providing information to vendors.

## Investigating the Operational SoA table

In this table, there is no option to add, edit, or delete information, besides normal page actions and view options. It is possible to download the table in different formats in the upper right corner.

The top rows of the table display the visit scheduling information, including epochs, visits, visit window, and timing towards the global anchor (baseline).

The selected preferred time unit will also be visible in the grey area above the table content.
The left-hand column displays the hierarchy for the activities, starting with the SoA group (if turned on), Activity Group, Activity subgroup, Activity, and Activity Instance. The legends of the levels are currently not implemented.

There is a fold-out option with expand or collapse all, and the option to expand within the groupings.
On the activity instance level, the Topic Code and ADaM Parameter Code are visible. The activity instances carry a hyperlink to access additional instance information in the library.


[![Operational SoA table](~@source/images/user_guides/data_specifications_03.png)](../../../images/user_guides/data_specifications_03.png)

*<p style="text-align: left;">Figure 1 Operational SoA table</p>*




