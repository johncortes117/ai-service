# services/analysis_service.py

import asyncio
from typing import Dict, Any

# Importamos el agente y las funciones de los otros servicios
# Asegúrate de que la ruta de importación a tu carpeta 'agents' sea correcta
# desde la perspectiva de la carpeta 'services'.
from app.agents.tenderAnalyzer.mainGraph import agentGraph  

from . import tender_service, sse_service

async def run_analysis_and_notify(tender_id: str, input_data: Dict[str, Any]):
    """
    This is the core background task. It runs the full agent graph and,
    when finished, sends the final report to the SSE endpoint.
    """
    print(f"--- 🤖 AGENT: Starting analysis for tender_id: {tender_id} ---")
    
    try:
        # Aquí es donde se invoca al agente con los datos de entrada
        final_state = await agentGraph.ainvoke(input_data)
        
        # El agente, en su último nodo, guarda el resultado en la clave 'finalReport'
        report_json = final_state.get("finalReport")

        if report_json:
            print(f"--- 🤖 AGENT: Analysis for tender {tender_id} completed successfully. ---")
            
            # Actualizamos el estado para que el frontend sepa que se completó
            # y enviamos el reporte completo.
            report_json['state'] = 'Completado'
            report_json['tenderId'] = tender_id
            
            # Notificamos al frontend enviando el resultado al endpoint de SSE
            sse_service.save_sse_data(report_json)
            print(f"--- 📡 SSE: Notification with final report sent for tender {tender_id}. ---")
        else:
            print(f"--- 🤖 AGENT ERROR: Analysis for tender {tender_id} finished but produced no finalReport. ---")
            error_payload = {
                "state": "Error",
                "tenderId": tender_id,
                "errorDetails": "The agent finished but did not produce a final report."
            }
            sse_service.save_sse_data(error_payload)

    except Exception as e:
        print(f"--- 💥 AGENT CRITICAL ERROR: Analysis for tender {tender_id} failed: {e} ---")
        # Enviamos una notificación de error al frontend
        error_payload = {
            "state": "Error",
            "tenderId": tender_id,
            "errorDetails": str(e)
        }
        sse_service.save_sse_data(error_payload)


async def start_tender_analysis(tender_id: str):
    """
    This is the main orchestrator function called by the API endpoint.
    It fetches data, starts the analysis in the background, and returns immediately.
    """
    print(f"--- Orchestrator: Kicking off analysis for tender_id: {tender_id} ---")
    
    # 1. Obtener los datos necesarios usando el servicio que ya teníamos
    try:
        json_data = await tender_service.generate_full_tender_json(tender_id)
        if not json_data.get("tenderText") or json_data.get("tenderText").strip() == "":
            return {"error": f"Could not start analysis. Tender text for ID {tender_id} is missing or empty."}
    except Exception as e:
        return {"error": f"Failed to fetch data for analysis: {e}"}

    # 2. Preparar el diccionario de entrada para el agente
    agent_input = {
        "tenderText": json_data["tenderText"],
        "proposals": json_data["proposals"]
    }
    
    # 3. Lanzar la tarea de análisis en segundo plano
    #    No usamos 'await' aquí para que la respuesta de la API sea inmediata.
    #    La tarea se ejecutará de forma independiente.
    asyncio.create_task(run_analysis_and_notify(tender_id, agent_input))
    
    # 4. Enviar una primera notificación para que el frontend sepa que el proceso comenzó
    initial_payload = {
        "state": "En Análisis",
        "isLoading": True,
        "tenderId": tender_id,
        "message": f"El análisis para la licitación {tender_id} ha comenzado. Esto puede tardar varios minutos."
    }
    sse_service.save_sse_data(initial_payload)
    
    # 5. Retornar una respuesta inmediata al usuario
    return {"message": "Analysis process started successfully. You will be notified via SSE upon completion."}
    
    
    
    
    
    
    
    
    
    
    