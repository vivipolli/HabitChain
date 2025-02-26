from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from secret_ai_sdk.secret_ai import ChatSecret
from secret_ai_sdk.secret import Secret
import os
import uvicorn
from prompt_templates import ANALYZE_AND_SUGGEST_PROMPT
from dotenv import load_dotenv
from secret_sdk.client.lcd import LCDClient
from secret_sdk.key.mnemonic import MnemonicKey
from secret_sdk.core.tx import Fee
from secret_sdk.core.wasm import MsgExecuteContract
from bip32utils import BIP32Key
from mnemonic import Mnemonic
import json
from secret_sdk.client.lcd.api.tx import BroadcastMode

import time
import logging

# Configurar logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

try:
    logger.info("Iniciando carregamento das variáveis de ambiente...")
    load_dotenv()

    logger.info("Inicializando FastAPI app...")
    app = FastAPI(
        title="Behavioral Analysis API",
        description="API for behavioral analysis using Secret AI",
        version="1.0.0"
    )

    logger.info("Verificando SECRET_AI_API_KEY...")
    api_key = os.getenv("SECRET_AI_API_KEY")
    if not api_key:
        raise ValueError("SECRET_AI_API_KEY environment variable is not set")

    logger.info("Inicializando Secret AI client...")
    secret_client = Secret()
    logger.info("Obtendo modelos disponíveis...")
    models = secret_client.get_models()
    logger.info(f"Modelos disponíveis: {models}")
    urls = secret_client.get_urls(model=models[0])
    logger.info(f"URLs disponíveis: {urls}")
    
    logger.info("Inicializando ChatSecret...")
    secret_ai_llm = ChatSecret(
        base_url=urls[0],
        model=models[0],
        temperature=1.0
    )

    logger.info("Verificando SECRET_MNEMONIC...")
    mnemonic = os.getenv("SECRET_MNEMONIC")
    if not mnemonic:
        raise ValueError("SECRET_MNEMONIC environment variable is not set")

    logger.info("Validando mnemônica...")
    mnemo = Mnemonic("english")
    if not mnemo.check(mnemonic):
        raise ValueError("Mnemônica inválida")
    
    logger.info("Gerando seed da mnemônica...")
    seed = mnemo.to_seed(mnemonic)
    
    logger.info("Inicializando Secret Network client...")
    mk = MnemonicKey(mnemonic=mnemonic)
    logger.info("MnemonicKey criada com sucesso!")
    
    secret = LCDClient(
        url="https://pulsar.lcd.secretnodes.com",  # Endpoint oficial da Secret Network
        chain_id="pulsar-3"
    )
    wallet = secret.wallet(mk)
    logger.info(f"Endereço da carteira: {wallet.key.acc_address}")

except Exception as e:
    logger.error(f"Erro durante a inicialização: {str(e)}", exc_info=True)
    raise

# Contract configuration
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")
CONTRACT_CODE_HASH = os.getenv("CONTRACT_CODE_HASH")

if not CONTRACT_CODE_HASH:
    raise ValueError("CONTRACT_CODE_HASH environment variable must be set")

# Define data models
class BehaviorData(BaseModel):
    patient_id: str
    behavior: str
    antecedent: str
    consequence: str
    previous_attempts: str

class Habit(BaseModel):
    name: str
    description: str
    implementation: List[str]
    scientific_basis: str

class FormattedAnalysis(BaseModel):
    general_analysis: str
    recommended_habits: List[Habit]

class AnalysisResponse(BaseModel):
    analysis: Dict[str, Any]  # Mudando para Dict para aceitar o formato atual
    tx_hash: str

class Task(BaseModel):
    name: str
    completed: bool

class DailyProgress(BaseModel):
    patient_id: str
    date: int  # Unix timestamp
    tasks: List[Task]
    description: str

class DailyProgressResponse(BaseModel):
    tx_hash: str

class GetAnalysesResponse(BaseModel):
    analyses: List[Dict[str, Any]]

class GetDailyProgressResponse(BaseModel):
    progress: List[Dict[str, Any]]

def format_ai_response(content: str) -> dict:
    """
    Format the AI response into a structured JSON format.
    """
    try:
        # Split content into analysis and habits
        parts = content.split("### Habit")
        general_analysis = parts[0].split("\n\n")[2]  # Skip think block and get analysis
        
        habits = []
        for habit_text in parts[1:]:  # Process each habit section
            lines = habit_text.strip().split("\n")
            
            # Extract habit name
            habit_name = lines[0].split(": ", 1)[1]
            
            # Extract description
            description = lines[1].replace("**Description:** ", "").strip()
            
            # Extract implementation steps
            implementation = []
            implementation_start = habit_text.find("  1. ")
            implementation_end = habit_text.find("- **Basis:**")
            if implementation_start != -1 and implementation_end != -1:
                steps = habit_text[implementation_start:implementation_end].strip().split("\n")
                implementation = [step.replace("  1. ", "").replace("  2. ", "").replace("  3. ", "").strip() 
                               for step in steps if step.strip()]
            
            # Extract scientific basis
            basis_start = habit_text.find("- **Basis:** ")
            if basis_start != -1:
                scientific_basis = habit_text[basis_start:].replace("- **Basis:** ", "").strip()
            
            habits.append({
                "name": habit_name,
                "description": description,
                "implementation": implementation,
                "scientific_basis": scientific_basis
            })
        
        return {
            "general_analysis": general_analysis,
            "recommended_habits": habits
        }
        
    except Exception as e:
        logger.error(f"Error formatting AI response: {str(e)}")
        return {
            "general_analysis": content,
            "recommended_habits": []
        }

# Routes
@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_behavior(data: BehaviorData):
    try:
        logger.info(f"Recebendo requisição de análise para patient_id: {data.patient_id}")
        
        # Format the prompt with the behavior data
        formatted_prompt = ANALYZE_AND_SUGGEST_PROMPT.format(
            behavior=data.behavior,
            antecedent=data.antecedent,
            consequence=data.consequence,
            previous_attempts=data.previous_attempts
        )
        logger.info("Prompt formatado com sucesso")
        
        # Define messages for the LLM
        messages = [
            (
                "system",
                "You are a psychologist specializing in behavioral analysis and radical behaviorism. Provide accurate analyses and practical suggestions based on scientific evidence."
            ),
            ("human", formatted_prompt),
        ]
        
        logger.info("Invocando Secret AI LLM...")
        response = secret_ai_llm.invoke(messages, stream=False)
        logger.info("Resposta do LLM recebida com sucesso")
        
        # Format the response
        formatted_response = format_ai_response(response.content)
        
        # Save to contract
        msg = {
            "save_analysis": {
                "patient_id": data.patient_id,
                "content": json.dumps(formatted_response)  # Save formatted JSON
            }
        }
        
        tx = wallet.execute_tx(
            CONTRACT_ADDRESS,
            msg,
            memo="Save analysis",
        )
        
        return {
            "analysis": formatted_response,  # Return formatted JSON
            "tx_hash": tx.txhash
        }
    
    except Exception as e:
        logger.error(f"Erro durante o processamento: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error generating analysis: {str(e)}")

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
        
        return {"viewing_key": "test_key", "tx_hash": tx.txhash}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating viewing key: {str(e)}")

@app.get("/analyses/{patient_id}", response_model=GetAnalysesResponse)
async def get_analyses(patient_id: str, viewing_key: str):
    try:
        result = secret.wasm.contract_query(
            contract_address=CONTRACT_ADDRESS,
            query={
                "get_analyses": {
                    "patient_id": patient_id,
                    "viewing_key": viewing_key
                }
            }
        )
        return {"analyses": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving analyses: {str(e)}")

@app.post("/daily-progress", response_model=DailyProgressResponse)
async def save_daily_progress(progress: DailyProgress):
    try:
        # Store daily progress in Secret Network contract
        tx_result = secret_network.execute(
            contract_address=CONTRACT_ADDRESS,
            code_hash=CONTRACT_CODE_HASH,
            msg={
                "save_daily_progress": {
                    "patient_id": progress.patient_id,
                    "date": progress.date,
                    "tasks": [task.dict() for task in progress.tasks],
                    "description": progress.description
                }
            },
        )
        
        return {"tx_hash": tx_result["txhash"]}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving daily progress: {str(e)}")

@app.get("/daily-progress/{patient_id}", response_model=GetDailyProgressResponse)
async def get_daily_progress(patient_id: str):
    try:
        # Query daily progress from Secret Network contract
        query_result = secret_network.query(
            contract_address=CONTRACT_ADDRESS,
            code_hash=CONTRACT_CODE_HASH,
            query={
                "get_daily_progress": {
                    "patient_id": patient_id
                }
            }
        )
        
        return query_result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving daily progress: {str(e)}")

@app.get("/")
async def root():
    return {"message": "Welcome to the Behavioral Analysis API"}

# Run the application
if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True) 