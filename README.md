# HACKIATHON
## Cómo levantar el proyecto

1. **Instala las dependencias:**
   
	```powershell
	poetry install
	```

2. **Configura las variables de entorno:**
   
	Copia `.env.example` a `.env` y ajusta los valores según tu entorno.

3. **Levanta el servidor de desarrollo:**
   
	```powershell
	poetry run uvicorn app.api.main:app --host 127.0.0.1 --port 8000
	```

4. **Accede a la documentación interactiva:**
   
	- [http://localhost:8000/docs](http://localhost:8000/docs) (Swagger UI)
	- [http://localhost:8000/redoc](http://localhost:8000/redoc) (ReDoc)

---


# Documentación del Proyecto `ai-service`

## Descripción General

`ai-service` es una API backend desarrollada con FastAPI para la gestión de licitaciones (tenders), propuestas y análisis documental. Incluye endpoints para subir archivos, procesar PDFs y ZIPs, transmitir datos en tiempo real mediante SSE, y generar resúmenes ejecutivos.

---

## Estructura de Carpetas

```
ai-service/
├── app/
│   ├── api/
│   │   ├── main.py                # Entrypoint principal de la API FastAPI
│   │   ├── schemas.py             # Esquemas Pydantic para validación y respuesta
│   │   ├── service_utils.py       # Utilidades para SSE, transición de estado y manejo de archivos
│   │   ├── utils/
│   │   │   ├── __init__.py        # Exposición de utilidades y wrappers
│   │   │   ├── proposal_utils.py  # Funciones para manejo de propuestas
│   │   │   ├── pdf_json_utils.py  # Funciones para extracción de texto de PDFs
│   │   ├── services/
│   │   │   ├── sse_service.py     # Lógica específica para SSE
│   │   │   ├── tender_service.py  # Lógica específica para tenders
│   ├── core/
│   │   ├── config.py              # Configuración global (CORS, límites, etc.)
│   │   ├── constants.py           # Constantes globales
├── data/
│   ├── sse_data.json              # Archivo fuente para eventos SSE
│   ├── proposals/                 # Propuestas organizadas por tender y contratista
│   ├── tenders/                   # PDFs de licitaciones
│   ├── temp_files/                # Archivos temporales
├── output_agent.json              # Salida de agentes de análisis
├── pyproject.toml                 # Configuración de dependencias (Poetry)
├── README.md                      # Documentación general
```

---

## Endpoints Principales

### 1. `/save_sse_data` [POST]
- **Función:** Recibe un JSON y lo guarda en `sse_data.json` para transmisión SSE.
- **Body:** `{ ... }` (estructura flexible)
- **Respuesta:** `{ "message": "Data saved successfully" }`

### 2. `/stream_sse` [GET]
- **Función:** Transmite los datos de `sse_data.json` como eventos SSE.
- **Respuesta:** Stream de eventos SSE.

### 3. `/tender/executive_summary` [GET]
- **Función:** Verifica si el estado del tender cambió de "En Análisis" a "Completado" y retorna el resumen ejecutivo.
- **Respuesta:** `{ "executiveSummary": ... }` o mensaje de estado.

### 4. `/tenders/upload` [POST]
- **Función:** Sube un PDF de licitación y crea un nuevo tender.
- **Body:** Archivo PDF.
- **Respuesta:** Detalles del tender creado.

### 5. `/proposals/upload_differentiated/{tender_id}/{contractor_id}/{company_name}` [POST]
- **Función:** Sube archivos de propuesta y anexos, organizados por tender, contratista y empresa.
- **Body:** Archivos principales y anexos.
- **Respuesta:** Detalles de la propuesta subida.

---

## Esquemas de Datos

### Propuesta (`proposals/`)
```
data/proposals/
└── tender_{id}/
		└── contractor_{id}/
				└── {company_name}/
						├── PRINCIPAL_{uuid}.pdf
						├── ATTACHMENT_{uuid}.pdf
						└── ...
```

### Licitación (`tenders/`)
```
data/tenders/
└── tender_{id}/
		└── TENDER_{id}.pdf
```

### SSE Data (`sse_data.json`)
```json
{
	"state": "En Análisis",
	"isLoading": true,
	"analysisResult": {
		"executiveSummary": "Resumen ejecutivo...",
		...
	}
}
```

---

## Utilidades y Servicios

- **service_utils.py:** Funciones para guardar y transmitir datos SSE, y detectar transición de estado.
- **proposal_utils.py:** Funciones para crear estructura de propuestas, guardar archivos y obtener contratistas.
- **pdf_json_utils.py:** Extracción de texto y páginas de PDFs.
- **sse_service.py / tender_service.py:** Lógica especializada para SSE y tenders.

---

## Flujo de Trabajo

1. **Subida de archivos:** Los usuarios suben PDFs de licitaciones y propuestas mediante los endpoints correspondientes.
2. **Procesamiento:** Los archivos se procesan y almacenan en la estructura de carpetas definida.
3. **Transmisión SSE:** Los cambios en el estado o resultados de análisis se transmiten en tiempo real usando SSE.
4. **Consulta de resúmenes:** Los usuarios pueden consultar el resumen ejecutivo cuando el estado del tender cambia.

---

## Configuración

- Variables de entorno en `.env.example`.
- Dependencias gestionadas con Poetry (`pyproject.toml`).

---

¿Necesitas la documentación en formato Markdown, PDF, o como endpoint `/docs`? ¿Quieres que incluya ejemplos de request/response?