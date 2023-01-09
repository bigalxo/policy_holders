from report import get_assets_for_policy
from policies import policy_id_atsuko as policy_id
import os 


RUN_DELAY = 0
assets = get_assets_for_policy(policy_id)

for asset in assets:
    asset = asset['minting_tx_metadata']['json'][policy_id]
    asset_id = list(asset.keys())[0][-4:]
    details = list(asset.values())[0]
    
    print(details.keys())
    details.values()
    break

aramar = ['Golden Brown', 'Scared Grey', 'Undercut Short Blonde', 'None', 'ADA Ninjaz - Aramar #8279', 'Triple', [{'src': 'ipfs://QmeYe9CwC1RrmjtxxLmrVEFBsKactA8YcztmxW6nR29Mvf', 'name': 'ADA Ninjaz - Aramar #8279', 'mediaType': 'image/png'}], 'ipfs://QmeYe9CwC1RrmjtxxLmrVEFBsKactA8YcztmxW6nR29Mvf', 'Shout', 'None', 'Kusarigama Orange', 'Embroidered Jacket Yellow', 'Soju', 'None', 'None', 'image/png', 'Sun Paint Splash', 'None', 'None']