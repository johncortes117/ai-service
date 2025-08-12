# services/sse_service.py
import json
import time
from typing import Dict, Any, AsyncGenerator
from fastapi import HTTPException

from app.core import constants

def save_sse_data(payload: Dict[str, Any]) -> Dict[str, str]:
    """Saves the received JSON to the SSE data file."""
    try:
        # Abre el archivo definido en constants.py en modo escritura ("w")
        # Esto sobrescribe el archivo si ya existe, o lo crea si no.
        with open(constants.SSE_DATA_FILE, "w", encoding="utf-8") as f:
            # Escribe el diccionario 'payload' en el archivo, con formato legible
            json.dump(payload, f, ensure_ascii=False, indent=2)
        
        # Devuelve una respuesta de éxito
        return {"message": "Data saved successfully for SSE streaming."}
    except Exception as e:
        # Si algo sale mal al escribir el archivo, lanza un error 500
        raise HTTPException(status_code=500, detail=f"Error saving SSE data: {e}")

async def stream_sse_data() -> AsyncGenerator[str, None]:
    """Streams data from the JSON file as Server-Sent Events."""
    last_state = {}
    while True:
        try:
            if constants.SSE_DATA_FILE.exists():
                with open(constants.SSE_DATA_FILE, "r", encoding="utf-8") as f:
                    current_data = json.load(f)
                
                # Send data only if it has changed to avoid unnecessary traffic
                if current_data != last_state:
                    yield f"data: {json.dumps(current_data)}\n\n"
                    last_state = current_data
        except (json.JSONDecodeError, FileNotFoundError):
            # If file is being written or not found, send an empty message
            yield "data: {}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        await asyncio.sleep(2) # Use asyncio.sleep in an async function

def get_executive_summary_if_completed() -> Dict[str, Any]:
    """Checks if state transitioned and returns the executive summary."""
    if not constants.SSE_DATA_FILE.exists():
        return {"message": "Analysis data not available yet."}
    
    try:
        with open(constants.SSE_DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        current_state = data.get("state") or (data.get("tenderDetails", {})).get("state")
        
        if current_state == "Completado":
            summary = (data.get("analysisResult", {})).get("executiveSummary")
            return {"executiveSummary": summary} if summary else {"message": "Analysis completed, but no executive summary found."}
        else:
            return {"message": f"Analysis not yet complete. Current state: {current_state or 'Unknown'}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading analysis data: {e}")