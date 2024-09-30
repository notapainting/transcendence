# Sepolia Contract

The **BillTournament** contract is a smart contract built on Ethereum, designed to record and manage match results for tournaments. It allows the owner to create and register multiple matches within different tournaments.

## Key Features

- **Match Recording**: Only the owner of the contract can record a new match. Each match includes details such as the winner’s name, the loser’s name, and their respective scores.

- **Result Storage**: Match results are stored on the blockchain using a `mapping` data structure, which associates a tournament ID with a list of matches.

- **Result Retrieval**: The match history for each tournament can be retrieved publicly via a read function, allowing anyone to view the recorded match results.

## Functions Overview

- `recordMatch(uint256 tournamentId, string memory winner, string memory loser, int256 winnerScore, int256 loserScore)`: Records a new match for a specified tournament. Only callable by the contract owner.

- `getMatchResults(uint256 tournamentId)`: Returns the list of matches for the specified tournament.

- `getLastTournamentId()`: Returns the ID of the most recently updated tournament.

# Blockchain Interaction via Django API

This is a Django-based application designed to interact with an Ethereum smart contract for recording and retrieving tournament match results on the blockchain.

## Key Components

### 1. **Blockchain Interaction**

- The `blockchain.py` script interacts with the smart contract by:
  - **Recording matches**: Using `record_match_on_blockchain` to send a match result to the Ethereum network.
  - **Fetching last tournament ID**: Using `get_last_tournament_id` to retrieve the most recent tournament ID stored on the blockchain.
  
### 2. **Django API Views**

- The Django API interacts with the blockchain container by sending HTTP requests to register new matches and retrieve information.
  
  - **`register_match` View**:
    - Handles both POST and GET requests.
    - POST requests are used to submit new match results to the blockchain via the `record_match_on_blockchain` function.
    - GET requests retrieve the latest tournament ID from the blockchain.
    - This view is **asynchronous** and leverages `asyncio` to manage the delay while waiting for blockchain transactions to be mined.
  
  - **Error Handling**:
    - The view handles multiple error types including missing keys in the JSON request body, JSON parsing errors, and any general internal server errors.
    - All errors are logged for debugging purposes.

### 3. **Asynchronous Tasks and HTTP Requests**

- The `send_match_to_blockchain` function sends the match data to the blockchain service using asynchronous HTTP requests.


## Environment Setup
  
  ### Required Environment Variables:
  
  - **`INFURA_API_KEY`**: The API key to connect to an Ethereum node via Infura.
  - **`CONTRACT_ADDRESS`**: The smart contract's address on the Ethereum network.
  - **`ACCOUNT_PRIVATE_KEY`**: The private key used to sign blockchain transactions.

## How It Works

1. **Recording a Match**:
   - A POST request is sent to `/register_match/` containing the match details (tournament ID, winner, loser, scores).
   - The match is sent to the blockchain container, where it is processed and recorded using the Web3 library.
   - Once the transaction is confirmed, the response is sent back indicating success or failure.

2. **Fetching the Last Tournament ID**:
   - A GET request to `/register_match/` triggers a request to the blockchain container to fetch the latest tournament ID.

## Example Usage:

- **POST**: To register a match
  ```bash
  curl -X POST http://localhost:8000/register_match/ \
  -H "Content-Type: application/json" \
  -d '{
      "tournament_id": 1,
      "winner": "Player1",
      "loser": "Player2",
      "score_w": 3,
      "score_l": 1
  }

- **GET**: To get the last tournament ID
 ```bash
 curl -X GET http://localhost:8000/register_match/
