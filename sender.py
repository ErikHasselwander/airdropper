from cmath import exp
from algosdk.v2client import algod
from algosdk.v2client import indexer
from algosdk.future import transaction
from time import sleep, time
import math
import private
import random


algod_address = 'https://mainnet-api.algonode.cloud'
indexer_adress = 'https://mainnet-idx.algonode.cloud'
alognode_token = ''

algo_client = algod.AlgodClient(alognode_token, algod_address, headers={'User-Agent': 'algosdk'})
algo_indexer = indexer.IndexerClient(alognode_token, indexer_adress, headers={'User-Agent': 'algosdk'})

from_address = private.account['address']
from_privatekey = private.account['private_key']

class parsed_tx():
    def __init__(self,sender,receiver,asaid,amount):
        self.sender = sender
        self.receiver = receiver
        self.asaid = asaid
        self.amount: float = amount
        self.group = ""
        self.optin = False
    def optin_check(self, accounts):
        if self.receiver in accounts:
            self.optin = True
            return self.optin
        account_info = algo_client.account_info(self.receiver)
        sleep(0.02) # To not get ratelimited by algonode.
        try:
            for x in account_info['assets']:
                if x['asset-id'] == self.asaid:
                    self.optin = True
                    return self.optin
        except:
            pass
        return self.optin

class tx_grp():
    def __init__(self):
        self.original_transactions = []
        self.transactions = []
        self.gid = None
        self.stx = []
    def add_og_tx(self,tx):
        self.original_transactions.append(tx)
    def add_transaction(self,tx):
        self.transactions.append(tx)
    def add_gid(self,gid):
        self.gid = gid
        for tx in self.transactions:
            tx.group = gid
    def sign_grp(self,key):
        for tx in self.transactions:
            self.stx.append(tx.sign(key))


def csv_reader(path):
    with open(path, 'r') as file:
        lines = file.read().splitlines()
    header = lines.pop(0)
    header = header.split(',')
    header.append('Group ID')
    transactions = []
    asas = {}

    for line in lines:
        line = line.split(',')
        if int(line[1]) not in asas:
            if int(line[1]) == 0:
                asas[int(line[1])] = {"decimals": 6}
            else:
                asas[int(line[1])] = {"decimals": algo_client.asset_info(int(line[1]))['params']['decimals']}
        try:
            transactions.append(parsed_tx(line[0], line[3], int(line[1]), int(float(line[2].replace('"', '')) * 10**asas[int(line[1])]["decimals"])))
        except Exception as err:
            print(f'Is {int(line[1])} a valid ASA? I couldn\'t load it. Maybe it\'s just a network error. Please rerun the script? Error is: {err}')
    return transactions, header, asas


def create_groups(transactions, txpergrp):
    txgrps = []
    while len(transactions):
        amount = min(txpergrp, len(transactions))
        params = algo_client.suggested_params()
        
        txgrp = tx_grp()
        for _ in range(amount):
            ctx: parsed_tx = transactions.pop(0)
            if ctx.asaid == 0:
                txgrp.add_transaction(transaction.PaymentTxn(ctx.sender,params,ctx.receiver,ctx.amount, note=str(time() + random.random())))
                txgrp.add_og_tx(ctx)
            else:
                txgrp.add_transaction(transaction.AssetTransferTxn(ctx.sender,params,ctx.receiver,ctx.amount,ctx.asaid,note=str(time() + random.random())))
                txgrp.add_og_tx(ctx)
        gid = transaction.calculate_group_id(txgrp.transactions)
        for tx in txgrp.transactions:
            tx.group = gid
        txgrp.add_gid(gid)
        txgrps.append(txgrp)
    return txgrps
        

def groups_to_csv(path,txgrps):
    with open(path, 'w') as file:
        for txgrp in txgrps:
            file.write(f'{txgrp.gid}\n')
            for tx in txgrp.transactions:
                tx = tx.__dict__
                if 'index' in tx:
                    tx["index"]
                    file.write(f'{tx["sender"]},{tx["index"]},{tx["amount"]},{tx["receiver"]}\n')
                else:
                    file.write(f'{tx["sender"]},0,{tx["amt"]},{tx["receiver"]}\n')


def check_optin_and_kick(transactions, header, asas):
    for asa in asas:
        if asa:
            asas[asa] = []
            accounts_with_app = algo_indexer.accounts(asset_id=asa, limit=1000)
            for account in accounts_with_app['accounts']:
                asas[asa].append(account['address'])
            
            while 'next-token' in accounts_with_app:
                accounts_with_app = algo_indexer.accounts(asset_id=asa, limit=1000, next_page=accounts_with_app['next-token'])
                for account in accounts_with_app['accounts']:
                    asas[asa].append(account['address'])


    validtxs = [tx for tx in transactions if not tx.asaid or tx.optin_check(asas[tx.asaid])]
    invalidtxs = [tx for tx in transactions if tx.asaid and not tx.optin_check(asas[tx.asaid])]
    if invalidtxs:
        with open('missing_optin.csv', 'w') as file:
                    file.write(str(header) + '\n')

        for tx in invalidtxs:
            with open('missing_optin.csv', 'a') as file:
                file.write(f'{tx.sender},{tx.asaid},{tx.amount},{tx.receiver}\n')

    return validtxs


def main():
    filepath = input('Input the filename of the .csv to read: ')
    transactions, header, asas = csv_reader(filepath)

    transactions = check_optin_and_kick(transactions, header, asas)

    txgrps = create_groups(transactions,private.GROUPSIZE)

    print('Writing transactions to "pending_transactions.csv" to file. Missing opt-ins can be found in "missing_optin.csv".')
    groups_to_csv('pending_transactions.csv',txgrps)

    if input('Do you want to sign these transactions? (y/n) ') != "y":
        print('Then that\'s all, cheers!')
        return
    print('Awesome. Commencing signage.')

    for txgrp in txgrps:
        txgrp.sign_grp(private.account['private_key'])

    if input('All groups signed without issue. Do you want to send these transactions? (y/n) ') != "y":
        print('Then that\'s all, cheers!')
        return
    for txgrp in txgrps:
        try:
            txid = algo_client.send_transactions(txgrp.stx)
            txgrp.txid = txid
            sleep(0.1)
        except Exception as err:
            txgrp.txid = f"FAILED with error {err}"

    print('All transactions signed and sent. Waiting 15 seconds and then checking status. All results will be printed to "final_output.csv"')
    sleep(15)
    with open('final_output.csv', 'w') as file:
        file.write('Group ID,status\n')
        
    failed_groups = []
    for txgrp in txgrps:
        try:
            tx_search = algo_indexer.search_transactions(txid=txgrp.txid)
            if txgrp.txid in tx_search['transactions'][0]['id']:
                with open('final_output.csv', 'a') as file:
                    file.write(f'{txgrp.gid},Success\n')
            else:
                with open('final_output.csv', 'a') as file:
                    file.write(f'{txgrp.gid},Failed\n')
                    failed_groups.append(txgrp.gid)
        except Exception as err:
            with open('final_output.csv', 'a') as file:
                file.write(f'{txgrp.gid},Failed with error {err}\n')
                failed_groups.append(txgrp.gid)
        sleep(0.1)

if __name__ == '__main__':
    main()