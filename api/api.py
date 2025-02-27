from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
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

    app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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

# Valor estático para desenvolvimento
STATIC_VIEWING_KEY = "test_key"

def format_ai_response(content: str) -> dict:
    """
    Format the AI response into a structured JSON format.
    """
    try:
        logger.info("=== Iniciando formatação da resposta da IA ===")
        logger.info(f"Conteúdo bruto recebido da IA:\n{content}")
        
        # Split content into analysis and habits
        parts = content.split("### Habit")
        logger.info(f"Número de partes após split '### Habit': {len(parts)}")
        logger.info(f"Partes encontradas:\n{parts}")
        
        # Get general analysis
        analysis_parts = parts[0].split("\n\n")
        general_analysis = analysis_parts[-1] if len(analysis_parts) > 2 else parts[0]
        logger.info(f"Análise geral extraída:\n{general_analysis}")
        
        habits = []
        if len(parts) > 1:
            logger.info(f"Processando {len(parts)-1} hábitos encontrados...")
            for i, habit_text in enumerate(parts[1:], 1):
                try:
                    logger.info(f"\n=== Processando hábito {i} ===")
                    logger.info(f"Texto bruto do hábito:\n{habit_text}")
                    
                    lines = habit_text.strip().split("\n")
                    logger.info(f"Linhas do hábito:\n{lines}")
                    
                    # Extract habit name
                    habit_name = lines[0].split(": ", 1)[-1].strip()
                    logger.info(f"Nome do hábito extraído: {habit_name}")
                    
                    # Extract description
                    desc_line = next((l for l in lines if "Description:" in l), "")
                    description = desc_line.replace("**Description:** ", "").strip()
                    logger.info(f"Descrição extraída: {description}")
                    
                    # Extract implementation steps
                    implementation = []
                    for line in lines:
                        if line.strip().startswith(("1. ", "2. ", "3. ")):
                            step = line.strip().split(". ", 1)[-1]
                            implementation.append(step)
                    logger.info(f"Passos de implementação extraídos: {implementation}")
                    
                    # Extract scientific basis
                    basis_line = next((l for l in lines if "Basis:" in l), "")
                    scientific_basis = basis_line.replace("- **Basis:** ", "").strip()
                    logger.info(f"Base científica extraída: {scientific_basis}")
                    
                    habit = {
                        "name": habit_name or "Habit",
                        "description": description or "Practice this habit regularly",
                        "implementation": implementation or ["Start small", "Be consistent", "Track progress"],
                        "scientific_basis": scientific_basis or "Based on behavioral psychology principles"
                    }
                    habits.append(habit)
                    logger.info(f"Hábito {i} processado com sucesso: {habit}")
                    
                except Exception as e:
                    logger.error(f"Erro ao processar hábito {i}: {str(e)}")
                    continue
        else:
            logger.warning("Nenhum hábito encontrado no texto da IA")
            logger.info("Verificando se há palavras-chave de hábitos no texto...")
            # Aqui podemos adicionar lógica para extrair hábitos do texto geral se necessário
        
        if not habits:
            logger.warning("Nenhum hábito encontrado ou extraído, adicionando hábitos padrão")
            habits = [
                {
                    "name": "Gradual Exposure",
                    "description": "Start with small, manageable steps",
                    "implementation": [
                        "Begin with brief interactions",
                        "Practice in comfortable settings",
                        "Gradually increase challenge"
                    ],
                    "scientific_basis": "Based on exposure therapy and behavioral activation"
                },
                {
                    "name": "Self-Monitoring",
                    "description": "Track your progress and patterns",
                    "implementation": [
                        "Keep a daily log",
                        "Note triggers and responses",
                        "Review and adjust strategies"
                    ],
                    "scientific_basis": "Based on cognitive behavioral therapy principles"
                }
            ]
        
        formatted_response = {
            "general_analysis": general_analysis.strip(),
            "recommended_habits": habits
        }
        
        logger.info("=== Formatação concluída ===")
        logger.info(f"Resposta final formatada:\n{json.dumps(formatted_response, indent=2)}")
        return formatted_response
        
    except Exception as e:
        logger.error(f"Erro na formatação da resposta: {str(e)}", exc_info=True)
        return {
            "general_analysis": content,
            "recommended_habits": [
                {
                    "name": "Default Habit",
                    "description": "A basic habit to get started",
                    "implementation": ["Start small", "Be consistent", "Track progress"],
                    "scientific_basis": "Based on behavioral psychology principles"
                }
            ]
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
        logger.debug(f"Prompt formatado: {formatted_prompt}")
        
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
        logger.debug(f"Resposta bruta do LLM: {response.content}")
        
        # Format the response
        logger.info("Formatando resposta...")
        formatted_response = format_ai_response(response.content)
        logger.debug(f"Resposta formatada: {formatted_response}")
        
        # Save to contract
        logger.info("Preparando dados para salvar no contrato...")
        msg = {
            "save_analysis": {
                "patient_id": data.patient_id,
                "content": json.dumps(formatted_response)  # Save formatted JSON
            }
        }
        logger.debug(f"Mensagem para o contrato: {msg}")
        
        logger.info("Executando transação no contrato...")
        tx = wallet.execute_tx(
            CONTRACT_ADDRESS,
            msg,
            memo="Save analysis",
        )
        logger.info(f"Transação executada com sucesso. Hash: {tx.txhash}")
        
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
        
        # Usa a chave estática definida
        return {"viewing_key": STATIC_VIEWING_KEY, "tx_hash": tx.txhash}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating viewing key: {str(e)}")

@app.get("/analyses/{patient_id}", response_model=GetAnalysesResponse)
async def get_analyses(patient_id: str, viewing_key: str):
    try:
        logger.info(f"Recebendo requisição de análises para patient_id: {patient_id}")
        
        try:
            # Tenta buscar do contrato
            result = secret.wasm.contract_query(
                contract_address=CONTRACT_ADDRESS,
                query={
                    "get_analyses": {
                        "patient_id": patient_id,
                        "viewing_key": viewing_key
                    }
                }
            )

            logger.info(f"Análises encontradas: {result}")
            
            # Se encontrou análise, verifica se precisa adicionar hábitos
            if result and len(result) > 0:
                for analysis in result:
                    content = json.loads(analysis["content"])
                    if not content.get("recommended_habits"):
                        # Adiciona hábitos recomendados baseados na análise existente
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
            logger.error(f"Erro ao conectar com o contrato: {str(contract_error)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error retrieving analyses from contract: {str(contract_error)}"
            )
            
    except Exception as e:
        logger.error(f"Erro ao processar requisição de análises: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving analyses: {str(e)}"
        )

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

# Inicialização da aplicação
if __name__ == "__main__":
    try:
        load_dotenv()
        logger.info("Variáveis de ambiente carregadas")
    except Exception as e:
        logger.error(f"Erro ao carregar variáveis de ambiente: {str(e)}")
    
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True) 