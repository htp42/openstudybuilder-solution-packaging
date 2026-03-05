@REQ_ID:1074260 
Feature: Studies - Define Study - Study Activities - Schedule of Activities - Protocol

    As a system user,
    I want the system to ensure [Scenario],
    So that I can make complete and consistent specification of study SoA for the protocol.

    # Note, SoA footnotes is specified in dedicated feature

    Background: User is logged in and study has been selected
        Given The user is logged in
        And A test study is selected

    Scenario: [Test data] User must be able to create data needed for study protocol timeframe_instances
        And [API] The epoch with type 'Pre Treatment' and subtype 'Run-in' exists in selected study
        And [API] The epoch with type 'Treatment' and subtype 'Intervention' exists in selected study
        And [API] Study vists uids are fetched for current study
        When [API] Study visits in current study are cleaned-up
        And [API] The static visit data is fetched
        And [API] The dynamic visit data is fetched: contact mode 'On Site Visit', time reference 'Global anchor visit', type 'Pre-screening', epoch 'Run-in'
        And [API] The visit with following attributes is created: isGlobalAnchor 1, visitWeek 0
        And [API] The visit with following attributes is created: isGlobalAnchor 0, visitWeek 1, minVisitWindow -1, maxVisitWindow 1
        And [API] The dynamic visit data is fetched: contact mode 'On Site Visit', time reference 'Global anchor visit', type 'Randomisation', epoch 'Intervention'
        And [API] The visit with following attributes is created: isGlobalAnchor 0, visitWeek 2, minVisitWindow 3, maxVisitWindow 7
        And [API] All Activities are deleted from study
        And [API] Study Activity is created and approved
        And [API] Get SoA Group 'INFORMED CONSENT' id
        And [API] Activity is added to the study
        And Activity, Group And Subgroup names are fetch to be used in SoA

    @manual_test
    Scenario: [Navigation] User must be able to navigate to Protocol SoA page using side menu
        Given The '/studies' page is opened
        When The 'Study Activities' submenu is clicked in the 'Define Study' section
        And The 'Schedule of Activities' tab is selected
        And the SoA View is switched to 'Protocol SoA'
        Then The current URL is '/activities/soa'

    @manual_test
    Scenario: [Table][Options] User must be able to see The Protocol SoA options
        Given The test study '/activities/soa' page is opened
        Then A table is visible with following options
            | option          |
            | SoA layout      |
            | Show epochs     |
            | Show milestones |
        Then The Export option is visible

    @manual_test
    Scenario: [Navigation] User must be able to swich SoA Layout to Protocol SoA
        Given The test study '/activities/protocol' page is opened
        When The user switches the layout to 'Protocol SoA'
        Then The user is presented with 'Protocol SoA' layout

    @manual_test
    Scenario: [Navigation] User must be able to swich SoA Layout to Detailed SoA
        Given The test study '/activities/protocol' page is opened
        When The user switches the layout to 'Detailed SoA'
        Then The user is presented with 'Detailed SoA' layout

    @manual_test
    Scenario: [Navigation] User must be able to swich SoA Layout to Operational SoA
        Given The test study '/activities/protocol' page is opened
        When The user switches the layout to 'Operational SoA'
        Then The user is presented with 'Operational SoA' layout

    @manual_test
    Scenario: [Table][Overview] User must be able to view The study activities in The Protocol SoA table
        Given The test study '/activities/protocol' page is opened
        When The test study activities is selected for the study
        And The test study activities is marked to be displayed in the Protocol SoA including all groupings
        Then The Protocol SoA table matrix display rows for each test study activity grouped by activity group, activity subgroup and SoA group
    # Note The specific display/hide options for The Protocol SoA is specified in study-detailed-soa.feature

    @manual_test
    Scenario: [Settings] User must be able to define SoA settings for time unit and show baseline as time 0
        Given The test study '/activities/protocol' page is opened
        When The user selects The SoA settings control icon
        Then The SoA Settings form opens

    @manual_test
    Scenario Outline: [Display][Time unit] User must be able to control display of time in SoA by selecting time unit and option to display basline time as 0 or 1
        Given The test study '/activities/protocol' page is opened
        When User select <time unit> and <option for baseline shown as time 0> on The SoA Settings form
        Then The SoA time row will show <time unit>
        And SoA time values will be according to <study time>
        Examples:
            | time unit | option for baseline shown as time 0 | study time                 |
            | Days      | True                                | Study duration days value  |
            | Weeks     | True                                | Study duration weeks value |
            | Days      | False                               | Study day value            |
            | Weeks     | False                               | Study week value           |

    @manual_test
    Scenario Outline: [Display][Epochs][Milestones] User must be able to control display of study epoch and study visit milestone in protocol SoA
        Given The test study '/activities/protocol' page is opened
        When user select show epochs as <Show epochs> and show milestone as <Show milestones>
        Then The study epoch display is <Show epochs> in the protocol SoA header row
        And The study visit milestone display is <Show milestones> in the protocol SoA header row
        Examples:
            | Show epochs | Show milestones |
            | enabled     | enabled         |
            | enabled     | disabled        |
            | disabled    | enabled         |
            | disabled    | disabled        |

    @manual_test
    Scenario: [Export][Docx] User must be able to export The Protocol SoA table including an empty column for protocol section references
        Given The test study '/activities/protocol' page is opened
        When The export in DOCX format is selected
        Then Protocol SoA is downloaded as a DOCX file
        And DOCX file contains the Protocol SoA table matrix including an empty column for protocol section references

    @manual_test
    Scenario: [Display][Week] User must be able to select week view of Protocol SoA
        Given The test study '/activities/protocol' page is opened
        When The user selects preffered time unit as week
        Then The Protocol SoA is presented with Study Weeks as time representation

    @manual_test
    Scenario: [Display][Day] User must be able to select day view of Protocol SoA
        Given The test study '/activities/protocol' page is opened
        When The user selects preffered time unit as day
        Then The Protocol SoA is presented with Study Days as time representation

    @manual_test
    Scenario: [Baseline] User must be able to mark baseline visit as time 0
        Given The test study '/activities/protocol' page is opened
        When The user selects 'Baseline shown as time 0'
        Then The Protocol SoA present the baseline visit (radnomisation) as time 0


    Scenario: User must be able to split protocol SoA by particular visit
        When The test study '/activities/soa' page is opened
        And User switches to the 'protocol' view
        And The SoA Splitting is enabled
        And The user splits the SoA by 'V3'
        Then The SoA split is created on 'V3'

    Scenario: User must be able to split protocol SoA by on multiple visits
        When The test study '/activities/soa' page is opened
        And User switches to the 'protocol' view
        And The user unsplits the SoA by 'V3'
        And The user splits the SoA by 'V3'
        Then The SoA split is created on 'V3'
        When The user splits the SoA by 'V2'
        Then The SoA split is created on 'V2'

    Scenario: User must be able to unsplit SoA
        When The test study '/activities/soa' page is opened
        And User switches to the 'protocol' view
        And The user unsplits the SoA by 'V3'
        Then The SoA split on 'V3' is removed

    Scenario: [Export][CSV] User must be able to export the data in CSV format
        Given The test study '/activities/soa' page is opened
        And User switches to the 'protocol' view
        When User clicks export button
        And User selects 'CSV' format to export the table content
        Then The study specific 'protocol SoA' file without timestamp is downloaded in 'csv' format

    Scenario: [Export][EXCEL] User must be able to export the data in JSON format
        Given The test study '/activities/soa' page is opened
        And User switches to the 'protocol' view
        When User clicks export button
        And User selects 'EXCEL' format to export the table content
        Then The study specific 'protocol SoA' file without timestamp is downloaded in 'xlsx' format

    Scenario: [Export][DOCX] User must be able to export the data in XML format
        Given The test study '/activities/soa' page is opened
        And User switches to the 'protocol' view
        When User clicks export button
        And User selects 'DOCX' format to export the table content
        Then The study specific 'protocol SoA' file without timestamp is downloaded in 'docx' format