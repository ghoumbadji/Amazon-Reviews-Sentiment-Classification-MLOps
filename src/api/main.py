"""API for inference tasks."""

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from tensorflow import keras
from src.model.model_pipeline import run_model_pipeline
from src.data.clean_transform import clean_text
from src.api.model_loader import ModelLoader


# Define the loader class
loader = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Define the Lifespan Context Manager"""
    global loader
    print("Loading model...")
    loader = ModelLoader().get_instance()
    yield # The application runs while waiting here    
    print("Shutting down...")


# Define the app (API)
app = FastAPI(title="Sentiment Analysis API", lifespan=lifespan)


# Input data schema
class PredictionRequest(BaseModel):
    content: str


# Endpoint Health
@app.get("/health")
def health_check():
    if loader.model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    return {"status": "ok", "model_loaded": True}


# Endpoint Predict
@app.post("/predict")
def predict(request: PredictionRequest):
    if not loader.model:
        raise HTTPException(status_code=503, detail="Model service unavailable")
    # Preprocessing
    cleaned_text = clean_text(request.content)
    sequences = loader.tokenizer.texts_to_sequences([cleaned_text])
    padded = keras.utils.pad_sequences(sequences, maxlen=128, padding="post", truncating="post")
    # Inference
    prediction = loader.model.predict(padded)
    score = float(prediction[0][0])
    label = "POSITIVE" if score > 0.5 else "NEGATIVE"
    # Enriched return (label + trust)
    return {
        "label": label,
        "confidence": score,
    }


# Endpoint Metrics
@app.get("/metrics")
def get_metrics():
    """Display metrics loaded from S3."""
    if not loader.metrics:
        raise HTTPException(status_code=404, detail="Metrics not found")
    return {
        "model_performance": loader.metrics, # JSON file content
        "system_info": {"status": "live", "api_version": "v1"}
    }


# Endpoint Train
@app.post("/train")
def trigger_training(background_tasks: BackgroundTasks):
    """Start retraining in the background."""
    background_tasks.add_task(run_model_pipeline)
    return {"message": "Training pipeline triggered in background"}
