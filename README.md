# Haust Testnet Wallet Creator and NFT Minter

This Python script automates the creation of wallets on the Haust Testnet, funds them with a small amount of HAUST tokens, and mints NFTs for each wallet. The script uses the `web3.py` library to interact with the blockchain and includes retry logic for transactions to ensure reliability.

## TTDL 
- Just import your private key in main.py lol

## Features

- **Wallet Creation**: Generates a specified number of Ethereum-compatible wallets.
- **Funding Wallets**: Sends a fixed amount of HAUST tokens (0.001 HAUST) to each wallet.
- **NFT Minting**: Mints an NFT for each wallet after confirming the funds are received.
- **Retry Logic**: Implements retry mechanisms for transactions to handle network issues.
- **Logging**: Provides detailed logs with timestamps for each step.
- **Data Persistence**: Saves wallet details (address and private key) to a JSON file and successful minting details to a text file.

## Prerequisites

Before running the script, ensure you have the following installed:

- Python 3.x
- Required Python libraries: `web3`, `eth_account`, `colorama`

You can install the required libraries using pip:

```bash
pip install web3 eth_account colorama


