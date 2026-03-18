from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI

from app.api.routes import interview, resume

app = FastAPI(title="JobFinder")

app.include_router(resume.router, prefix="/api/v1")
app.include_router(interview.router, prefix="/api/v1")
