from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.models.database import engine, Base
from app.routers import auth, agencies, kpis, targets, results, reviews, actions, users, countries, dashboard

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Agency Performance Tracker API",
    description="REST API for Agency Performance Tracking System",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(agencies.router, prefix="/api/agencies", tags=["Agencies"])
app.include_router(kpis.router, prefix="/api/kpis", tags=["KPIs"])
app.include_router(targets.router, prefix="/api/targets", tags=["Targets"])
app.include_router(results.router, prefix="/api/results", tags=["Results"])
app.include_router(reviews.router, prefix="/api/reviews", tags=["Reviews"])
app.include_router(actions.router, prefix="/api/actions", tags=["Action Items"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(countries.router, prefix="/api/countries", tags=["Countries"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])

@app.get("/")
def root():
    return {"message": "Agency Performance Tracker API", "version": "1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
