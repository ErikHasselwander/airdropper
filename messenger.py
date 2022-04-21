from algosdk.v2client import algod
from algosdk.v2client import indexer
from algosdk.future import transaction
from time import sleep
import private


algod_address = 'http://mainnet-api.algonode.cloud'
indexer_adress = 'https://algoindexer.algoexplorerapi.io' # get_accounts_holding_asa does not work with algonode for some reason... :(
alognode_token = ''

algo_client = algod.AlgodClient(alognode_token, algod_address, headers={'User-Agent': 'algosdk'})
algo_indexer = indexer.IndexerClient(alognode_token, indexer_adress, headers={'User-Agent': 'algosdk'})

from_address = private.account['address']
from_privatekey = private.account['private_key']

def get_accounts_holding_asa(asa):
    accounts = []
    accounts_with_app = algo_indexer.accounts(asset_id=asa, limit=1000, exclude='all')
    for account in accounts_with_app['accounts']:
        accounts.append(account['address'])
    
    while 'next-token' in accounts_with_app:
        accounts_with_app = algo_indexer.accounts(asset_id=asa, limit=1000, next_page=accounts_with_app['next-token'], exclude='all')
        sleep(0.005)
        for account in accounts_with_app['accounts']:
            accounts.append(account['address'])

    return accounts

def create_groups(accounts, asa, note):
    txgrps = []
    while len(accounts):
        amount = min(private.GROUPSIZE, len(accounts))
        print(amount)
        params = algo_client.suggested_params()
        txgrp = []
        for i in range(amount):
            
            if asa == 0:
                ctx = transaction.PaymentTxn(private.account['address'],params,accounts.pop(0),0, note=note)
            else:
                ctx = transaction.AssetTransferTxn(private.account['address'],params,accounts.pop(0),0,asa, note=note)

            txgrp.append(ctx)
            print(len(txgrp))
        gid = transaction.calculate_group_id(txgrp)
        stx = []
        for tx in txgrp:
            tx.group = gid
            stx.append(tx.sign(private.account['private_key']))
        txgrps.append(stx)
    return txgrps

def messenger(asa, note):
    accounts = get_accounts_holding_asa(asa)
    ans = input(f'{len(accounts)} accounts loaded. Do you wish to send a 0 amt tx with the note {note} to all of them? y/n ')
    if ans.lower() != "y":
        return
    txgrps = create_groups(accounts, asa, note)

    txids = []
    for txgrp in txgrps:
        try:
            txid = algo_client.send_transactions(txgrp)
            txids.append(txid)
            sleep(0.1)
        except Exception as err:
            txids.append(f"FAILED with error {err}")
    
    print('All transactions signed and sent. Waiting 15 seconds and then checking status. All results will be printed to "final_output.csv"')
    sleep(10)
    with open('final_output.csv', 'w') as file:
        file.write('Group ID,status\n')
        
    for txid in txids:
        try:
            tx_search = algo_indexer.search_transactions(txid=txid)
            if txid in tx_search['transactions'][0]['id']:
                with open('final_output.csv', 'a') as file:
                    file.write(f'{txid},Success\n')
            else:
                with open('final_output.csv', 'a') as file:
                    file.write(f'{txid},Failed\n')
        except Exception as err:
            with open('final_output.csv', 'a') as file:
                file.write(f'{txid},Failed with error {err}\n')
        sleep(0.1)

def main():
    messenger(ASAID_HERE_AS_INT, "ENTER YOUR NOTE HERE") # Ex: messenger(557977043, "sorry dudes just testing")

if __name__ == '__main__':
    main()