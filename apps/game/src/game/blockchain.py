import os
from web3 import Web3
from eth_account import Account
from eth_account.signers.local import LocalAccount
from web3.middleware import construct_sign_and_send_raw_middleware

infura_api_key = os.environ.get('INFURA_API_KEY')

# Se connecter à un nœud Ethereum (nœud local ou RPC)
# web3 = Web3(Web3.HTTPProvider(f"https://sepolia.infura.io/v3/{infura_api_key}"))

web3 = Web3(Web3.HTTPProvider(f"https://sepolia.infura.io/v3/82baf32070fa426a9603f544c7ccf3cc"))

private_key = '784da8965fb39e878bec458d9ceb342b6a9ee506a7a8c16d33e95ea6ac823895'

account = Account.from_key(private_key)

web3.middleware_onion.add(construct_sign_and_send_raw_middleware(private_key))

my_account = account.address

contract_abi = [
	{
		"inputs": [],
		"stateMutability": "nonpayable",
		"type": "constructor"
	},
	{
		"anonymous": "false",
		"inputs": [
			{
				"indexed": "true",
				"internalType": "uint256",
				"name": "tournamentId",
				"type": "uint256"
			},
			{
				"indexed": "false",
				"internalType": "string",
				"name": "winner",
				"type": "string"
			},
			{
				"indexed": "false",
				"internalType": "string",
				"name": "loser",
				"type": "string"
			},
			{
				"indexed": "false",
				"internalType": "int256",
				"name": "winnerScore",
				"type": "int256"
			},
			{
				"indexed": "false",
				"internalType": "int256",
				"name": "loserScore",
				"type": "int256"
			}
		],
		"name": "MatchRecorded",
		"type": "event"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "_tournamentId",
				"type": "uint256"
			}
		],
		"name": "getMatchResults",
		"outputs": [
			{
				"components": [
					{
						"internalType": "string",
						"name": "winner",
						"type": "string"
					},
					{
						"internalType": "string",
						"name": "loser",
						"type": "string"
					},
					{
						"internalType": "int256",
						"name": "winnerScore",
						"type": "int256"
					},
					{
						"internalType": "int256",
						"name": "loserScore",
						"type": "int256"
					}
				],
				"internalType": "struct SimpleTournament.MatchResult[]",
				"name": "",
				"type": "tuple[]"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "_tournamentId",
				"type": "uint256"
			},
			{
				"internalType": "string",
				"name": "_winner",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "_loser",
				"type": "string"
			},
			{
				"internalType": "int256",
				"name": "_winnerScore",
				"type": "int256"
			},
			{
				"internalType": "int256",
				"name": "_loserScore",
				"type": "int256"
			}
		],
		"name": "recordMatch",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	}
]

contract_address = '0x2947e45e3C99e4a11E0466A8Cbecda9fD956A8CC'

contract = web3.eth.contract(address=contract_address, abi=contract_abi)    

import traceback
import sys

def record_match_on_blockchain(tournament_id, winner, loser, winner_score, loser_score):
    try:
        transaction = contract.functions.recordMatch(
			tournament_id,
			winner,
			loser,
			winner_score,
			loser_score
		).build_transaction({
			'from': my_account,
			'nonce': web3.eth.get_transaction_count(my_account),
			'gas': 2000000,
			'gasPrice': web3.to_wei('20', 'gwei')
		})
        signed_txn = web3.eth.account.sign_transaction(transaction, private_key)
        tx_hash = web3.eth.send_raw_transaction(signed_txn.raw_transaction)
        receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
        if receipt.status == 1:
            print("Le match a été enregistré avec succès sur la blockchain !")
            print_etherscan_transaction_url(tx_hash)
        else:
            print("L'enregistrement du match a échoué.")
    except Exception as e:
        error_message = "Erreur lors de l'enregistrement du match :\n"
        error_message += f"Type d'erreur : {type(e).__name__}\n"
        error_message += f"Message d'erreur : {str(e)}\n"
        error_message += "Traceback complet :\n"
        error_message += traceback.format_exc()
        print(error_message, file=sys.stderr)
        print("\nVariables locales au moment de l'erreur :")
        for name, value in locals().items():
            print(f"{name} = {value}")

def print_etherscan_transaction_url(tx_hash):
    etherscan_url = 'https://sepolia.etherscan.io/tx/'
    print("Transaction URL:", etherscan_url + tx_hash.hex())