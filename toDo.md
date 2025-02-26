# Implementing Unique Viewing Keys in Secret Contract

## Current Implementation

Currently, the contract uses a static viewing key ("test_key") for all users. This is not secure for production use as all users share the same key.

## Proposed Changes

### 1. Contract Changes (Rust)

```rust
use sha2::{Sha256, Digest};
use rand::{Rng, thread_rng};

impl Contract {
    fn generate_viewing_key(&self, entropy: &[u8]) -> String {
        // Generate a random 32 byte value
        let mut rng = thread_rng();
        let mut random_bytes = vec![0u8; 32];
        rng.fill(&mut random_bytes[..]);

        // Combine entropy with random bytes
        let mut hasher = Sha256::new();
        hasher.update(entropy);
        hasher.update(&random_bytes);

        // Convert to hex string
        hex::encode(hasher.finalize())
    }
}

#[entry_point]
pub fn execute(deps: DepsMut, env: Env, info: MessageInfo, msg: ExecuteMsg) -> StdResult<Response> {
    match msg {
        ExecuteMsg::CreateViewingKey { patient_id } => {
            let mut state: State = from_binary(&Binary::from(deps.storage.get(b"state").unwrap_or_default()))?;

            // Generate unique viewing key using block height, time, and sender address
            let entropy = format!(
                "{}{}{}",
                env.block.height,
                env.block.time,
                info.sender
            );

            let key = generate_viewing_key(entropy.as_bytes());
            state.viewing_keys.push((patient_id, key.clone()));
            deps.storage.set(b"state", &to_binary(&state)?);

            // Return key in a way that only the requesting user can see it
            Ok(Response::new()
                .add_attribute("viewing_key", key)
                .set_data(to_binary(&key)?))
        },
        // ... other message handlers
    }
}
```

### 2. API Changes (Python)

```python
@app.post("/create-viewing-key/{patient_id}")
async def create_viewing_key(patient_id: str):
    try:
        msg = {
            "create_viewing_key": {
                "patient_id": patient_id
            }
        }

        tx = wallet.execute_tx(
            CONTRACT_ADDRESS,
            msg
        )

        # Get the viewing key from transaction data
        tx_result = secret.tx.get_tx(tx.txhash)
        viewing_key = tx_result.data  # Encrypted data only visible to tx sender

        return {
            "viewing_key": viewing_key,
            "tx_hash": tx.txhash
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error creating viewing key: {str(e)}"
        )
```

## Security Considerations

1. **Entropy Sources**
   - Block height
   - Block time
   - Sender address
   - Random bytes
2. **Key Storage**
   - Keys are stored encrypted in contract state
   - Only accessible with valid authentication
3. **Key Generation**
   - Uses SHA256 for key generation
   - Includes random entropy to prevent prediction
4. **Access Control**
   - Each patient has their own unique key
   - Keys are tied to specific patient IDs
   - Invalid keys return errors instead of data

## Implementation Steps

1. Update contract dependencies in `Cargo.toml`:

   ```toml
   [dependencies]
   sha2 = "0.9"
   rand = "0.8"
   hex = "0.4"
   ```

2. Deploy updated contract with new viewing key logic

3. Update API to handle unique keys per user

4. Update frontend to store user-specific viewing keys

## Testing

1. Create viewing keys for multiple users
2. Verify each key is unique
3. Test cross-user access (should fail)
4. Test invalid key access (should fail)
5. Test key persistence across sessions

## Migration Plan

1. Create new contract version with unique keys
2. Deploy alongside existing contract
3. Migrate users gradually to new contract
4. Deprecate old contract after migration

This implementation provides secure, unique viewing keys per user while maintaining compatibility with Secret Network's privacy features.
