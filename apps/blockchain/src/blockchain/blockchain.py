import os
from web3 import Web3
from eth_account import Account
from eth_account.signers.local import LocalAccount
from web3.middleware import construct_sign_and_send_raw_middleware
import traceback
import sys

from logging import getLogger
logger = getLogger('base')

infura_api_key = os.environ.get('INFURA_API_KEY')
contract_address = os.environ.get('CONTRACT_ADDRESS')
private_key = os.environ.get('ACCOUNT_PRIVATE_KEY')

web3 = Web3(Web3.HTTPProvider(infura_api_key))

account = Account.from_key(private_key)

web3.middleware_onion.add(construct_sign_and_send_raw_middleware(private_key))

my_account = account.address

contract_abi = [
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
	},
	{
		"inputs": [],
		"stateMutability": "nonpayable",
		"type": "constructor"
	},
	{
		"inputs": [],
		"name": "getLastTournamentId",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
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
				"internalType": "struct BillTournament.MatchResult[]",
				"name": "",
				"type": "tuple[]"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "lastTournamentId",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	}
]



contract = web3.eth.contract(address=contract_address, abi=contract_abi)

def record_match_on_blockchain(tournament_id, winner, loser, winner_score, loser_score):
    try:
        tx_hash = (contract.functions.recordMatch(tournament_id, winner, loser, winner_score, loser_score).
                   transact({'from':  my_account}))
        
        receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
        if receipt.status == 1:
            logger.info("Le match a été enregistré avec succès sur la blockchain !")
            print_etherscan_transaction_url(tx_hash)
        else:
            logger.error("L'enregistrement du match a échoué.")
    except Exception as e:
        error_message = "Erreur lors de l'enregistrement du match :\n"
        error_message += f"Type d'erreur : {type(e).__name__}\n"
        error_message += f"Message d'erreur : {str(e)}\n"
        error_message += "Traceback complet :\n"
        error_message += traceback.format_exc()
        logger.error(error_message)
        logger.error("Variables locales au moment de l'erreur :")
        for name, value in locals().items():
            logger.error(f"{name} = {value}")

def print_etherscan_transaction_url(tx_hash):
    etherscan_url = 'https://sepolia.etherscan.io/tx/'
    logger.info("Transaction URL: " + etherscan_url + tx_hash.hex())
    
def get_last_tournament_id():
    try:
        last_tournament_id = contract.functions.getLastTournamentId().call()
        logger.info(f"Le dernier ID de tournoi est : {last_tournament_id}")
        return last_tournament_id
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du dernier ID de tournoi : {str(e)}")