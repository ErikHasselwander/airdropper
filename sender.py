from algosdk.v2client import algod
from algosdk.v2client import indexer
from algosdk.future.transaction import AssetTransferTxn
from algosdk.future.transaction import assign_group_id
from time import sleep, time
import private
import random


algod_address = 'http://mainnet-api.algonode.cloud'
indexer_adress = 'http://mainnet-idx.algonode.cloud'
alognode_token = ''

algo_client = algod.AlgodClient(alognode_token, algod_address, headers={'User-Agent': 'algosdk'})
algo_indexer = indexer.IndexerClient(alognode_token, indexer_adress, headers={'User-Agent': 'algosdk'})

from_address = private.account['address']
from_privatekey = private.account['private_key']

def sign_txn_grp(txngrp, sk):
    return [x.sign(sk) for x in txngrp]

def sender(path):
    asa = 700965019
    with open(path, 'r') as file:
        lines = file.read().splitlines()

    transactions = []
    for line in lines:
        line = line.split(';')
        transactions.append([line[0], int(float(line[1])*10**6)])
    
    accounts_opted_in = []
    accounts_with_app = algo_indexer.accounts(asset_id=asa, limit=1000)
    for account in accounts_with_app['accounts']:
        accounts_opted_in.append(account['address'])
    
    while 'next-token' in accounts_with_app:
        accounts_with_app = algo_indexer.accounts(asset_id=asa, limit=1000, next_page=accounts_with_app['next-token'])
        sleep(0.005)
        for account in accounts_with_app['accounts']:
            accounts_opted_in.append(account['address'])
    
    valid_accs = []    
    for tx in transactions:
        if tx[0] in accounts_opted_in:
            valid_accs.append(tx)
    txgrps = []
    sp = algo_client.suggested_params()

    if len(valid_accs) > 15:
        txgrp = []
        for tx in valid_accs[0:16]:
            txgrp.append(AssetTransferTxn(from_address, sp, tx[0], tx[1], asa))
        txgrp = assign_group_id(txgrp)
        txgrps.append(txgrp)
    else:
        txgrp = []
        for tx in valid_accs:
            txgrp.append(AssetTransferTxn(from_address, sp, tx[0], tx[1], asa))
        txgrp = assign_group_id(txgrp)
        txgrps.append(txgrp)
    
    for txgrp in txgrps:
        txgrp = sign_txn_grp(txgrp, from_privatekey)
        algo_client.send_transactions(txgrp)
        sleep(0.005)

if __name__ == '__main__':
    sender('test.csv', )