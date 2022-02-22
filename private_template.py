from algosdk import mnemonic
MNEMINOC = "your mnemoic here"

account = {
    'address': mnemonic.to_public_key(MNEMINOC),
    'private_key': mnemonic.to_private_key(MNEMINOC),
}