import json
import time
import asyncio
from datetime import datetime
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


def emit_progress_event(
    tender_id: str,
    event_type: str,
    progress: int,
    message: str,
    node_name: str = None
) -> None:
    """
    Emits a progress event to the SSE stream.
    
    Args:
        tender_id: ID of the tender being analyzed
        event_type: Type of event ('progress', 'node_complete', 'error', 'complete')
        progress: Progress percentage (0-100)
        message: Human-readable message
        node_name: Optional name of the graph node
    """
    event_data = {
        "event_type": event_type,
        "tender_id": tender_id,
        "progress": progress,
        "message": message,
        "timestamp": datetime.now().isoformat(),
    }
    
    if node_name:
        event_data["node_name"] = node_name
    
    # Merge with existing data to preserve state
    try:
        if constants.SSE_DATA_FILE.exists():
            with open(constants.SSE_DATA_FILE, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
        else:
            existing_data = {}
        
        # Update with new event data
        existing_data.update({
            "state": "En Análisis" if event_type != "complete" else "Completado",
            "isLoading": event_type != "complete",
            "tenderId": tender_id,
            "currentProgress": progress,
            "currentStep": message,
            "lastUpdate": event_data["timestamp"]
        })
        
        # Save updated data
        save_sse_data(existing_data)
        
    except Exception as e:
        print(f"Error emitting progress event: {e}")


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
                    yield f"data: {json.dumps(current_data, ensure_ascii=False)}\n\n"
                    last_state = current_data
            # Si no hay datos o no han cambiado, no se envía nada para ahorrar ancho de banda
            # El cliente simplemente mantiene la conexión abierta
        except (json.JSONDecodeError, FileNotFoundError):
            # If file is being written or not found, yield an empty message or a specific state
            yield "data: {}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        # Usamos asyncio.sleep en una función asíncrona para no bloquear el servidor
        await asyncio.sleep(2)


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


def get_current_analysis_status(tender_id: str = None) -> Dict[str, Any]:
    """
    Gets the current analysis status from the SSE data file.
    
    Args:
        tender_id: Optional tender ID to filter by
        
    Returns:
        Dictionary with current status information
    """
    if not constants.SSE_DATA_FILE.exists():
        return {
            "status": "pending",
            "progress": 0,
            "message": "No analysis in progress"
        }
    
    try:
        with open(constants.SSE_DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # If tender_id is provided, check if it matches
        if tender_id and data.get("tenderId") != tender_id:
            return {
                "status": "pending",
                "progress": 0,
                "message": f"No analysis found for tender {tender_id}"
            }
        
        state = data.get("state", "pending")
        status_map = {
            "En Análisis": "processing",
            "Completado": "completed",
            "Error": "failed"
        }
        
        return {
            "tender_id": data.get("tenderId"),
            "status": status_map.get(state, "pending"),
            "progress": data.get("currentProgress", 0),
            "current_step": data.get("currentStep"),
            "message": data.get("message", ""),
            "last_update": data.get("lastUpdate")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading status: {e}")