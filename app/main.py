from fastapi import FastAPI, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.database import get_db, Base, engine
from contextlib import asynccontextmanager
import time
import os

# Create database tables
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")
    yield

app = FastAPI(
    title="Tender Insight Hub API",
    description="API for the Tender Insight Hub SaaS platform",
    version="1.0.0",
    lifespan=lifespan
)

# Include routers
from app.routes import tenders, company
app.include_router(tenders.router)
app.include_router(company.router)

# Read the HTML template
def read_html_template():
    template_path = os.path.join(os.path.dirname(__file__), 'templates', 'index.html')
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
            "company": "/api/company/profile"
        }
    }

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    try:
        # Test database connection
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
    """
    Debug endpoint to test client-side search
    """
    from app.services.ocds_service import ocds_service
    
    try:
        # Get results with client-side filtering
        results = ocds_service.search_tenders(keywords)
        
        # Extract useful info for debugging
        tender_info = []
        for result in results[:5]:  # First 5 results
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
    """
    Debug endpoint to see what tenders are actually available from API
    """
    from app.services.ocds_service import ocds_service
    
    try:
        # Get all tenders without filtering
        all_tenders = ocds_service.search_tenders("")
        
        # Extract useful information about what's available
        tender_samples = []
        for tender in all_tenders[:limit]:
            tender_data = tender.get('tender', {})
            items = []
            for item in tender_data.get('items', [])[:3]:  # First 3 items
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)