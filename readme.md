api.koios.rest 

addresses.py:
import libraries and give example addresses

csv_write.py:
Input policy_id to export policy_id.py containing list of Addresses holding policy_id 

Example Input:
    policy_id = "427c7121856c400b69a589da28c5967cc86700530aee78302c94629a"

Example Output:

    PolicyID: 427c7121856c400b69a589da28c5967cc86700530aee78302c94629a
    Scanning Index: 1-1000
    Total: 29
    2 AssetIDs are burned or do not have an assosiated address
    Finding Addresses holding asssets
    100.00%
    Exported Address List as "427c7121856c400b69a589da28c5967cc86700530aee78302c94629a.csv"
    3.6 Seconds

csv_read.py:
Input list of policy_id's with assosiated .csv and output holder data

Example Input:
    list_policy_id = ['83c0ab67afc9148bd1571b7a14de1df03cd5624f5992d3b8ec84d6fb', '83cb87b69639e20d7c99755fcfc310fb47882c3591778a3c869ea34c', '8903555ad05ed1794f26240d44137717d0c8049e9133266222c4186a', 'a4b7f3bbb16b028739efc983967f1e631883f63a2671d508023b5dfb']

Example Output:

    Deriving Stake Keys from Address List in 83c0ab67afc9148bd1571b7a14de1df03cd5624f5992d3b8ec84d6fb
    Deriving Stake Keys from Address List in 83cb87b69639e20d7c99755fcfc310fb47882c3591778a3c869ea34c
    Deriving Stake Keys from Address List in 8903555ad05ed1794f26240d44137717d0c8049e9133266222c4186a
    Deriving Stake Keys from Address List in a4b7f3bbb16b028739efc983967f1e631883f63a2671d508023b5dfb

    Policy: 83c0ab67afc9148bd1571b7a14de1df03cd5624f5992d3b8ec84d6fb
    Holders: 2693

    Policy: 83cb87b69639e20d7c99755fcfc310fb47882c3591778a3c869ea34c
    Holders: 1730

    Policy: 8903555ad05ed1794f26240d44137717d0c8049e9133266222c4186a
    Holders: 1194

    Policy: a4b7f3bbb16b028739efc983967f1e631883f63a2671d508023b5dfb
    Holders: 344

    179 stake keys hold all 4 policies
    4008 unique holders across all 4 sets

    16.4 Seconds

get_all.py:
Input list of policy IDs to export .csv of addresses and display report on holder data

Example Input:
    list_policy_id = ['427c7121856c400b69a589da28c5967cc86700530aee78302c94629a', '10d11bf75e738fa5551b598868d725551aca9f833acda1bfd20fb068', 'c0e8073b9171ff085eb5e421002d314ac614632ac5ca9f230da83366']

Example Output:
    PolicyID: 427c7121856c400b69a589da28c5967cc86700530aee78302c94629a
    Scanning Index: 1-10000

    Returned: 31 Assets in 1.8 seconds
    Total Asset Names: 31

    Getting Addresses for Asset Names
    Request Size: 50
    Retry Delay: 10 Seconds
    Retries: 10

    Burned: 2
    Returned: 29 Addresses in 3.79 seconds

    Exported: "427c7121856c400b69a589da28c5967cc86700530aee78302c94629a.csv"
    ---------------------------------------------------------------------------

    PolicyID: 10d11bf75e738fa5551b598868d725551aca9f833acda1bfd20fb068
    Scanning Index: 1-10000

    Returned: 29 Assets in 1.33 seconds
    Total Asset Names: 29

    Getting Addresses for Asset Names
    Request Size: 50
    Retry Delay: 10 Seconds
    Retries: 10

    Burned: 2
    Returned: 27 Addresses in 4.82 seconds

    Exported: "10d11bf75e738fa5551b598868d725551aca9f833acda1bfd20fb068.csv"
    ---------------------------------------------------------------------------

    PolicyID: c0e8073b9171ff085eb5e421002d314ac614632ac5ca9f230da83366
    Scanning Index: 1-10000

    Returned: 184 Assets in 2.11 seconds
    Total Asset Names: 184

    Getting Addresses for Asset Names
    Request Size: 50
    Retry Delay: 10 Seconds
    Retries: 10

    Burned: 3
    Returned: 181 Addresses in 32.87 seconds

    Exported: "c0e8073b9171ff085eb5e421002d314ac614632ac5ca9f230da83366.csv"
    ---------------------------------------------------------------------------

    Deriving Stake Keys from Address List in 427c7121856c400b69a589da28c5967cc86700530aee78302c94629a
    Deriving Stake Keys from Address List in 10d11bf75e738fa5551b598868d725551aca9f833acda1bfd20fb068
    Deriving Stake Keys from Address List in c0e8073b9171ff085eb5e421002d314ac614632ac5ca9f230da83366

    ---------------------------------------------------------------------------

    Report

    policy: 427c7121856c400b69a589da28c5967cc86700530aee78302c94629a
    holders: 24

    policy: 10d11bf75e738fa5551b598868d725551aca9f833acda1bfd20fb068
    holders: 18

    policy: c0e8073b9171ff085eb5e421002d314ac614632ac5ca9f230da83366
    holders: 94

    4 stake keys holding all 3 policies
    113 unique holders across all 3 sets

    Total Time: 46.79 Seconds