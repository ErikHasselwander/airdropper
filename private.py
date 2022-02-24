from algosdk import mnemonic
from algosdk import account
# THIS IS WHERE YOU CHANGE UR MNEMONIC
MNEMINOC = "Enter your mnemonic here, space seperated without commas/numbers/dots."




# IGNORE EVERYTHING BELOW THIS
if MNEMINOC == "Enter your mnemonic here, space seperated without commas/numbers/dots.":
    private_key, address = account.generate_account()
    account = {
        'address': address,
        'private_key': private_key,
    }
else:
    account = {
        'address': mnemonic.to_public_key(MNEMINOC),
        'private_key': mnemonic.to_private_key(MNEMINOC),
    }