from report import main as report
from keys import API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET
import tweepy

# Danketsu
UP = "\u25B2"
DOWN = "\u25BC"
SIGNOFF = "IKUZO! \U0001F977 \U0001F5E1"

def main():
    mutual_stake_addresses, global_stake_addresses, policy_ids = 181, 4013, 4 # Run report
    mutual_change, global_change = change(mutual_stake_addresses, global_stake_addresses) # Get Daily change
    tweet('Daily Report:\n\n'
    f'{mutual_stake_addresses} Ninjaz holding all {policy_ids} policies {mutual_change}\n'
    f'{global_stake_addresses} unique holders across {policy_ids} Sets {global_change}\n\n'
    f'{SIGNOFF}'
    )

def change(mutual_stake_addresses, global_stake_addresses): # Calculate daily change 
    # Get yesterdays stats
    with open("outputs/yesterday.txt", "r") as f:
        mutual_yesterday, global_yesterday = map(int, f.read().split())

    # Store for tomorrow
    with open("outputs/yesterday.txt", "w") as f:
        f.write(str(mutual_stake_addresses) + " " + str(global_stake_addresses))
    mutual_change = mutual_stake_addresses - mutual_yesterday
    global_change = global_stake_addresses - global_yesterday

    #Assign up down, or no change
    if mutual_change == 0:
        mutual_change = ""
    else:
        if mutual_change > 0:
            mutual_change = f'{UP}{mutual_change}'
        else:
            if mutual_change < 0:
                mutual_change = f'{DOWN}{abs(mutual_change)}'

    if global_change == 0:
        global_change = ""
    else:
        if global_change > 0:
            global_change = f'{UP}{global_change}'
        else:
            if global_change < 0:
                global_change = f'{DOWN}{abs(global_change)}'
    
    return mutual_change, global_change

def tweet(text):
    auth = tweepy.OAuth1UserHandler(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET)
    api = tweepy.API(auth)
    api.update_status(text)

if __name__ == "__main__":
    main()
