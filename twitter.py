from report import main as report
from keys import API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET
import tweepy
import requests
import json
from policies import policies


# Danketsu
UP = "\u25B2"
DOWN = "\u25BC"
ADA = "\u20B3"
SIGNOFF = "IKUZO! \U0001F977 \U0001F5E1"


def main():
    mutual_stake_addresses, global_stake_addresses, len_policy_ids, just_three = report() # Run report
    populate_floor_prices(policies) # grab floor prices
    mutual_change, global_change, three_change = calculate_changes(mutual_stake_addresses, global_stake_addresses, just_three, policies) # Get Daily change

    tweet_string = build_tweet(policies, mutual_stake_addresses, global_stake_addresses, len_policy_ids, just_three, mutual_change, global_change, three_change)
    tweet(tweet_string)


def build_tweet(policies, mutual_stake_addresses, global_stake_addresses, len_policy_ids, just_three, mutual_change, global_change, three_change):
    policy_report_string = ""
    for policy in policies:
        policy_report_string += f'{policy["name"]}: {policy["floor_price"]}{ADA}  {policy["change"]}{ADA}\n'

    tweet_string = (
        f'TESTING Daily Report:\n'
        f'\n'
        f'Floors:\n'
        f'{policy_report_string}'
        f'\n'
        f'{just_three} Ninjaz holding (Aramar,Atsuko,Daisuke) {three_change}\n'
        f'{mutual_stake_addresses} Ninjaz holding all {len_policy_ids}  {mutual_change}\n'
        f'{global_stake_addresses} unique holders across {len_policy_ids}  {global_change}\n'
        f'\n'
        f'{SIGNOFF}'
    )

    return tweet_string


def populate_floor_prices(policies):
    for policy in policies:
        policy_id = policy["id"]
        url = f'https://api.opencnft.io/1/policy/{policy_id}/floor_price'
        response = requests.get(url)
        info = json.loads(response.content)
        floor = int(info['floor_price'] / 1000000)
        policy["floor_price"] = floor


def calculate_changes(mutual_stake_addresses, global_stake_addresses, just_three, policies): # Calculate daily change 
    with open("outputs/yesterday.txt", "r") as file:
        yesterdays = list(map(int, file.read().split()))
        read_policy_yesterdays(yesterdays, policies)
        mutual_yesterday, global_yesterday, three_yesterday = read_stats_yesterdays(yesterdays)
    
    write_yesterdays(mutual_stake_addresses, global_stake_addresses, just_three, policies)

    mutual_change = change_string(mutual_stake_addresses - mutual_yesterday)
    global_change = change_string(global_stake_addresses - global_yesterday)
    three_change = change_string(just_three - three_yesterday)
    for policy in policies:
        policy["change"] = change_string(policy["floor_price"] - policy["yesterday"])

    return mutual_change, global_change, three_change


def read_policy_yesterdays(yesterdays, policies):
    # Get yesterdays stats
    for i, policy in enumerate(policies):
        yesterday = yesterdays[i + 3]
        policy["yesterday"] = yesterday


def read_stats_yesterdays(yesterdays):
    # Get yesterdays stats
    mutual_yesterday = yesterdays[0]
    global_yesterday = yesterdays[1]
    three_yesterday = yesterdays[2]
    return mutual_yesterday, global_yesterday, three_yesterday


def write_yesterdays(mutual_stake_addresses, global_stake_addresses, just_three, policies):
    # Store for tomorrow
    policy_floors = ' '.join([policy["floor_price"] for policy in policies])
    with open("outputs/yesterday.txt", "w") as file:
        file.write(f'{mutual_stake_addresses} {global_stake_addresses} {just_three} {policy_floors}')


def change_string(value):
    if value == 0:
        return "-"

    if value > 0:
        return f'{UP}{value}'
    else:
        return f'{DOWN}{abs(value)}'


def tweet(text):
    auth = tweepy.OAuth1UserHandler(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET)
    api = tweepy.API(auth)
    api.update_status(text)

if __name__ == "__main__":
    main()
