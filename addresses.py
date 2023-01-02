import pandas as pd
import time
import asyncio
import aiohttp
import math
import requests
import json
from pycardano import Address, Network
from functools import reduce

#Danketsu
policy_id_aramar = "83c0ab67afc9148bd1571b7a14de1df03cd5624f5992d3b8ec84d6fb"
policy_id_atsuko = "83cb87b69639e20d7c99755fcfc310fb47882c3591778a3c869ea34c"
policy_id_daisuke = "8903555ad05ed1794f26240d44137717d0c8049e9133266222c4186a"
policy_id_fourth = "a4b7f3bbb16b028739efc983967f1e631883f63a2671d508023b5dfb"
policy_id_small = "427c7121856c400b69a589da28c5967cc86700530aee78302c94629a" # only 29 assets

list_policy_id = [policy_id_aramar, policy_id_atsuko, policy_id_daisuke, policy_id_fourth]

list_policy_id_test = [policy_id_small]

