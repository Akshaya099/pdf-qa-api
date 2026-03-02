from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import upload, query, pdf

# -------------------- App Initialization -------------------- #

app = FastAPI(
    title="PDF QA Service",
    description="""

🔐 Authentication Required
--------------------------

### How to Authorize:

1️⃣ Click the **Authorize 🔒** 

2️⃣ Enter your token (example):

    my_secure_token

3️⃣ Click **Authorize** and close the dialog.

✅ You can now access protected endpoints.

---
**Note:**

Authorize once using the 🔒 button. the token will be sent automatically with future requests.


"""
)

# -------------------- CORS Configuration -------------------- #
# Allows frontend applications to access this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://pdf-qa-api-indol.vercel.app"],  # production frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------- Include Routers -------------------- #

app.include_router(upload.router)
app.include_router(query.router)
app.include_router(pdf.router)