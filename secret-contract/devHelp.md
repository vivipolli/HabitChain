# Secret Contract Deployment Guide

## 1. Build and Optimize

```bash
# Clean previous builds
cargo clean
rm -f contract.wasm*
rm -f Cargo.lock
cargo build --release --target wasm32-unknown-unknown

# Update Cargo.lock version to 3 if needed
# Edit Cargo.lock and change "version = 3" at the top

# Optimize contract using Docker
docker run --rm -v "$(pwd)":/code \
  --mount type=volume,source="$(basename "$(pwd)")_cache",target=/code/target \
  --mount type=volume,source=registry_cache,target=/usr/local/cargo/registry \
  cosmwasm/rust-optimizer:0.12.13
```

## 2. Upload Contract

```bash
# Upload the optimized contract
secretcli tx compute store artifacts/secret_contract.wasm --from app --chain-id pulsar-3 --node https://pulsar.rpc.secretnodes.com --gas-prices=0.25uscrt --gas=1000000 -y

# Get code_id from transaction hash
secretcli query tx <TRANSACTION_HASH> --chain-id pulsar-3 --node https://pulsar.rpc.secretnodes.com
```

## 3. Instantiate Contract

```bash
# Instantiate the contract
secretcli tx compute instantiate <CODE_ID> '{}' --from app --label "behavioral-analysis" --chain-id pulsar-3 --node https://pulsar.rpc.secretnodes.com --gas-prices=0.25uscrt --gas=700000 -y

# Get contract address
secretcli query compute list-contract-by-code <CODE_ID> --chain-id pulsar-3 --node https://pulsar.rpc.secretnodes.com
```

## 4. Interact with Contract

### Create Viewing Key

```bash
# Create viewing key for a patient
secretcli tx compute execute <CONTRACT_ADDRESS> '{"create_viewing_key":{"patient_id":"123"}}' --from app --chain-id pulsar-3 --node https://pulsar.rpc.secretnodes.com --gas-prices=0.25uscrt --gas=300000 -y

# Query transaction to confirm (viewing key is "test_key" in this implementation)
secretcli query tx <TRANSACTION_HASH> --chain-id pulsar-3 --node https://pulsar.rpc.secretnodes.com
```

### Save Analysis

```bash
# Save a new analysis for a patient
secretcli tx compute execute <CONTRACT_ADDRESS> '{"save_analysis":{"patient_id":"123","content":"análise do paciente"}}' --from app --chain-id pulsar-3 --node https://pulsar.rpc.secretnodes.com --gas-prices=0.25uscrt --gas=300000 -y

# Query transaction to confirm
secretcli query tx <TRANSACTION_HASH> --chain-id pulsar-3 --node https://pulsar.rpc.secretnodes.com
```

### Query Analyses

```bash
# Query all analyses for a patient using viewing key
secretcli query compute query <CONTRACT_ADDRESS> '{"get_analyses":{"patient_id":"123","viewing_key":"test_key"}}' --chain-id pulsar-3 --node https://pulsar.rpc.secretnodes.com
```

## Useful Commands

```bash
# List all code IDs
secretcli query compute list-code --chain-id pulsar-3 --node https://pulsar.rpc.secretnodes.com

# Query transaction details
secretcli query tx <HASH> --chain-id pulsar-3 --node https://pulsar.rpc.secretnodes.com

# List contracts for a specific code ID
secretcli query compute list-contract-by-code <CODE_ID> --chain-id pulsar-3 --node https://pulsar.rpc.secretnodes.com
```

## Notes

- The viewing key is set to "test_key" in the current implementation
- All transactions return a hash that can be queried to confirm the result
- Gas prices and limits may need adjustment based on contract complexity
- Always verify transaction success by querying the transaction hash
