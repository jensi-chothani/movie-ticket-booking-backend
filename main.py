from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import (
    auth,
    movies,
    users,
    screens,
    shows,
    bookings,
    payments,
    offers,
    ratings,
    admin,
    trending,
    cinemas,
    stripe_routes 

)


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(movies.router, prefix="/v1")
app.include_router(users.router, prefix="/v1")
app.include_router(screens.router, prefix="/v1")
app.include_router(shows.router, prefix="/v1")
app.include_router(bookings.router, prefix="/v1")
app.include_router(payments.router, prefix="/v1")
app.include_router(offers.router, prefix="/v1")
app.include_router(ratings.router, prefix="/v1")
app.include_router(admin.router, prefix="/v1")
app.include_router(trending.router, prefix="/v1")
app.include_router(cinemas.router, prefix="/v1")
app.include_router(stripe_routes.router, prefix="/v1")
app.include_router(auth.router, prefix="/v1")

