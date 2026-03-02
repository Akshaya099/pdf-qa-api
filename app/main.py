from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


from app.api.routes import upload, query

from app.api.routes import pdf


# -------------------- App Initialization -------------------- #

app = FastAPI(title="PDF QA Service")

# CORS configuration (allow frontend access)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # change in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------- Include Routers -------------------- #

app.include_router(upload.router)
app.include_router(query.router)
# app.include_router(pdf_router)
app.include_router(pdf.router)