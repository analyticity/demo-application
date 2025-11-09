from bp_api.data_loader import DataLoader
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from bp_api.routers import accidents, charts, waze

data_loader = DataLoader()

async def lifespan(app: FastAPI):
    data_loader.load_waze()
    data_loader.load_accidents_file()
    data_loader.create_matched_tables()
    yield

app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost:5173",
    "http://localhost:5174",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(accidents.router, prefix="/api/v1/accidents", tags=["Accidents"])
app.include_router(waze.router, prefix="/api/v1/waze", tags=["Waze Reports"])
app.include_router(charts.router, prefix="/api/v1/charts", tags=["Charts"])


@app.get("/")
def read_root():
    return {"message": "Welcome to the Accident Tracking API!"}
