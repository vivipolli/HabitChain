from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
from secret_ai_sdk.secret_ai import ChatSecret
from secret_ai_sdk.secret import Secret
import os
import uvicorn
from prompt_templates import ANALYZE_AND_SUGGEST_PROMPT
from dotenv import load_dotenv
from secret_sdk.client.lcd import LCDClient
from secret_sdk.key.mnemonic import MnemonicKey
from mnemonic import Mnemonic
import json

import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    load_dotenv()

    app = FastAPI(
        title="Behavioral Analysis API",
        description="API for behavioral analysis using Secret AI",
        version="1.0.0"
    )

    app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "https://secret-vert-six.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

    api_key = os.getenv("SECRET_AI_API_KEY")
    if not api_key:
        raise ValueError("SECRET_AI_API_KEY environment variable is not set")

    secret_client = Secret()
    models = secret_client.get_models()
    urls = secret_client.get_urls(model=models[0])
    
    secret_ai_llm = ChatSecret(
        base_url=urls[0],
        model=models[0],
        temperature=1.0
    )

    mnemonic = os.getenv("SECRET_MNEMONIC")
    if not mnemonic:
        raise ValueError("SECRET_MNEMONIC environment variable is not set")

    mnemo = Mnemonic("english")
    if not mnemo.check(mnemonic):
        raise ValueError("Invalid mnemonic")
    
    seed = mnemo.to_seed(mnemonic)
    
    mk = MnemonicKey(mnemonic=mnemonic)
    
    secret = LCDClient(
        url="https://pulsar.lcd.secretnodes.com",
        chain_id="pulsar-3"
    )
    wallet = secret.wallet(mk)

except Exception as e:
    logger.error(f"Initialization error: {str(e)}", exc_info=True)
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

# Valor estático para desenvolvimento
STATIC_VIEWING_KEY = "test_key"

def format_ai_response(content: str) -> dict:
    """
    Format the AI response into a structured JSON format.
    """
    try:
        # Split the content into general analysis and habits
        parts = content.split("Habits:")
        
        # Capture the general analysis
        general_analysis = parts[0].replace("GENERAL:", "").strip() if len(parts) > 0 else content.strip()
        
        habits = []
        if len(parts) > 1:
            habit_sections = parts[1].strip().split("\n\n")
            for section in habit_sections:
                if section.strip():
                    lines = section.strip().split("\n")
                    
                    # Ensure there are enough lines to extract habit details
                    if len(lines) < 4:
                        logger.warning("Incomplete habit section found, skipping.")
                        continue
                    
                    # Extract habit details
                    habit_name = lines[0].strip().replace("**", "")
                    description = lines[1].split("**Description:** ")[-1].strip() if "**Description:**" in lines[1] else "No description provided"
                    
                    implementation = []
                    for line in lines[2:]:
                        if line.strip().startswith("**Implementation:**"):
                            continue
                        if line.strip().startswith("1. "):
                            step = line.strip().split(". ", 1)[-1]
                            implementation.append(step)
                    
                    scientific_basis = lines[-1].split("**Scientific Basis:** ")[-1].strip() if "**Scientific Basis:**" in lines[-1] else "No scientific basis provided"
                    
                    habit = {
                        "name": habit_name,
                        "description": description,
                        "implementation": implementation,
                        "scientific_basis": scientific_basis
                    }
                    habits.append(habit)
        
        formatted_response = {
            "general_analysis": general_analysis,
            "recommended_habits": habits
        }
        
        return formatted_response
        
    except Exception as e:
        logger.error(f"Error formatting response: {str(e)}", exc_info=True)
        return {
            "general_analysis": content,
            "recommended_habits": []
        }

# Routes
@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_behavior(data: BehaviorData):
    try:
        # Format the prompt with the behavior data
        formatted_prompt = ANALYZE_AND_SUGGEST_PROMPT.format(
            behavior=data.behavior,
            antecedent=data.antecedent,
            consequence=data.consequence,
            previous_attempts=data.previous_attempts
        )
        
        messages = [
            (
                "system",
                "You are a psychologist specializing in behavioral analysis and radical behaviorism. Provide accurate analyses and practical suggestions based on scientific evidence."
            ),
            ("human", formatted_prompt),
        ]
        
        response = secret_ai_llm.invoke(messages, stream=False)
        
        # Format the response
        formatted_response = format_ai_response(response.content)
        
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
        # In production, this would interact with the contract
        # For now, return a static key for development
        return {"viewing_key": STATIC_VIEWING_KEY}
        
    except Exception as e:
        logger.error(f"Viewing key creation error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analyses/{patient_id}", response_model=GetAnalysesResponse)
async def get_analyses(patient_id: str, viewing_key: str):
    try:
        
        try:
            result = secret.wasm.contract_query(
                contract_address=CONTRACT_ADDRESS,
                query={
                    "get_analyses": {
                        "patient_id": patient_id,
                        "viewing_key": STATIC_VIEWING_KEY
                    }
                }
            )

            
            if result and len(result) > 0:
                for analysis in result:
                    content = json.loads(analysis["content"])
                    if not content.get("recommended_habits"):
                        content["recommended_habits"] = [
                            {
                                "name": "Gradual Exposure",
                                "description": "Start with small, manageable social interactions",
                                "implementation": [
                                    "Begin with brief interactions",
                                    "Practice with trusted friends/family",
                                    "Gradually increase duration and complexity"
                                ],
                                "scientific_basis": "Based on exposure therapy principles"
                            },
                            {
                                "name": "Self-Compassion Practice",
                                "description": "Develop a kinder inner dialogue",
                                "implementation": [
                                    "Notice negative self-talk",
                                    "Challenge unrealistic thoughts",
                                    "Practice positive self-affirmations"
                                ],
                                "scientific_basis": "Based on cognitive behavioral therapy"
                            }
                        ]
                        analysis["content"] = json.dumps(content)
                
                return {"analyses": result}
            
        except Exception as contract_error:
            raise HTTPException(
                status_code=500,
                detail=f"Error retrieving analyses from contract: {str(contract_error)}"
            )
            
    except Exception as e:
        logger.error(f"Fetching analyses error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/daily-progress", response_model=DailyProgressResponse)
async def save_daily_progress(progress: DailyProgress):
    try:
        # Store in contract (in production)
        # For development, just return a mock tx hash
        return {"tx_hash": "mock_tx_hash_for_daily_progress"}
        
    except Exception as e:
        logger.error(f"Storing progress error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/daily-progress/{patient_id}", response_model=GetDailyProgressResponse)
async def get_daily_progress(patient_id: str, viewing_key: str):
    try:
        # Validate viewing key (in production)
        if viewing_key != STATIC_VIEWING_KEY:
            # In production, this would verify against the contract
            # For development, we accept the static key
            pass
        
        # In production, this would query the contract
        # For development, return mock data
        mock_progress = [
            {
                "id": "1",
                "date": int(time.time()) - 86400,
                "tasks": [
                    {"name": "Deep Breathing", "completed": True},
                    {"name": "Progressive Exposure", "completed": False}
                ],
                "description": "I felt less anxious today after practicing deep breathing."
            }
        ]
        
        return {"progress": mock_progress}
        
    except Exception as e:
        logger.error(f"Fetching progress error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "Welcome to the Behavioral Analysis API"}

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True) 