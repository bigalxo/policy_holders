from addresses import *
start = time.time()

## INPUT ##
#Input: list of policy IDs
list_policy_id = list_policy_id_test # see addresses.py

#def aiohttp and asyncio
urls = []
output = []
limit = 50 # how many calls can be made at once
retries = 10 # Number of retries
delay = 10 # Delay between retries in seconds
async def main(urls):
    runs = math.ceil(len(urls)/limit)
    counter = 0
    for i in range (runs):
        urls_slice = urls[counter:(i+1)*limit]
        counter += limit
        async with aiohttp.ClientSession() as session:
            ret = await asyncio.gather(*[get(url, session) for url in urls_slice])

async def get(url, session):
    for i in range(retries):
        try:
            async with session.get(url=url) as response:
                info = await response.json()
                output.append(info)
                print("\r                                         \r{:.2f}%".format(len(output)/len(urls)*100), end="")
                break
        except Exception as e:
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
    list_burned = []
    offset = 0 #counts offset for pagination
    offset_counter = 10 #limits 10 offset pagination requests at a time
    scanned_counter = 0 
    print(f'PolicyID: {policy_id}')
    while True:
        #reset arrays for new request
        urls = []
        output = []
        print(f'\rScanning Index: {offset+1}-{offset+10000}')
        for i in range(offset_counter-10, offset_counter):#create URLs for 10 offsets
            urls.append("https://api.koios.rest/api/v0/asset_policy_info?_asset_policy={}&offset={}".format(policy_id, offset))
            offset += 1000
        result = asyncio.run(main(urls)) #run 10 requests, return output
        for i in range(0,len(output)): 
            scanned_counter += len(output[i])
            for j in range(0,len(output[i])):
                list_asset_names.append(output[i][j]["asset_name"])
        
        if scanned_counter % 10000 == 0: # if return was exactly 10,000, assume more than 10,000 and retry for 10,001-20,000
            offset_counter += 10
            continue
        else: # all asset_names have been collected, find assosiated addresses
            time_assets_end = time.time()
            print(f'\r         \nReturned: {scanned_counter} Assets in {round(time_assets_end-time_assets_start,2)} seconds')
            print(f'\rTotal Asset Names: {len(list_asset_names)}')
            #reset arrays for new request
            urls = [] 
            output = []
            address_list = []
            for i in range(0,len(list_asset_names)): # create URLs for each asset_name
                if list_asset_names[i]:                    
                    urls.append("https://api.koios.rest/api/v0/asset_address_list?_asset_policy="+policy_id+"&_asset_name=" + list_asset_names[i])
            time_addresses_start = time.time()
            print(f'\nGetting Addresses for Asset Names\nRequest Size: {limit}\nRetry Delay: {delay} Seconds\nRetries: {retries}')
            result = asyncio.run(main(urls)) # run request
            for i in range(0,len(output)):
                if output[i]:
                    address_list.append(output[i][0]["payment_address"])
            print(f'\r          \nBurned: {len(list_asset_names)-len(address_list)}')
            #save address_list to .csv with filename policy_id
            df = pd.DataFrame ({'Address List' : address_list})
            df.to_csv(policy_id + '.csv', index=False, encoding='utf-8')
            time_addresses_end = time.time()
            print(f'Returned: {len(address_list)} Addresses in {round(time_addresses_end-time_addresses_start,2)} seconds')
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
print('\n---------------------------------------------------------------------------\n')
print('Report')
for i in range (len(list_get_all)):
    print("\npolicy: "+list_policy_id[i]+"\nholders: "+str(len(list_get_all[i])))

# Convert the lists to sets
sets = [set([str(a) for a in l]) for l in list_get_all]

# Find the intersection of all the sets
intersection = reduce(lambda s1, s2: s1.intersection(s2), sets)

# Find the number of elements in the intersection
num_elements = len(intersection)

print(f'\n{num_elements} stake keys holding all {len(list_policy_id)} policies')
print(f'{len(list_unique)} unique holders across all {len(list_policy_id)} sets')



end = time.time()
print(f'\nTotal Time: {round(end-start,2)} Seconds')