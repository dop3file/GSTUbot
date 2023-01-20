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
    def __init__(self, redis: redis.StrictRedis, query_name: str) -> None:
        self.r = redis
        self.name = query_name

    def get_count_members(self) -> int:
        return self.r.zcard(self.name)

    def add_member(self, query_position: int, telegram_username: str) -> None:
            self.r.zadd(self.name,
                    {
                        telegram_username: query_position
                    }
            )

    def clear_query(self):
        self.r.delete(self.name)

    def get_all_members(self) -> list:
        return self.r.zrange(self.name, 0, -1, withscores=True)


class QueryFactory:
    def __init__(self):
        self.querys = {}

    def add_query(self, query_name: str) -> None:
        self.querys[query_name] = Query(_Redis(), query_name)

    def get_query(self, query_name: str) -> Query:
        return self.querys[query_name]

    def delete_query(self, query_name: str) -> None:
        self.querys[query_name].clear_query()
        del self.querys[query_name]
        
    






