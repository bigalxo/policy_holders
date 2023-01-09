import time
import os
import math
from functools import reduce
import copy

import asyncio
import aiohttp
import pandas as pd
from pycardano import Address, Network

from policies import list_policy_id_test as policy_ids


# asyncio params
BATCH_SIZE = 100 # Quantity of calls made concurrently
RUN_DELAY = 5 # Delay between runs
RETRY_DELAY = 5 # Delay between retries in seconds
RETRIES = 1000 # Number of retries

# koios api params
OFFSET_SIZE = 1000
OFFSET_COUNT = 10
BATCH_OFFSET = OFFSET_SIZE * OFFSET_COUNT


def main():
    start_time = time.time()
    policy_addresses = {}
    burn_counts = {}
    asset_counts = {} # tracks total of assets scanned
    error_counts = {} # tracks total of failed calls
    for policy_id in policy_ids: # Write .csv, update vars
        file_name = os.path.join("outputs", f"{policy_id}.csv")
        addresses, burn_count, asset_count, errors = get_addresses_for_policy(policy_id, file_name)
        policy_addresses[policy_id] = addresses
        burn_counts[policy_id] = burn_count
        asset_counts[policy_id] = asset_count
        error_counts[policy_id] = errors

    global_stake_addresses = set() # List of unique Stake addresses across all policies
    stake_addresses = {} # List of Stake addresses per policy_id
    stake_addresses_three = {}
    for policy_id in policy_ids: # Read .csv, update vars
        print(f'Deriving Stake Keys from Address List in {policy_id}')

        policy_stake_addresses = set() # List of stake addresses for current policy_id
        addresses = policy_addresses[policy_id]
        for address in addresses: # Derive Stake key from address
            if len(address) == 103: # If address has Stake component
                primative_address = Address.from_primitive(address)
                cypto_address = Address(staking_part=primative_address.staking_part, network=Network.MAINNET)
                address = str(cypto_address)

            policy_stake_addresses.add(address)
            global_stake_addresses.add(address)
        if policy_id != 'a4b7f3bbb16b028739efc983967f1e631883f63a2671d508023b5dfb':
            stake_addresses_three[policy_id] = policy_stake_addresses
        stake_addresses[policy_id] = policy_stake_addresses

    just_three = reduce(lambda s1, s2: s1.intersection(s2), stake_addresses_three.values())
    #convert stake_addresses_lists to satisfy "Stake keys holding all policies" 
    all_mutual_addresses = reduce(lambda s1, s2: s1.intersection(s2), stake_addresses.values())

    error_total = sum(error_counts.values())
    asset_total = sum(asset_counts.values())

    formatted_time = format_time(time.time() - start_time)
    print('\n---------------------------------------------------------------------------\n')
    print('Report')
    for policy_id in policy_ids:
        print(
            f"\nPolicyID: {policy_id}"
            f"\nHolders: {len(stake_addresses[policy_id])}"
            f"\nBurned: {burn_counts[policy_id]}"
        )
    print(f'\n{len(all_mutual_addresses)} stake keys holding all {len(policy_ids)} policies')
    print(f'{len(global_stake_addresses)} unique holders across all {len(policy_ids)} sets')
    print(f'Batch Size: {BATCH_SIZE}\nRetry Delay: {RETRY_DELAY} Seconds\nRun Delay: {RUN_DELAY} Seconds')
    print(f'Fails: {error_total}')
    print(f'Accuracy: {round(100 * (asset_total / (asset_total + error_total)), 2)}%')
    print(f"Time: {formatted_time}")
    return len(all_mutual_addresses), len(global_stake_addresses), len(policy_ids), len(just_three)


def get_addresses_for_policy(policy_id, output_file):
    print(f'Getting Asset Names for PolicyID: {policy_id}')

    asset_start_time = time.time()
    assets = get_assets_for_policy(policy_id)

    asset_names = []
    for asset in assets:
        asset_names.append(asset["asset_name"])

    assest_count = len(asset_names)
    formatted_time = format_time(time.time() - asset_start_time)
    print(f'\n\nReturned: {len(asset_names)} Assets in {formatted_time}')

    urls = []
    for asset_name in asset_names: # create URLs for each asset_name
        urls.append(f"https://api.koios.rest/api/v0/asset_address_list?_asset_policy={policy_id}&_asset_name={asset_name}")

    print(f'\nGetting Addresses for Asset Names')
    address_start_time = time.time()

    addresses, errors = asyncio.run(make_requests(urls)) # run request

    payment_addresses = []
    for address in addresses:
        if "payment_address" in address:
            payment_addresses.append(address["payment_address"])
    burn_count = len(asset_names) - len(payment_addresses)

    #save list_address to .csv with filename policy_id
    df = pd.DataFrame({'Address List' : payment_addresses})
    df.to_csv(output_file, index=False, encoding='utf-8')

    formatted_time = format_time(time.time() - address_start_time)
    print(f'\n\nReturned: {len(addresses)} Addresses in {formatted_time}')
    print(f'Burned: {burn_count}')
    print(f'Failed: {errors}')
    print(f'Accuracy: {round(len(urls) / (errors + len(urls)) * 100, 2)}%')
    print(f'\nExported: "{policy_id}.csv"')
    print('---------------------------------------------------------------------------\n')
    return payment_addresses, burn_count, assest_count, errors


def get_assets_for_policy(policy_id):
    offset_start = 0
    assets = []
    while True:
        print(f'Scanning Indexes: {offset_start} - {offset_start + BATCH_OFFSET - 1}')

        urls = []
        for offset in range(offset_start, offset_start + BATCH_OFFSET, OFFSET_SIZE):
            urls.append(f"https://api.koios.rest/api/v0/asset_policy_info?_asset_policy={policy_id}&offset={offset}")

        output, errors = asyncio.run(make_requests(urls))
        assets += output

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
    batch_end = min(batch_start + BATCH_SIZE, len(urls))
    total_errors = 0
    output = []
    batch_done = []
    while True:
        if batch_start >= len(urls):
            break

        start_time = time.time()
        urls_slice = urls[batch_start: batch_end]

        async with aiohttp.ClientSession() as session:                
            results = await asyncio.gather(*[get_response(url, session, len(urls), batch_done) for url in urls_slice])
        batch_errors = 0
        for info, errors in results:
            output += info
            batch_errors += errors
        total_errors += batch_errors

        formatted_time = format_time(time.time() - start_time)
        print(
            f'\rBatch {batch_start+1}-{batch_end}: '
            f'{formatted_time}, '
            f'{batch_errors} Fails, '
            f'{round(100 * (1 - (batch_errors / (BATCH_SIZE+batch_errors))), 2)}% Accuracy',
        )
        print(f'\r{RUN_DELAY} Second Batch Delay', end='')
        time.sleep(RUN_DELAY)
        print('\r                                 ', end='')

        batch_start += BATCH_SIZE
        batch_end = min(batch_start + BATCH_SIZE, len(urls))

    return output, total_errors

async def get_response(url, session, len_urls, batch_done):
    for retry in range(RETRIES):
        try:
            async with session.get(url=url) as response:
                info = await response.json()
                batch_done.append(0)
                pct = (len(batch_done)/len_urls)*100
                print("\r{:.2f}%".format(pct), end="")
                return info, retry
        except Exception as e:
            await asyncio.sleep(RETRY_DELAY)
    print(f"Failed to get url {url} after {RETRIES} retries")
    return [], retry


if __name__ == "__main__":
    main()