import abc
import models


class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, pool: models.Pool):
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, pool_id: str) -> models.Pool:
        raise NotImplementedError
