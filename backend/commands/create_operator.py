import argparse
import asyncio

from loguru import logger
from sqlalchemy.exc import IntegrityError, DBAPIError

from core.database import get_contextual_session
from services.operators import create_operator
from views.operators import CreateOperatorView


async def run(email, password, first_name, last_name, address):
    view = CreateOperatorView(
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
        address=address
    )
    async with get_contextual_session() as session:
        user = await create_operator(session, view)
        try:
            await session.commit()
        except IntegrityError:
            logger.warning("The user with given email already exists.")
            return
        except DBAPIError:
            import traceback
            logger.error("Too long values.")
            return

    logger.success(f"Successfully created user with email={user.email} and password={password}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--email", type=str, required=True)
    parser.add_argument("-p", "--password", type=str, required=True)
    parser.add_argument("-f", "--fname", type=str, required=True)
    parser.add_argument("-l", "--lname", type=str, required=True)
    parser.add_argument("-a", "--address", type=str, required=True)
    args = parser.parse_args()

    asyncio.run(run(
        email=args.email,
        password=args.password,
        first_name=args.fname,
        last_name=args.lname,
        address=args.address
    ))
