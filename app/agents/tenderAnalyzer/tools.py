from langchain.tools import tool
import httpx

@tool
async def validateRuc(ruc: str) -> dict:
    """
    Validates an Ecuadorian RUC by calling the official SRI public API.
    It extracts and returns the bidder's name, status, and primary economic activity.
    """
    print(f"--- 🛠️ TOOL CALLED: validateRuc with RUC: {ruc} ---")
    
    url = f"https://srienlinea.sri.gob.ec/sri-catastro-sujeto-servicio-internet/rest/ConsolidadoContribuyente/obtenerPorNumerosRuc?&ruc={ruc}"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=10.0)
            response.raise_for_status()
            data = response.json()
            
            if not data:
                return {"error": "No data returned from SRI for this RUC."}

            contributor_info = data[0]
            
            return {
                "bidderName": contributor_info.get("razonSocial"),
                "status": contributor_info.get("estadoContribuyenteRuc"),
                "economicActivity": contributor_info.get("actividadEconomicaPrincipal")
            }
            
    except httpx.HTTPStatusError as e:
        print(f"--- TOOL ERROR: HTTP error validating RUC {ruc}: {e} ---")
        return {"error": f"Failed to validate RUC. API returned status: {e.response.status_code}"}
    except Exception as e:
        print(f"--- TOOL ERROR: An unexpected error occurred: {e} ---")
        return {"error": f"An unexpected error occurred while validating RUC: {e}"}