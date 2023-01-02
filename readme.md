api.koios.rest 

addresses.py:
import libraries and give example addresses

csv_write.py:
Input policy_id to export policy_id.py containing list of asset names

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