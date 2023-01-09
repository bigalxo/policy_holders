from report import main as report
from keys import API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET
import tweepy
import requests
import json
from policies import policy_ids

# Danketsu
UP = "\u25B2"
DOWN = "\u25BC"
ADA = "\u20B3"
SIGNOFF = "IKUZO! \U0001F977 \U0001F5E1"

def main():
    mutual_stake_addresses, global_stake_addresses, len_policy_ids, just_three = report() # Run report
    aramar_floor, atsuko_floor, daisuke_floor, fourth_floor =  floor() # grab floor prices
    mutual_change, global_change, aramar_change, atsuko_change, daisuke_change, fourth_change, three_change = change(mutual_stake_addresses, global_stake_addresses, aramar_floor, atsuko_floor, daisuke_floor, fourth_floor, just_three) # Get Daily change
    
    tweet(
    f'Daily Report:\n'
    f'\n'
    f'Floors:\n'
    f'Aramar: {atsuko_floor}{ADA}  {aramar_change}{ADA}\n'
    f'Atsuko: {aramar_floor}{ADA}  {atsuko_change}{ADA} \n'
    f'Daisuke: {daisuke_floor}{ADA}  {daisuke_change}{ADA}\n'
    f'Fourth: {fourth_floor}{ADA}  {fourth_change}{ADA}\n'
    f'\n'
    f'{just_three} Ninjaz holding (Aramar,Atsuko,Daisuke) {three_change}\n'
    f'{mutual_stake_addresses} Ninjaz holding all {len_policy_ids}  {mutual_change}\n'
    f'{global_stake_addresses} unique holders across {len_policy_ids}  {global_change}\n'
    f'\n'
    f'{SIGNOFF}'
    )



def floor(): 
    a = []
    for policy_id in policy_ids:
        url = f'https://api.opencnft.io/1/policy/{policy_id}/floor_price'
        response = requests.get(url)
        info = json.loads(response.content)
        floor = int(info['floor_price']/1000000)
        a.append(floor)
    return a[0], a[1], a[2], a[3]


def change(mutual_stake_addresses, global_stake_addresses, aramar_floor, atsuko_floor, daisuke_floor, fourth_floor, just_three): # Calculate daily change 
    # Get yesterdays stats
    with open("outputs/yesterday.txt", "r") as f:
        mutual_yesterday, global_yesterday, aramar_yesterday, atusko_yesterday, daisuke_yesterday, fourth_yesterday, three_yesterday = map(int, f.read().split())
    # Store for tomorrow
    with open("outputs/yesterday.txt", "w") as f:
        f.write(f'{mutual_stake_addresses} {global_stake_addresses} {aramar_floor} {atsuko_floor} {daisuke_floor} {fourth_floor} {just_three}')
    mutual_change = change_string(mutual_stake_addresses - mutual_yesterday)
    global_change = change_string(global_stake_addresses - global_yesterday)
    aramar_change = change_string(aramar_floor - aramar_yesterday)
    atsuko_change = change_string(atsuko_floor - atusko_yesterday)
    daisuke_change = change_string(daisuke_floor - daisuke_yesterday)
    fourth_change = change_string(fourth_floor - fourth_yesterday)
    three_change = change_string(just_three - three_yesterday)
    
    return mutual_change, global_change, aramar_change, atsuko_change, daisuke_change, fourth_change, three_change

def change_string(value):
    if value == 0:
        value = "-"
    else:
        if value > 0:
            value = f'{UP}{value}'
        else:
            if value < 0:
                value = f'{DOWN}{abs(value)}'
    return value   

def tweet(text):
    auth = tweepy.OAuth1UserHandler(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET)
    api = tweepy.API(auth)
    api.update_status(text)

if __name__ == "__main__":
    main()
