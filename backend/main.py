import asyncio

from loguru import logger

from app import app
from controllers.actions import actions_router
from controllers.charge_points import charge_points_router, anonymous_charge_points_router
from controllers.drivers import drivers_router
from controllers.operators import operators_public_router, operators_private_router
from controllers.transactions import transactions_router
from events import process_event
from pyocpp_contrib.decorators import init_logger
from pyocpp_contrib.queue.consumer import start_consume
from pyocpp_contrib.settings import EVENTS_EXCHANGE_NAME

background_tasks = set()


@app.on_event("startup")
async def startup():
    init_logger(logger)
    # Save a reference to the result of this function, to avoid a task disappearing mid-execution.
    # The event loop only keeps weak references to tasks.
    task = asyncio.create_task(
        start_consume(exchange_name=EVENTS_EXCHANGE_NAME, on_message=process_event)
    )
    background_tasks.add(task)


app.include_router(actions_router)
app.include_router(transactions_router)
app.include_router(anonymous_charge_points_router)
app.include_router(drivers_router)
app.include_router(operators_public_router)
app.include_router(operators_private_router)
app.include_router(charge_points_router)
