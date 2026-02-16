@REQ_ID:1070683 @skip_on_prv_val
Feature: Library - Concepts - Activities - Activity instances - wizard stepper test_code mandatory validation
    As a user, I want to ensure that test_code is mandatory when creating Activity Instances with Wizard Stepper 
    process to ensure data integrity.

    Background: User must be logged in
        Given The user is logged in

    Scenario: [Create][Mandatory fields] User must not be able to continue without selecting test_code for Numeric Findings instance class
        Given The '/library/activities/activity-instances' page is opened
        When The Add Activity Instance button is clicked
        When First activity is selected from the activity list
        And Form continue button is clicked
        When The 'NumericFindings' is selected from the Activity instance class field
        And The 'LB' is selected from the Activity instance domain field
        And The 'AE ADDITIONAL DATA' is selected from the Data category field
        And The Instance unit_dimension and standard_unit are selected
        And Form continue button is clicked
        Then Warning is displayed for mandatory field 'Code submission value'
        And Warning is displayed for mandatory field 'Name submission value'
        And The Activity Instance Wizard Stepper 'Required' page is displayed

