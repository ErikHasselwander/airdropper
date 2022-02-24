from algosdk import mnemonic
from algosdk import account
# THIS IS WHERE YOU CHANGE UR MNEMONIC
MNEMINOC = "Enter your mnemonic here, space seperated without commas/numbers/dots."
GROUPSIZE = 16  # This should be a value between 2 and 16. Maybe 1 works too. Higher is generally better, since they get sent out faster.
                # However; If one transaction in a group fails the entire group fails, so this might take some tuning based on the results you are seeing.


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