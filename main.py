import json
import time
from datetime import datetime
from web3 import Web3
from eth_account import Account
from colorama import Fore, init

# Initialize colorama
init(autoreset=True)

RPC_URL = "https://rpc-testnet.haust.app"
CHAIN_ID = 1523903251
PRIVATE_KEY = "hehe"
TOKEN_AMOUNT = Web3.to_wei(0.001, 'ether')  # Amount to send to each wallet
WALLET_FILE = "wallets.json"
SUCCESS_FILE = "success.txt"

# Web3 instance
web3 = Web3(Web3.HTTPProvider(RPC_URL))
account = Account.from_key(PRIVATE_KEY)

# Banner and basic info
hehe = r'''
 _   _                 _     _   _ _____ _____  
| | | | __ _ _   _ ___| |_  | \ | |  ___|_   _| 
| |_| |/ _ | | | / __| __| |  \| | |_    | |   
|  _  | (_| | |_| \__ \ |_  | |\  |  _|   | |   
|_| |_|\__,_|\__,_|___/\__| |_| \_|_|     |_|   
'''
print(Fore.GREEN + hehe + Fore.RESET)
print(f"\U0001F680 Connected to Haust Testnet RPC: {RPC_URL}")
print(f"\U0001F511 Using wallet: {account.address}")

# Function to get balance of an address
def get_balance(address):
    balance = web3.eth.get_balance(address)
    return web3.from_wei(balance, 'ether')

def print_with_timestamp(message):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {message}")

print_with_timestamp(f"Current balance: {get_balance(account.address)} HAUST")

# Ask user how many wallets to create
num_wallets = int(input("\U0001F522 How many wallets do you want to create? "))
walls = []

# Retry logic for transactions
def retry_transaction(func, *args, retries=3, delay=5):
    for attempt in range(retries):
        try:
            return func(*args)
        except Exception as e:
            print_with_timestamp(f"⚠️ Error: {e}. Retrying... ({attempt + 1}/{retries})")
            time.sleep(delay)
    print_with_timestamp(f"❌ Transaction failed after {retries} attempts.")
    return None

# Create wallets
for i in range(num_wallets):
    new_account = Account.create()
    wallet_data = {"address": new_account.address, "private_key": new_account.key.hex(), "minted": False}
    walls.append(wallet_data)
    print_with_timestamp(f"✅ Wallet {i+1} Created: {new_account.address}")

# Save wallet data to JSON file
with open(WALLET_FILE, "w") as f:
    json.dump(walls, f, indent=4)
print_with_timestamp(f"📝 Wallets saved to {WALLET_FILE}")

# Function to send funds from main wallet to a new wallet with increased gas fee
def send_funds(to_address):
    # Increase the gas price (for example, double the current gas price)
    gas_price = web3.eth.gas_price * 2  # Increase the gas fee
    tx = {
        'to': to_address,
        'value': TOKEN_AMOUNT,
        'gas': 21000,
        'gasPrice': gas_price,
        'nonce': web3.eth.get_transaction_count(account.address),
        'chainId': CHAIN_ID
    }
    signed_tx = web3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
    print_with_timestamp(f"💸 Sent 0.001 HAUST to {to_address} | Tx: {web3.to_hex(tx_hash)}")
    time.sleep(5)
    return tx_hash

# Function to verify if funds have arrived with retries and failure after 6 attempts
def verify_funds_received(address, expected_amount, retries=6):
    for attempt in range(retries):
        balance = get_balance(address)
        if balance >= expected_amount:
            return True
        else:
            print_with_timestamp(f"❌ Funds not received in wallet {address}, retrying... ({attempt + 1}/{retries})")
            time.sleep(10)  # Recheck after 10 seconds
    return False  # Return False after 6 retries if funds haven't been received

# Simulated NFT minting function (Replace with actual mint logic)
def mint_nft(private_key):
    wallet = Account.from_key(private_key)
    contract_address = "0x6B3f185C4c9246c52acE736CA23170801D636c8E"
    contract_abi = [
        {
            "inputs": [],
            "name": "safeMint",
            "outputs": [],
            "stateMutability": "nonpayable",
            "type": "function"
        }
    ]
    
    contract = web3.eth.contract(address=contract_address, abi=contract_abi)
    nonce = web3.eth.get_transaction_count(wallet.address)
    gas_price = web3.eth.gas_price
    
    tx = contract.functions.safeMint().build_transaction({
        'from': wallet.address,
        'gas': 200000,  # Adjust based on actual contract requirements
        'gasPrice': gas_price,
        'nonce': nonce,
        'chainId': CHAIN_ID
    })
    
    signed_tx = web3.eth.account.sign_transaction(tx, private_key)
    tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
    
    print_with_timestamp(f"🎨 Minting NFT for {wallet.address}... Tx: {web3.to_hex(tx_hash)}")

    # Wait for confirmation
    for attempt in range(3):
        try:
            receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)
            if receipt['status'] == 1:
                print_with_timestamp(f"✅ NFT Minted Successfully for {wallet.address}!")
                return True
            else:
                print_with_timestamp(f"❌ Minting failed for {wallet.address}. Retrying...")
        except Exception as e:
            print_with_timestamp(f"⚠️ Error: {e}. Retrying...")
        time.sleep(10)
    
    print_with_timestamp(f"❌ Minting failed after 3 attempts for {wallet.address}.")
    return False

# Send funds to each wallet and immediately mint NFT after funds are received
for wall in walls:
    tx_hash = retry_transaction(send_funds, wall['address'])

    # Recheck until funds are received or retry 6 times
    if tx_hash:
        if verify_funds_received(wall['address'], Web3.from_wei(TOKEN_AMOUNT, 'ether')):
            print_with_timestamp(f"✅ Funds received in wallet {wall['address']}. Proceeding to mint NFT.")
            mint_status = retry_transaction(mint_nft, wall['private_key'])
            wall['minted'] = mint_status if mint_status is not None else False

            # Save wallet data if minting is successful
            if wall['minted']:
                with open(SUCCESS_FILE, "a") as f:
                    f.write(f"Private key: {wall['private_key']}\n")
                    f.write(f"Address: {wall['address']}\n")
                    f.write(f"Minted: {wall['minted']}\n")
                    f.write("-" * 50 + "\n")
                #print_with_timestamp(f"✅ NFT successfully minted for {wall['address']}!")
        else:
            print_with_timestamp(f"❌ Funds not received in wallet {wall['address']} after retrying.")
    time.sleep(2)  # Small delay before moving to the next wallet

print_with_timestamp("🎉 All wallets funded and NFTs minted!")
