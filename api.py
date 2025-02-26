from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from secret_ai_sdk.secret_ai import ChatSecret
from secret_ai_sdk.secret import Secret
import os
import uvicorn
from prompt_templates import ANALYZE_AND_SUGGEST_PROMPT
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Behavioral Analysis API",
    description="API for behavioral analysis using Secret AI",
    version="1.0.0"
)

# Get Secret AI API key from environment variable
api_key = os.getenv("SECRET_AI_API_KEY")
if not api_key:
    raise ValueError("SECRET_AI_API_KEY environment variable is not set")

# Initialize Secret AI client
secret_client = Secret()
models = secret_client.get_models()
urls = secret_client.get_urls(model=models[0])
secret_ai_llm = ChatSecret(
    base_url=urls[0],
    model=models[0],
    temperature=1.0
)

# Define data models
class BehaviorData(BaseModel):
    behavior: str
    antecedent: str
    consequence: str
    previous_attempts: str

class AnalysisResponse(BaseModel):
    analysis: str

class HabitTrack(BaseModel):
    user_id: str
    habit_id: str
    date: str
    completed: bool
    notes: Optional[str] = None

# Mock database (to be replaced with blockchain integration)
analysis_db = {}
habit_tracks_db = []

# Routes
@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_behavior(data: BehaviorData):
    try:
        # Format the prompt with the behavior data
        formatted_prompt = ANALYZE_AND_SUGGEST_PROMPT.format(**data.dict())
        
        # Define messages for the LLM
        messages = [
            (
                "system",
                "You are a psychologist specializing in behavioral analysis and radical behaviorism. Provide accurate analyses and practical suggestions based on scientific evidence."
            ),
            ("human", formatted_prompt),
        ]
        
        # Invoke the LLM
        response = secret_ai_llm.invoke(messages, stream=False)
        
        # Store in mock database (to be replaced with blockchain)
        analysis_id = len(analysis_db) + 1
        analysis_db[analysis_id] = {
            "data": data.dict(),
            "analysis": response.content
        }
        
        return {"analysis": response.content}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating analysis: {str(e)}")

@app.get("/analyses", response_model=Dict[str, Any])
async def list_analyses():
    # This would be replaced with blockchain query in the future
    return {"message": "Future endpoint for listing analyses from blockchain", "data": analysis_db}

@app.post("/track-habit", response_model=Dict[str, Any])
async def track_habit(habit_track: HabitTrack):
    # This would be replaced with blockchain storage in the future
    habit_tracks_db.append(habit_track.dict())
    return {"message": "Habit tracking recorded successfully", "data": habit_track.dict()}

@app.get("/")
async def root():
    return {"message": "Welcome to the Behavioral Analysis API"}

# Run the application
if __name__ == "__main__":
    uvicorn.run("secret_ai_getting_started_api:app", host="0.0.0.0", port=8000, reload=True) 