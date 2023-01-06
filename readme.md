# @DanketsuStatBot

Find relational data between the four Danketsu policies and tweet the report

## API Source

https://api.koios.rest/

## Files

### twitter.py:

Run report.py and tweet the results

### policies.py:

Example policyIDs as strings and lists of strings

Also contains some exchange addresses which are not currently utilised

### report.py:

Input list of policy IDs from policies.py to export .csv of addresses and display report on holder data

#### Example Output:

    Getting Asset Names for PolicyID: 427c7121856c400b69a589da28c5967cc86700530aee78302c94629a
    Scanning Indexes: 0 - 9999
    Last batch: 4.42 Seconds, 0 Failed Requests, 0 Total Failed Requests, 100.0% Accuracy


    Returned: 31 Assets in 4.42 Seconds

    Getting Addresses for Asset Names
    Last batch: 7.49 Seconds, 0 Failed Requests, 0 Total Failed Requests, 100.0% Accuracy


    Returned: 29 Addresses in 7.5 Seconds
    Burned: 2

    Exported: "427c7121856c400b69a589da28c5967cc86700530aee78302c94629a.csv"   
    ---------------------------------------------------------------------------

    Getting Asset Names for PolicyID: 10d11bf75e738fa5551b598868d725551aca9f833acda1bfd20fb068
    Scanning Indexes: 0 - 9999
    Last batch: 4.32 Seconds, 0 Failed Requests, 0 Total Failed Requests, 100.0% Accuracy


    Returned: 29 Assets in 4.32 Seconds

    Getting Addresses for Asset Names
    Last batch: 6.79 Seconds, 0 Failed Requests, 0 Total Failed Requests, 100.0% Accuracy


    Returned: 27 Addresses in 6.79 Seconds
    Burned: 2

    Exported: "10d11bf75e738fa5551b598868d725551aca9f833acda1bfd20fb068.csv"
    ---------------------------------------------------------------------------

    Getting Asset Names for PolicyID: c0e8073b9171ff085eb5e421002d314ac614632ac5ca9f230da83366
    Scanning Indexes: 0 - 9999
    Last batch: 5.07 Seconds, 0 Failed Requests, 0 Total Failed Requests, 100.0% Accuracy


    Returned: 184 Assets in 5.07 Seconds

    Getting Addresses for Asset Names
    Last batch: 7.84 Seconds, 0 Failed Requests, 0 Total Failed Requests, 100.0% Accuracy
    Last batch: 4.23 Seconds, 0 Failed Requests, 0 Total Failed Requests, 100.0% Accuracy
    Last batch: 11.22 Seconds, 36 Failed Requests, 36 Total Failed Requests, 80.33% Accuracy
    Last batch: 4.19 Seconds, 0 Failed Requests, 36 Total Failed Requests, 83.41% Accuracy


    Returned: 181 Addresses in 27.47 Seconds
    Burned: 3

    Exported: "c0e8073b9171ff085eb5e421002d314ac614632ac5ca9f230da83366.csv"
    ---------------------------------------------------------------------------

    Deriving Stake Keys from Address List in 427c7121856c400b69a589da28c5967cc86700530aee78302c94629a
    Deriving Stake Keys from Address List in 10d11bf75e738fa5551b598868d725551aca9f833acda1bfd20fb068
    Deriving Stake Keys from Address List in c0e8073b9171ff085eb5e421002d314ac614632ac5ca9f230da83366

    ---------------------------------------------------------------------------

    Report

    PolicyID: 427c7121856c400b69a589da28c5967cc86700530aee78302c94629a
    Holders: 24
    Burned: 2
    PolicyID: 10d11bf75e738fa5551b598868d725551aca9f833acda1bfd20fb068
    Holders: 18
    Burned: 2

    PolicyID: c0e8073b9171ff085eb5e421002d314ac614632ac5ca9f230da83366
    Holders: 94
    Burned: 3

    4 stake keys holding all 3 policies
    113 unique holders across all 3 sets
    Request Size: 50
    Retry Delay: 3 Seconds
    Run Delay: 3 Seconds
    Failed Requests: 36
    Accuracy: 87.14%
    Total Time: 1 Minutes, 1.67 Seconds

## TODO

Add Twitter API to tweet report DONE
Add Exchange data to report