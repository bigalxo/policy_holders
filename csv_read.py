from addresses import *
start = time.time()

## INPUT ##
#list of policy_ids with assosiated .csv files
list_policy_id = list_policy_id # see addresses.py

list_all_policies = [] # [ [], [], [], [] ] one list appended for each set
list_unique = [] # stake keys with no duplicates

for policy_id in list_policy_id:
    a = pd.read_csv(policy_id+'.csv')
    b = a.to_dict()
    list_stake = []
    print(f'Deriving Stake Keys from Address List in {policy_id}')
    for i in range(0,len(b['Address List'])):
        c = b['Address List'][i]
        if len(c) == 103:
            addr = Address.from_primitive(c)
            addr2 = Address(staking_part=addr.staking_part, network=Network.MAINNET)
            if addr2 not in list_stake:
                list_stake.append(addr2)
                if addr2 not in list_unique:
                    list_unique.append(addr2)
        else:
            if c not in list_stake:
                list_stake.append(c)
                if c not in list_unique:
                    list_unique.append(c)
    list_all_policies.append(list_stake)


for i in range (len(list_all_policies)):
    print(f'\nPolicy: {list_policy_id[i]}\nHolders: {len(list_all_policies[i])}')

# Convert the lists to sets
sets = [set([str(a) for a in l]) for l in list_all_policies]

# Find the intersection of all the sets
intersection = reduce(lambda s1, s2: s1.intersection(s2), sets)

# Find the number of elements in the intersection
num_elements = len(intersection)

print(f'\n{num_elements} stake keys hold all {len(list_policy_id)} policies')
print(f'{len(list_unique)} unique holders across all {len(list_policy_id)} sets')
end = time.time()
print(f'\n{round(end-start,2)} Seconds')