import abc
from datetime import datetime
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Type
from typing import Union

import sqlalchemy as sa
from databases import Database
from sqlalchemy import Table

from sqlalchemy.sql import Select
from sqlalchemy.sql.elements import BooleanClauseList


class BaseModifier(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def modify(self: 'BaseModifier', model: Type[Table], query: Select) -> Select:
        raise NotImplementedError


class WhereModifier(BaseModifier):
    def __init__(self: 'WhereModifier', **kwargs) -> None:
        self.fields = kwargs

    def modify(self: 'WhereModifier', model: Type[Table], query: Select) -> Select:
        return query.where(
            sa.and_(
                *[getattr(model, key) == value for key, value in self.fields.items()],
            ),
        )


class ExpiredModifier(BaseModifier):
    def __init__(self, utc_now: Optional[datetime] = None) -> None:
        self.utc_now = utc_now or datetime.utcnow()

    def modify(self: 'ExpiredModifier', model: Type[Table], query: Select) -> Select:
        return query.where(sa.and_(model.end_at >= self.utc_now, model.start_at <= self.utc_now))


class SortModifier(BaseModifier):
    def __init__(self: 'SortModifier', field: str, sort_type: str = 'asc') -> None:
        self.field = field
        self.sort_type = sa.asc if sort_type == 'asc' else sa.desc

    def modify(self: 'SortModifier', model: Type[Table], query: Select) -> Select:
        return query.order_by(self.sort_type(getattr(model, self.field)))


class BaseRepository:
    model: Type[Table]
    db_connection: Database

    @classmethod
    async def get(
        cls: Type['BaseRepository'],
        modifiers: List[BaseModifier],
    ) -> Optional[Dict[Any, Any]]:
        query = cls._modify_query(cls.get_base_query(), modifiers)
        result = await cls.db_connection.fetch_one(query)
        return dict(result) if result else None

    @classmethod
    async def create(cls: Type['BaseRepository'], **kwargs) -> None:
        # Issue: https://github.com/dropbox/sqlalchemy-stubs/issues/48
        query = sa.insert(cls.model).values(**kwargs)  # type: ignore[arg-type]
        await cls.db_connection.execute(query)

    @classmethod
    async def update(
        cls: Type['BaseRepository'],
        fields: Dict[str, Any],
        **kwargs,
    ) -> Optional[Dict[str, Any]]:
        query = (
            sa.update(cls.model)  # type: ignore[arg-type]
            .values(**fields)
            .where(cls.get_where_clause(**kwargs))
            .returning(*cls.model.__table__.columns)
        )
        result = await cls.db_connection.fetch_one(query)
        return dict(result) if result else None

    @classmethod
    async def delete(cls: Type['BaseRepository'], **kwargs) -> None:
        query = sa.delete(cls.model).where(cls.get_where_clause(**kwargs))  # type: ignore[arg-type]
        await cls.db_connection.execute(query)

    @classmethod
    async def all(
        cls: Type['BaseRepository'],
        modifiers: List[BaseModifier],
    ) -> List[Dict[Any, Any]]:
        query = cls._modify_query(cls.get_base_query(), modifiers)
        result = await cls.db_connection.fetch_all(query)
        return [dict(row) for row in result] if result else []

    @classmethod
    def get_base_query(
        cls: Type['BaseRepository'],
        select: Optional[Union[list, tuple]] = None,
    ) -> Select:
        if select is None:
            select = (cls.model,)
        return sa.select(select)

    @classmethod
    def get_where_clause(cls: Type['BaseRepository'], **kwargs) -> BooleanClauseList:
        return sa.and_(
            *[getattr(cls.model, key) == value for key, value in kwargs.items()],
        )

    @classmethod
    def _modify_query(
        cls: Type['BaseRepository'],
        query: Select,
        modifiers: List[BaseModifier],
    ) -> Select:
        for modifier in modifiers:
            query = modifier.modify(cls.model, query)
        return query

    @classmethod
    async def count(cls: Type['BaseRepository'], modifiers: List[BaseModifier]) -> int:
        query = cls._modify_query(
            sa.select([sa.func.count()]).select_from(cls.model),  # type: ignore[arg-type]
            modifiers,
        )
        return await cls.db_connection.fetch_val(query)
