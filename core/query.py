from aiogram import types
import redis

import config


class _Redis(redis.StrictRedis):
    def __init__(self):
        super().__init__(
            host=config.REDIS_HOST,
            port=config.REDIS_PORT, 
            password=config.REDIS_PASSWORD,
            charset="utf-8",
            decode_responses=True
        )


class Query:
    def __init__(self, _redis: redis.StrictRedis, name: str) -> None:
        self._redis = _redis
        self.name = name
        
        self._redis.set('query_length', 1)

    def add_member(self, query_position: int | None, telegram_username: str) -> None:
        if query_position == -1:
            query_position = self._redis.get('query_length')
        self._redis.zadd(self.name,
            {
                telegram_username: query_position
            }
        )

        self._redis.incr('query_length')

    def clear_query(self):
        self._redis.delete(self.name)
        self._redis.delete('query_length')

    def get_all_members(self) -> list:
        return self._redis.zrange(self.name, 0, -1, withscores=True)


class QueryUtils:
    @staticmethod
    def get_stylish_members(members: list[tuple]) -> str:
        result = '\n'.join([f"{int(count)}. @{member}" for member, count in members])
        return result


class QueryFactory:
    def __init__(self):
        self.queues = {}

    def add_query(self, query_name: str) -> None:
        if query_name in self.queues:
            self.queues[query_name].clear_query()
        self.queues[query_name] = Query(_Redis(), query_name)

    def get_query(self, query_name: str) -> Query:
        try:
            return self.queues[query_name]
        except KeyError as exc:
            raise QueryNameException from exc

    def delete_query(self, query_name: str) -> None:
        try:
            self.queues[query_name].clear_query()
            del self.queues[query_name]
        except KeyError as exc:
            raise QueryNameException from exc


class QueryNameException(Exception):
    pass
        
    






