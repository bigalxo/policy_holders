import time
import os
import math
from functools import reduce

import asyncio
import aiohttp
import pandas as pd
from pycardano import Address, Network

from addresses import list_policy_id_test as list_policy_id


# asyncio params
REQUEST_SIZE = 50 # how many calls can be made at once
RUN_DELAY = 3 # wait when one run finished before starting the next
RETRY_TIME = 3 # Delay between retries in seconds
RETRIES = 10 # Number of retries

# koios api params
OFFSET_SIZE = 1000
OFFSET_COUNT = 10
BATCH_OFFSET = OFFSET_SIZE * OFFSET_COUNT

def main():
    start_time = time.time()

    for policy_id in list_policy_id:
        file_name = os.path.join("outputs", f"{policy_id}.csv")
        get_addresses_for_policy(policy_id, file_name)

    stake_address_lists = []
    stake_address_set = []
    for policy_id in list_policy_id:
        print(f'Deriving Stake Keys from Address List in {policy_id}')
        file_name = os.path.join("outputs", f"{policy_id}.csv")
        df = pd.read_csv(file_name)

        addresses = set()
        for address_string in df["Address List"]:
            if len(address_string) == 103:
                primative_address = Address.from_primitive(address_string)
                address = Address(staking_part=primative_address.staking_part, network=Network.MAINNET)
                addresses.add(str(address))
            else:
                addresses.append(address_string)

        stake_address_lists.append(list(address))
        stake_address_set |= addresses

    num_elements = len(stake_address_set)

    formatted_time = format_time(time.time() - start_time)
    print('\n---------------------------------------------------------------------------\n')
    print('Report')
    for i in range(len(stake_address_lists)):
        print(
            f"\nPolicyID: {list_policy_id[i]}"
            f"\nHolders: {len(stake_address_lists[i])}"
            f"\nBurned: {list_burned[i]}"
        )
    print(f'\n{num_elements} stake keys holding all {len(list_policy_id)} policies')
    print(f'{len(list_unique)} unique holders across all {len(list_policy_id)} sets')
    print(f'Request Size: {REQUEST_SIZE}\nRetry Delay: {RETRY_TIME} Seconds\nRun Delay: {RUN_DELAY} Seconds')
    print(f'Failed Requests: {len(errors)}')
    print(f'Accuracy: {round(100*(1 - (len(errors)/(len(list_asset_names)+len(errors)))), 2)}%')
    print(f"Total Time: {formatted_time}")



def get_addresses_for_policy(policy_id, output_file):
    print(f'Getting Asset Names for PolicyID: {policy_id}')

    asset_start_time = time.time()
    assets = get_assets_for_policy(policy_id)

    asset_names = []
    for asset in assets:
        asset_names.append(asset["asset_name"])

    formatted_time = format_time(time.time() - asset_start_time)
    print(f'\n\nReturned: {len(asset_names)} Assets in {formatted_time}')

    urls = []
    for asset_name in asset_names: # create URLs for each asset_name
        urls.append(f"https://api.koios.rest/api/v0/asset_address_list?_asset_policy={policy_id}&_asset_name={asset_name}")

    time.sleep(2)
    print(f'\nGetting Addresses for Asset Names')
    address_start_time = time.time()
    
    addresses = asyncio.run(make_requests(urls)) # run request

    payment_addresses = []
    for address in addresses:
        payment_addresses.append(address["payment_address"])
    
    #save list_address to .csv with filename policy_id
    df = pd.DataFrame({'Address List' : payment_addresses})
    df.to_csv(output_file, index=False, encoding='utf-8')

    formatted_time = format_time(time.time() - address_start_time)
    print(f'\n\nReturned: {len(addresses)} Addresses in {formatted_time}')
    print(f'\nExported: "{policy_id}.csv"')
    print('---------------------------------------------------------------------------\n')


def get_assets_for_policy(policy_id):
    offset_start = 0
    assets = []
    while True:
        print(f'Scanning Indexes: {offset_start} - {offset_start + BATCH_OFFSET - 1}')

        urls = []
        for offset in range(offset_start, offset_start + BATCH_OFFSET, OFFSET_SIZE):
            urls.append(f"https://api.koios.rest/api/v0/asset_policy_info?_asset_policy={policy_id}&offset={offset}")

        assets += asyncio.run(make_requests(urls))

        if len(assets) % (BATCH_OFFSET) == 0: # if return was exactly 10,000, assume more than 10,000 and retry for 10,001-20,000
            offset_start += BATCH_OFFSET
        else:
            return assets


def format_time(time_in_seconds):
    hours = int(time_in_seconds // 3600)
    minutes = int((time_in_seconds % 3600) // 60)
    seconds = round((time_in_seconds % 60), 2)

    time_string = ""
    if hours > 0:
        time_string += f"{hours} Hours, "
    if hours > 0 or minutes > 0:
        time_string += f"{minutes} Minutes, "
    time_string += f"{seconds} Seconds"
    return time_string


async def make_requests(urls):
    batch_start = 0
    batch_end = min(batch_start + REQUEST_SIZE, len(urls))
    total_errors = 0
    output = []
    while True:
        if batch_start >= len(urls):
            break

        start_time = time.time()
        urls_slice = urls[batch_start: batch_end]

        async with aiohttp.ClientSession() as session:
            results = await asyncio.gather(*[get_response(url, session) for url in urls_slice])

        batch_errors = 0
        for info, errors in results:
            output += info
            batch_errors += errors
        total_errors += batch_errors

        await asyncio.sleep(RUN_DELAY)

        formatted_time = format_time(time.time() - start_time)
        print(
            f'Last batch: {formatted_time}, '
            f'{batch_errors} Failed Requests, '
            f'{total_errors} Total Failed Requests, '
            f'{round(100 * (1 - (total_errors / (len(output) + total_errors))), 2)}% Accuracy',
        )

        batch_start += REQUEST_SIZE
        batch_end = min(batch_start + REQUEST_SIZE, len(urls))

    return output


async def get_response(url, session):
    for retry in range(RETRIES):
        try:
            async with session.get(url=url) as response:
                info = await response.json()
                return info, retry
        except Exception:
            await asyncio.sleep(RETRY_TIME)
    print(f"Failed to get url {url} after {RETRIES} retries")
    return [], retry
            



if __name__ == "__main__":
    main()
