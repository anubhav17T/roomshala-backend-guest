import os
from datetime import datetime
from fastapi import FastAPI, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from starlette import status
from src.constants.fields import V1_PREFIX, GUEST_TAGS, HEALTH_TAGS
from src.controller.v1.booking import booking_engine
from src.controller.v1.guest import guest
# from src.utils.connections.consul.connection import connection_service
from src.utils.connections.db_object import db
from src.utils.connections.check_database_connection import DatabaseConfiguration
from src.utils.custom_exceptions.custom_exceptions import CustomExceptionHandler
from src.utils.tables.guest_db_tables import creating_guest_table, creating_codes_table, creating_blacklist_table, \
    guest_fav_property, booking


origins = ["*"]

conn = DatabaseConfiguration()


def connection():
    conn.checking_database_connection()
    creating_guest_table()
    creating_codes_table()
    creating_blacklist_table()
    guest_fav_property()
    booking()


def service_handler():
    consul_host = os.environ.get("CONSUL_HOST")
    consul_port = os.environ.get("CONSUL_PORT")
    # connection_service(host=consul_host,port=consul_port)



app = FastAPI(title="Roomshala Guest Backend API'S",
              version="1.0.0"
              )

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(guest, prefix=V1_PREFIX,tags=[GUEST_TAGS])
app.include_router(booking_engine, prefix=V1_PREFIX,tags=[GUEST_TAGS])


@app.get("/health",tags=[HEALTH_TAGS])
async def check():
    return {"status": "Ok"}


@app.on_event("startup")
async def startup():
    await db.connect()


@app.on_event("shutdown")
async def shutdown():
    await db.disconnect()


@app.exception_handler(CustomExceptionHandler)
async def NotFoundException(request: Request, exception: CustomExceptionHandler):
    """:return custom exceptions """
    return JSONResponse(status_code=exception.code,
                        content={"error": {"message": exception.message,
                                           "code": exception.code,
                                           "target": exception.target,
                                           "success": exception.success
                                           }
                                 }
                        )


@app.exception_handler(Exception)
async def NotHandleException(request: Request, exception: Exception):
    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        content={"error": {"message": "Something Went Wrong Broken Pipeline",
                                           "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                                           "target": request.url.components.path.upper(),
                                           "error": exception.__str__(),
                                           "success": False
                                           }
                                 }
                        )


@app.middleware("http")
async def middleware(request: Request, call_next):
    start_time = datetime.utcnow()
    response = await call_next(request)
    # modify response adding custom headers
    execution_time = (datetime.utcnow() - start_time).microseconds
    response.headers["x-execution-time"] = str(execution_time)
    return response


if __name__ == "__main__":
    connection()
    # service_handler()
    import uvicorn
    uvicorn.run(app, port=8002)
