# HabitChain

A privacy-first mental health application that helps users track and analyze behavioral patterns while ensuring complete data confidentiality through **Secret Network's** encryption capabilities and **Secret AI SDK**.

## ⭐ Key Features

- 🧠 **Private Behavioral Analysis:** AI-powered analysis with encrypted data
- 📊 **Smart Recommendations:** Personalized habit suggestions based on encrypted analysis
- 📝 **Secure Habit Tracking:** Daily progress monitoring with privacy guarantees
- 🔑 **User-Friendly Web3 Authentication:** Secure and private access through social login (Google, Facebook, Twitter, etc.), making Web3 accessible to everyone
- 🛡️ **Privacy-First Design:** All data encrypted and stored on Secret Network

---

## 🎯 Problem Statement

Mental health data is highly sensitive, yet many digital health solutions compromise privacy and accessibility. Centralized data storage often leaves user information vulnerable to breaches, with limited user control over data access and insecure AI analysis processes.

Beyond privacy concerns, patients frequently express dissatisfaction with the quality and cost of traditional therapy services. High prices and inconsistent service quality make mental health care inaccessible for many. As a result, some individuals turn to common language models (LLMs) for mental health advice. However, these alternatives lack privacy guarantees, store sensitive conversations without encryption, and offer no systematic progress tracking or professional oversight.

Our platform addresses these issues that integrates AI-driven analysis with professional mental health care, ensuring both data security and high-quality service. By leveraging behavioral analysis principles, our platform suggests personalized interventions to support users' mental health journeys. **It is important to note that while our platform offers valuable insights and recommendations, it is designed to complement, not replace, conventional therapy.**

## 💡 Solution

We leverage **Secret Network** and **Secret AI SDK** to create a secure platform where:

- 🔒 **Users maintain complete control** over their mental health data
- 🤖 **AI analysis is performed on encrypted data**
- 🔐 **All interactions are confidential by default**
- 🗝️ **Access is managed through secure viewing keys**

---

# 🛠️ Development Deep Dive

## 🏗️ Architecture Overview

### 1. Smart Contracts (Rust)

- 🔐 Encrypted data storage
- 🗝️ Viewing key management
- 🔐 Privacy-preserving queries

### 2. Backend API (FastAPI)

- 🔄 Secret Network integration
- 🤖 Secret AI SDK implementation
- 🛣️ REST API for frontend communication

### 3. Frontend (React)

- 🔑 Web3Auth integration
- ⚡ Real-time tracking
- 🔒 Encrypted data submission

---

# 🚀 Technical Setup

## 📋 Prerequisites

### System Requirements

Required technologies:

- 🦀 Rust and Cargo (latest version)
- 🐍 Python 3.12 with Anaconda
- 💻 Node.js v16 or higher
- 🐳 Docker (for contract optimization)

For detailed installation instructions, refer to:

- [Rust Installation Guide](https://www.rust-lang.org/tools/install)
- [Anaconda Installation Guide](https://docs.anaconda.com/free/anaconda/install/)
- [Node.js Downloads](https://nodejs.org/)
- [Docker Installation](https://docs.docker.com/get-docker/)

### Secret Network Tools

```sh
# Install SecretCLI
wget https://github.com/scrtlabs/SecretNetwork/releases/latest/download/secretcli-Linux
chmod +x secretcli-Linux
sudo mv secretcli-Linux /usr/local/bin/secretcli

# Add WASM target
rustup target add wasm32-unknown-unknown
```

---

## Smart Contract Deployment

### Build Contract

```sh
cargo build --release --target wasm32-unknown-unknown
cp target/wasm32-unknown-unknown/release/secret_mood.wasm .
gzip -k secret_mood.wasm
```

### Optimize Contract

```sh
docker run --rm -v "$(pwd)":/code \
 --mount type=volume,source="$(basename "$(pwd)")_cache",target=/code/target \
 --mount type=volume,source=registry_cache,target=/usr/local/cargo/registry \
 cosmwasm/rust-optimizer:0.12.13
mv secret_mood.wasm.gz contract.wasm.gz
```

### Deploy Contract

```sh
# Upload
secretcli tx compute store contract.wasm.gz --from app \
  --chain-id pulsar-3 --node https://pulsar.rpc.secretnodes.com \
  --gas-prices=0.25uscrt --gas=1000000 -y

# Get code ID
secretcli query tx <TX_HASH> --chain-id pulsar-3 \
  --node https://pulsar.rpc.secretnodes.com

# Instantiate
secretcli tx compute instantiate <CODE_ID> '{}' --from app \
  --label "behavioral-analysis" --chain-id pulsar-3 \
  --node https://pulsar.rpc.secretnodes.com \
  --gas-prices=0.25uscrt --gas=700000 -y
```

---

## API Setup

### 1. Activate Environment and Install Dependencies

```sh
# Activate the Anaconda environment
conda activate secret-env

# Navigate to the API directory
cd api

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

```sh
# API Configuration
SECRET_AI_API_KEY=your_secret_ai_api_key

# Secret Network Configuration
SECRET_MNEMONIC="your_mnemonic"
CONTRACT_ADDRESS="your_contract_address"
CONTRACT_CODE_HASH="your_contract_hash"
NODE_URL="https://pulsar.lcd.secretnodes.com"
CHAIN_ID="pulsar-3"
```

### 3. Run API

```sh
uvicorn api:app --reload
```

---

## Frontend Setup

### 1. Install Dependencies

```sh
cd frontend
npm install
```

### 2. Environment Configuration

### Obtain Web3Auth Client ID

- Create account on **Web3Auth Dashboard**
- Set up new project
- Configure authorized domains
- Copy **Client ID** to frontend `.env`

```sh
VITE_API_BASE_URL=http://localhost:8000
VITE_WEB3AUTH_CLIENT_ID=your_web3auth_client_id
VITE_RPC_TARGET=https://rpc.ankr.com/eth
```

### 3. Run Development Server

```sh
npm run dev
```

---

# 🔮 Future Development

## Short Term (3 months)

- 🔑 **Dynamic Viewing Keys**: Implementation of unique, per-user viewing keys for enhanced privacy and access control
- 📊 **Comprehensive Habit Tracking**: Recording of completed habits, habit history, and daily notes for AI-powered progress analysis
- 🤖 **AI Prompt Optimization**: Refinement of prompt engineering for more accurate and personalized behavioral analysis

## Medium Term (6-12 months)

- 📈 **Progress Analytics Dashboard**: Comprehensive graphical visualization of user's weekly, monthly, and annual habit progress
- 💡 **Alternative Habit Generation**: Smart feature to suggest alternative habits when users decline initial recommendations
- 💳 **Payment Integration**: Implementation of subscription-based model with secure payment processing

## Long Term (1-2 years)

- 🌐 **Social Media Integration**: Generation of customizable templates for sharing progress and achievements, encouraging community support and self-motivation
- 🤝 **Decentralized Mental Health Network**: Integration with a decentralized social platform focused on mental health, enabling private and secure community interactions

---

# 📚 References

- 📖 [Secret Network Documentation](https://docs.scrt.network/)
- 🤖 [Secret AI Documentation](https://docs.secret.ai/)
- 🔑 [Web3Auth Documentation](https://web3auth.io/)
- ⚡ [FastAPI Documentation](https://fastapi.tiangolo.com/)
