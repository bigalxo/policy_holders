from addresses import *
start = time.time()

## INPUT ##
#Input: list of policy IDs
list_policy_id = list_policy_id_test # see addresses.py

errors = []
run_errors = []
urls = [] # def aiohttp and asyncio
output = [] # def aiohttp and asyncio
list_burned = [] # counts how many burns in each policy
list_asset_qty = []

# Tweak to optimise asyncio efficiency
request_size = 50 # how many calls can be made at once
delay = 3 # Delay between retries in seconds
run_delay = 3 # wait when one run finished before starting the next
retries = 10 # Number of retries
print(f'\n---------------------------------------------------------------------------')
async def main(urls):
    runs = math.ceil(len(urls)/request_size)
    counter = 0
    for i in range (runs):
        run_errors.append(len(errors))
        run_start = time.time()
        urls_slice = urls[counter:(i+1)*request_size]
        counter += request_size
        async with aiohttp.ClientSession() as session:
            await asyncio.gather(*[get(url, session, errors) for url in urls_slice])
        if i != runs-1:
            await asyncio.sleep(run_delay)
        run_end = time.time()
        total_time = run_end - run_start
        formatted_time = format_time(total_time)
        print(f' Last run: {formatted_time}, {len(errors) - run_errors[-1]} Failed Requests, {len(errors)} Total Failed Requests, {round(100*(1 - (len(errors)/(len(output)+len(errors)))), 2)}% Accuracy   ', end="")

async def get(url, session, errors):
    for i in range(retries):
        try:
            async with session.get(url=url) as response:
                info = await response.json()
                output.append(info)
                print(f'\r{len(output)/len(urls)*100:.2f}%', end='')
                break
        except Exception as e:
            errors.append(0)
            if i < retries - 1:  # Not the last retry
                await asyncio.sleep(delay)
            else:  # Last retry
                print("\rFailed to get url {} after {} retries".format(url, retries))

#Koios
#Input: list_policy_id
#Output: list_asset_names
for policy_id in list_policy_id:
    time_assets_start = time.time()
    #reset arrays for new policy_id
    list_asset_names = []
    offset = 0 #counts offset for pagination
    offset_counter = 10 #limits 10 offset pagination requests at a time
    scanned_counter = 0 
    print(f'PolicyID: {policy_id}\n')
    print('Getting Asset Names')
    while True:
        #reset arrays for new request
        urls = []
        output = []
        print(f'\rScanning Index: {offset+1}-{offset+10000}')
        for i in range(offset_counter-10, offset_counter):#create URLs for 10 offsets
            urls.append("https://api.koios.rest/api/v0/asset_policy_info?_asset_policy={}&offset={}".format(policy_id, offset))
            offset += 1000
        asyncio.run(main(urls)) #run 10 requests, return output
        for i in range(0,len(output)): 
            scanned_counter += len(output[i])
            for j in range(0,len(output[i])):
                list_asset_names.append(output[i][j]["asset_name"])
        list_asset_qty.append(len(list_asset_names))
        if scanned_counter % 10000 == 0: # if return was exactly 10,000, assume more than 10,000 and retry for 10,001-20,000
            offset_counter += 10
            continue
        else: # all asset_names have been collected, find assosiated addresses
            time_assets_end = time.time()
            total_time = round((time_assets_end - time_assets_start), 2)
            formatted_time = format_time(total_time)
            print(f'\n\nReturned: {scanned_counter} Assets in {formatted_time}')
            print(f'\rTotal Asset Names: {len(list_asset_names)}')
            #reset arrays for new request
            urls = [] 
            output = []
            list_address = []
            for i in range(0,len(list_asset_names)): # create URLs for each asset_name
                if list_asset_names[i]:                    
                    urls.append("https://api.koios.rest/api/v0/asset_address_list?_asset_policy="+policy_id+"&_asset_name=" + list_asset_names[i])
            time_addresses_start = time.time()
            print(f'\nGetting Addresses for Asset Names')
            time.sleep(2)
            result = asyncio.run(main(urls)) # run request
            for i in range(0,len(output)):
                if output[i]:
                    list_address.append(output[i][0]["payment_address"])
            list_burned.append(len(list_asset_names)-len(list_address))
            #save list_address to .csv with filename policy_id
            df = pd.DataFrame ({'Address List' : list_address})
            df.to_csv(policy_id + '.csv', index=False, encoding='utf-8')
            time_addresses_end = time.time()
            total_time = round((time_addresses_end - time_addresses_start), 2)           
            formatted_time = format_time(total_time)
            print(f'\n\nReturned: {len(list_address)} Addresses in {formatted_time}')
            print(f'Burned: {list_burned[-1]}')
            print(f'\nExported: "{policy_id}.csv"')
            print('---------------------------------------------------------------------------\n')
            break
            

list_get_all = [] # [ [], [], [], [] ] one list appended for each set
list_unique = [] # stake keys with no duplicates
for policy_id in list_policy_id:
    a = pd.read_csv(policy_id+'.csv')
    b = a.to_dict()
    stake = []
    print(f'Deriving Stake Keys from Address List in {policy_id}')
    for i in range(0,len(b['Address List'])):
        c = b['Address List'][i]
        if len(c) == 103:
            addr = Address.from_primitive(c)
            addr2 = Address(staking_part=addr.staking_part, network=Network.MAINNET)
            if addr2 not in stake:
                stake.append(addr2)
                if addr2 not in list_unique:
                    list_unique.append(addr2)
        else:
            if c not in stake:
                stake.append(c)
                if c not in list_unique:
                    list_unique.append(c)
    list_get_all.append(stake)

#get stake keys holding all policies
sets = [set([str(a) for a in l]) for l in list_get_all] # Convert the lists to sets
intersection = reduce(lambda s1, s2: s1.intersection(s2), sets) # Find the intersection of all the sets
num_elements = len(intersection) # Find the number of elements in the intersection

#get time from start to finish
end = time.time()
total_time = round((end - start), 2)
formatted_time = format_time(total_time)
print('\n---------------------------------------------------------------------------\n')
print('Report')
for i in range (len(list_get_all)):
    print(f'\nPolicyID: {list_policy_id[i]}\nAssets: {list_asset_qty[i]}\nHolders: {len(list_get_all[i])}\nBurned: {list_burned[i]}')
print(f'\n{num_elements} stake keys holding all {len(list_policy_id)} policies')
print(f'{len(list_unique)} unique holders across all {len(list_policy_id)} sets')
print(f'Request Size: {request_size}\nRetry Delay: {delay} Seconds\nRun Delay: {run_delay} Seconds')
print(f'Failed Requests: {len(errors)}')
print(f'Accuracy: {round(100*(1 - (len(errors)/(sum(list_asset_qty)+len(errors)))), 2)}%')
print(f"Total Time: {formatted_time}")

print(len(stake))
print(len(list_unique))