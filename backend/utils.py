from typing import Tuple, List
from uuid import uuid4

import arrow
import math
from fastapi import Query
from sqlalchemy import func, select

from views import PaginationView


def params_extractor(
        page: int = Query(1, ge=1),
        size: int = Query(10, gt=0)
) -> Tuple:
    return page, size


async def paginate(
        session,
        query_builder,
        page: int,
        size: int
) -> Tuple[List, PaginationView]:
    query = await query_builder()
    count = await session.execute(select(func.count()) \
                                  .select_from(query.alias('subquery')))
    query = query.limit(size).offset(size * (page - 1))

    result = await session.execute(query)
    items = result.unique().fetchall()

    total = count.scalar()
    pagination = PaginationView(
        current_page=page,
        last_page=math.ceil(total / size) or 1,
        total=total
    )

    return items, pagination


def now():
    return arrow.utcnow()


def generate_message_id() -> str:
    return str(uuid4())
