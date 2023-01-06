import time
import os
import math
from functools import reduce

import asyncio
import aiohttp
import pandas as pd
from pycardano import Address, Network

from policies import list_policy_id as list_policy_id


# asyncio params
BATCH_SIZE = 50 # Quantity of calls made concurrently
RUN_DELAY = 3 # Delay between runs
RETRY_DELAY = 2 # Delay between retries in seconds
RETRIES = 10 # Number of retries

# koios api params
OFFSET_SIZE = 1000
OFFSET_COUNT = 10
BATCH_OFFSET = OFFSET_SIZE * OFFSET_COUNT

def main():
    start_time = time.time()
    list_burned = [] # tracks how many assets are burned per policy_id
    total_asset_qty = 0 # tracks total of assets scanned
    sum_errors = 0 # tracks total of failed calls
    for policy_id in list_policy_id: # Write .csv, update vars
        file_name = os.path.join("outputs", f"{policy_id}.csv")
        burned, asset_qty, errors = get_addresses_for_policy(policy_id, file_name)
        list_burned.append(burned)
        total_asset_qty += asset_qty
        sum_errors += errors

    stake_addresses_unique = [] # List of unique Stake addresses across all policies
    stake_addresses_lists = [] # List of Stake addresses per policy_id
    for policy_id in list_policy_id: # Read .csv, update vars
        print(f'Deriving Stake Keys from Address List in {policy_id}')
        file_name = os.path.join("outputs", f"{policy_id}.csv")
        df = pd.read_csv(file_name)

        stake_addresses = [] # List of stake addresses for current policy_id
        for address_string in df["Address List"]: # Derive Stake key from address
            if len(address_string) == 103: # If address has Stake component
                primative_address = Address.from_primitive(address_string)
                address = Address(staking_part=primative_address.staking_part, network=Network.MAINNET)
                if str(address) not in stake_addresses: # If address is not a duplicate in current policy_id
                    stake_addresses.append(str(address))
                    if address not in stake_addresses_unique: # If address is not a duplicate across all policies
                        stake_addresses_unique.append(address)
            else: # If address has no stake component (No Stake Key to derive, treat unstaked addresses like a Stake Key)
                if address_string not in stake_addresses:
                    stake_addresses.append(address_string)
                    if address_string not in stake_addresses_unique:
                        stake_addresses_unique.append(address_string)

        stake_addresses_lists.append(stake_addresses)

    #convert stake_addresses_lists to satisfy "Stake keys holding all policies" 
    lists_as_sets = [set([str(a) for a in l]) for l in stake_addresses_lists]
    all_policies = reduce(lambda s1, s2: s1.intersection(s2), lists_as_sets)
    qty_all_policies = len(all_policies) 


    formatted_time = format_time(time.time() - start_time)
    print('\n---------------------------------------------------------------------------\n')
    print('Report')
    for i in range(len(list_policy_id)):
        print(
            f"\nPolicyID: {list_policy_id[i]}"
            f"\nHolders: {len(stake_addresses_lists[i])}"
            f"\nBurned: {list_burned[i]}"
        )
    print(f'\n{qty_all_policies} stake keys holding all {len(list_policy_id)} policies')
    print(f'{len(stake_addresses_unique)} unique holders across all {len(list_policy_id)} sets')
    print(f'Batch Size: {BATCH_SIZE}\nRetry Delay: {RETRY_DELAY} Seconds\nRun Delay: {RUN_DELAY} Seconds')
    print(f'Fails: {sum_errors}')
    print(f'Accuracy: {round(100*(1 - (sum_errors/(total_asset_qty+sum_errors))), 2)}%')
    print(f"Time: {formatted_time}")



def get_addresses_for_policy(policy_id, output_file):
    print(f'Getting Asset Names for PolicyID: {policy_id}')

    asset_start_time = time.time()
    assets = get_assets_for_policy(policy_id)

    asset_names = []
    for asset in assets:
        asset_names.append(asset["asset_name"])
    asset_qty = len(asset_names)
    formatted_time = format_time(time.time() - asset_start_time)
    print(f'\n\nReturned: {len(asset_names)} Assets in {formatted_time}')

    urls = []
    for asset_name in asset_names: # create URLs for each asset_name
        urls.append(f"https://api.koios.rest/api/v0/asset_address_list?_asset_policy={policy_id}&_asset_name={asset_name}")

    
    print(f'\nGetting Addresses for Asset Names')
    time.sleep(RUN_DELAY)
    address_start_time = time.time()
    
    addresses, errors = asyncio.run(make_requests(urls)) # run request

    payment_addresses = []
    for address in addresses:
        if address:
            payment_addresses.append(address["payment_address"])
    burned = (len(asset_names)-len(payment_addresses))

    #save list_address to .csv with filename policy_id
    df = pd.DataFrame({'Address List' : payment_addresses})
    df.to_csv(output_file, index=False, encoding='utf-8')

    formatted_time = format_time(time.time() - address_start_time)
    print(f'\n\nReturned: {len(addresses)} Addresses in {formatted_time}')
    print(f'Burned: {burned}')
    print(f'Failed: {errors}')
    print(f'Accuracy: {round(1-(errors/(errors+len(urls)))*100,2)}%')
    print(f'\nExported: "{policy_id}.csv"')
    print('---------------------------------------------------------------------------\n')
    return burned, asset_qty, errors


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
        time.sleep(RUN_DELAY)

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
        except Exception:
            await asyncio.sleep(RETRY_DELAY)
    print(f"Failed to get url {url} after {RETRIES} retries")
    return [], retry
            



if __name__ == "__main__":
    main()
