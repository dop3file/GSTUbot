from aiogram import types
import redis

import config


class Redis(redis.StrictRedis):
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
        elif query_position < 0:
            return
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
        self.redis = Redis()
        self.name = 'queues'

    def check_in_query(self, query_name: str) -> bool:
        print(self.get_all_queues())
        if query_name in self.get_all_queues():
            return True
        return False

    def add_query(self, query_name: str) -> None:
        if self.check_in_query(query_name):
            self.delete_query(query_name)
        self.redis.lpush(self.name, query_name)

    def get_all_queues(self) -> list:
        return self.redis.lrange(self.name, 0, -1)

    def get_query(self, query_name: str) -> Query:
        if not self.check_in_query(query_name):
            raise QueryNameException
        return Query(_redis=Redis(), name=query_name)

    def delete_query(self, query_name: str) -> None:
        query = Query(_redis=Redis(), name=query_name)
        query.clear_query()
        self.redis.rpush(self.name, query_name)


class QueryNameException(Exception):
    pass
        
    






