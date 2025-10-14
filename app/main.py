from fastapi import FastAPI, Depends, Request, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from app.mongodb import mongodb 
from app.database import get_db, Base, engine
from contextlib import asynccontextmanager
import time
import os
import shutil

from fastapi.middleware.cors import CORSMiddleware

# Import existing routers
from app.routes import company, auth, tenders, tender_summarize, workspace

# Import summarization services
from app.services.tender_doc_services import (
    extract_text_from_pdf,
    extract_text_from_zip,
    summarize_text,
    highlight_key_points
)


# Create database tables
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create SQL tables on startup
    print("Creating SQL database tables...")
    Base.metadata.create_all(bind=engine)
    print("SQL database tables created successfully!")
    
    # Initialize MongoDB
    print("Initializing MongoDB...")
    await mongodb.connect()
    
    yield
    
    # Cleanup on shutdown
    await mongodb.close()

app = FastAPI(
    title="Tender Insight Hub API",
    description="API for the Tender Insight Hub SaaS platform",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:8001",
        "http://127.0.0.1:8001"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    print("🚀 Starting Tender Insight Hub...")
    # Connect to MongoDB
    await mongodb.connect()
    print("✅ All services initialized")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    await mongodb.close()
    print("👋 Services shut down")

# Include routers
app.include_router(tenders.router)
app.include_router(company.router)
app.include_router(auth.router)
app.include_router(tender_summarize.router) 
app.include_router(
    workspace.router, 
    prefix="/api/workspace", 
    tags=["workspace"]
)

# Mount static files directory
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Read the HTML template
def read_html_template():
    template_path = os.path.join(os.path.dirname(__file__), 'templates', 'base.html')
    with open(template_path, 'r', encoding='utf-8') as f:
        return f.read()

html_template = read_html_template()

@app.get("/")
async def root():
    return {
        "message": "Tender Insight Hub API is running!",
        "timestamp": time.time(),
        "endpoints": {
            "web_ui": "/ui",
            "api_docs": "/docs",
            "health": "/health",
            "tenders": "/api/tenders/search",
            "company": "/api/company/profile",
            "summarize_tender": "/api/tenders/summarize"
        }
    }

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    try:
        db.execute("SELECT 1")
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": time.time()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
            "timestamp": time.time()
        }

@app.get("/test")
async def test_endpoint():
    """Simple test endpoint without database dependency"""
    return {
        "message": "Test endpoint works!",
        "timestamp": time.time()
    }

@app.get("/ui", response_class=HTMLResponse)
async def serve_ui():
    """Serve the main web interface"""
    return HTMLResponse(content=html_template)

@app.get("/api/debug/search-test")
async def debug_search_test(keywords: str = "construction"):
    from app.services.ocds_service import ocds_service
    try:
        results = ocds_service.search_tenders(keywords)
        tender_info = []
        for result in results[:5]:
            tender = result.get('tender', {})
            tender_info.append({
                "title": tender.get('title', 'No title'),
                "description": tender.get('description', '')[:100] + "..." if tender.get('description') else 'No description',
                "buyer": tender.get('procuringEntity', {}).get('name', 'Unknown'),
            })
        return {
            "success": True,
            "search_keywords": keywords,
            "total_results": len(results),
            "sample_results": tender_info,
            "message": "Using client-side filtering since API search is broken"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "search_keywords": keywords
        }

@app.get("/api/debug/available-tenders")
async def debug_available_tenders(limit: int = 20):
    from app.services.ocds_service import ocds_service
    try:
        all_tenders = ocds_service.search_tenders("")
        tender_samples = []
        for tender in all_tenders[:limit]:
            tender_data = tender.get('tender', {})
            items = []
            for item in tender_data.get('items', [])[:3]:
                items.append({
                    "description": item.get('description', ''),
                    "classification": item.get('classification', {}).get('description', '')
                })
            tender_samples.append({
                "title": tender_data.get('title', 'No title'),
                "description": tender_data.get('description', '')[:100] + "..." if tender_data.get('description') else 'No description',
                "buyer": tender_data.get('procuringEntity', {}).get('name', 'Unknown'),
                "value": tender_data.get('value', {}).get('amount', 0),
                "items": items
            })
        return {
            "success": True,
            "total_available": len(all_tenders),
            "sample_tenders": tender_samples,
            "message": "These are the actual tenders available from the API. Use these to find relevant search terms."
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

# Serve partial templates
@app.get("/tender-search-partial", response_class=HTMLResponse)
async def tender_search_partial():
    template_path = os.path.join(os.path.dirname(__file__), 'templates', 'partials', 'index.html')
    with open(template_path, 'r', encoding='utf-8') as f:
        return HTMLResponse(content=f.read())

@app.get("/company-profile-partial", response_class=HTMLResponse)
async def company_profile_partial():
    template_path = os.path.join(os.path.dirname(__file__), 'templates', 'partials', 'company.html')
    with open(template_path, 'r', encoding='utf-8') as f:
        return HTMLResponse(content=f.read())

@app.get("/register-partial", response_class=HTMLResponse)
async def register_partial():
    template_path = os.path.join(os.path.dirname(__file__), 'templates', 'partials', 'register.html')
    with open(template_path, 'r', encoding='utf-8') as f:
        return HTMLResponse(content=f.read())

@app.get("/login-partial", response_class=HTMLResponse)
async def login_partial():
    template_path = os.path.join(os.path.dirname(__file__), 'templates', 'partials', 'login.html')
    with open(template_path, 'r', encoding='utf-8') as f:
        return HTMLResponse(content=f.read())

# Main SPA route
@app.get("/app", response_class=HTMLResponse)
async def serve_spa():
    with open("app/templates/base.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

# ---------------------------
# Tender Document Summarization Endpoint (direct integration as optional)
# ---------------------------


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
