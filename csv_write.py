from addresses import *
start = time.time()

## INPUT ## 
# this function writes one csv at a time given as policy_id
policy_id = policy_id_small # see addresses.py


async def get(url, session):
    retries = 10  # Number of retries
    delay = 10  # Delay between retries in seconds
    for i in range(retries):
        try:
            async with session.get(url=url) as response:
                info = await response.json()
                if not info:
                    raise Exception
                output.append(info)
                print("\r{:.2f}%".format(len(output)/len(urls)*100), end="")
                break
        except Exception as e:
            if i < retries - 1:  # Not the last retry
                await asyncio.sleep(delay)
            else:  # Last retry
                print("\rFailed to get url {} after {} retries\n".format(url, retries))
async def main(urls):
    runs = math.ceil(len(urls)/50)
    counter = 0
    for i in range (runs):
        urls_slice = urls[counter:(i+1)*50]
        counter += 50
        async with aiohttp.ClientSession() as session:
            ret = await asyncio.gather(*[get(url, session) for url in urls_slice])

def get_asset_id(policy_id):
    offset = 0
    list_asset_name = [] 
    list_burned = []
    while True:
        url = "https://api.koios.rest/api/v0/asset_policy_info?_asset_policy={}&offset={}".format(policy_id, offset)
        print(f'Scanning Index: {offset+1}-{offset+1000}')
        info = requests.get(url)
        asset_policy_info = json.loads(info.content)
        for i in range(0,len(asset_policy_info)):
            if int(asset_policy_info[i]['total_supply']) == 0:
                list_burned.append(asset_policy_info[i]["asset_name"])
                continue
            else:
                list_asset_name.append(asset_policy_info[i]["asset_name"])
        offset += 1000
        if len(asset_policy_info) < 1000:
            print(f'Total: {len(list_asset_name)}')
            if len(list_burned) > 0:
                print(f'{len(list_burned)} AssetIDs are burned or do not have an assosiated address')
            break
    return policy_id, list_asset_name


print(f'PolicyID: {policy_id}')
urls = []
output = []

policy_id, list_asset_name = get_asset_id(policy_id)

for i in range(0,len(list_asset_name)):
    if list_asset_name[i]:
        urls.append("https://api.koios.rest/api/v0/asset_address_list?_asset_policy="+policy_id+"&_asset_name=" + list_asset_name[i])

print('Finding Addresses holding asssets')
result = asyncio.run(main(urls))
address_list = []
for i in range(0,len(output)):
    address_list.append(output[i][0]["payment_address"])

df = pd.DataFrame ({'Address List' : address_list})
df.to_csv(policy_id + '.csv', index=False, encoding='utf-8')
print(f'\nExported Address List as "{policy_id}.csv"')
end = time.time()
print(f'{round(end-start,2)} Seconds')