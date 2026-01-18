
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
import joblib
import pandas as pd
import numpy as np
from prometheus_fastapi_instrumentator import Instrumentator
import mlflow
from retraining_flow import retraining_flow

app = FastAPI(title="Student Failure Risk API")

# Setup Prometheus
Instrumentator().instrument(app).expose(app)

# Setup MLFlow
mlflow.set_tracking_uri("http://mlflow:5000")
mlflow.set_experiment("api_inference")

# Load Model (Find latest version)
import glob
import os

try:
    model_files = glob.glob("model_*.pkl")
    if model_files:
        # Sort by modification time (latest first)
        latest_model = max(model_files, key=os.path.getctime)
        print(f"Loading latest model: {latest_model}")
        model = joblib.load(latest_model)
        model_version = latest_model.replace("model_", "").replace(".pkl", "")
    else:
        print("No model file found (model_*.pkl).")
        model = None
        model_version = "none"
except Exception as e:
    print(f"Error loading model: {e}")
    model = None
    model_version = "error"

# ... (StudentData class remains unchanged)

class StudentData(BaseModel):
    school: str
    sex: str
    age: int
    address: str
    famsize: str
    Pstatus: str
    Medu: int
    Fedu: int
    Mjob: str
    Fjob: str
    reason: str
    guardian: str
    traveltime: int
    studytime: int
    failures: int
    schoolsup: str
    famsup: str
    paid: str
    activities: str
    nursery: str
    higher: str
    internet: str
    romantic: str
    famrel: int
    freetime: int
    goout: int
    Dalc: int
    Walc: int
    health: int
    absences: int
    G1: int
    G2: int

@app.get("/")
def health_check():
    return {"status": "ok", "model_loaded": model is not None, "model_version": model_version}

@app.post("/predict")
def predict(data: StudentData):
    if not model:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    input_data = data.dict()
    
    # Feature Engineering mirroring training time
    input_data['TotalAlc'] = input_data['Dalc'] + input_data['Walc']
    input_data['ParentEdu'] = input_data['Medu'] + input_data['Fedu']
    input_data['HasFailed'] = 1 if input_data['failures'] > 0 else 0
    
    df = pd.DataFrame([input_data])
    
    try:
        prediction = model.predict(df)[0]
        
        # Log to MLFlow
        try:
            with mlflow.start_run(run_name="prediction_request"):
                mlflow.log_params(input_data)
                mlflow.log_metric("prediction_G3", float(prediction))
                mlflow.set_tag("model_version", model_version)
        except Exception as e:
            print(f"MLFlow logging failed: {e}")

        return {"prediction_G3": float(prediction)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/retrain")
async def trigger_retrain(background_tasks: BackgroundTasks):
    """
    Trigger the model retraining flow in the background.
    """
    background_tasks.add_task(retraining_flow)
    return {"status": "Retraining started in background"}
