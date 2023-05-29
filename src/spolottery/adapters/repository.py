import abc
from typing import List
from spolottery.adapters.data_mappers import pool_model_to_entity
from spolottery.domain import models


class PoolDoesntExist(Exception):
    pass


class AbstractPoolRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, pool: models.Pool):
        raise NotImplementedError

    @abc.abstractmethod
    def add_multiple(self, pools: List[models.Pool]):
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, pool_id: str) -> models.Pool:
        raise NotImplementedError

    @abc.abstractmethod
    def list(self) -> List[models.Pool]:
        raise NotImplementedError


class SqlAlchemyPoolRepository(AbstractPoolRepository):
    def __init__(self, session):
        self.session = session

    def add(self, pool: models.Pool):
        self.session.add(pool)

    def add_multiple(self, pools: List[models.Pool]):
        self.session.add_all(pools)

    def get(self, pool_id):
        try:
            return self.session.query(
                models.Pool).filter_by(pool_id=pool_id).one()
        except Exception as e:
            raise PoolDoesntExist(
                "Pool {} doesn't exist".format(pool_id))
        return

    def list(self):
        instance_pools = self.session.query(models.Pool).all()
        return [pool_model_to_entity(pool) for pool in instance_pools]


class AbstractDelegatorRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, delegator: models.Delegator):
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, delegator_id: str) -> models.Delegator:
        raise NotImplementedError


class SqlAlchemyDelegatorRepository(AbstractDelegatorRepository):
    def __init__(self, session):
        self.session = session

    def add(self, delegator):
        self.session.add(delegator)

    def get(self, delegator_id):
        return self.session.query(models.Delegator).filter_by(address_id=delegator_id).one()

    def list(self):
        return self.session.query(models.Delegator).all()


# Pool Owner
class AbstractPoolOwnerRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, pool_owner: models.PoolOwner):
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, pool_owner_id: str) -> models.PoolOwner:
        raise NotImplementedError


class SqlAlchemyPoolOwnerRepository(AbstractPoolOwnerRepository):
    def __init__(self, session):
        self.session = session

    def add(self, pool_owner):
        self.session.add(pool_owner)

    def get(self, pool_owner_id):
        return self.session.query(models.PoolOwner).filter_by(id=pool_owner_id).one()

    def list(self):
        return self.session.query(models.PoolOwner).all()


# lottery_tickets
class AbstractLotteryTicketRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, pool_owner: models.LotteryTicket):
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, lottery_tickets_id: str) -> models.LotteryTicket:
        raise NotImplementedError


class SqlAlchemyLotteryTicketRepository(AbstractLotteryTicketRepository):
    def __init__(self, session):
        self.session = session

    def add(self, lottery_tickets):
        self.session.add(lottery_tickets)

    def get(self, lottery_tickets_id):
        return self.session.query(models.LotteryTicket).filter_by(id=lottery_tickets_id).one()

    def list(self):
        return self.session.query(models.LotteryTicket).all()


# Lottery
class AbstractLotteryRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, pool_owner: models.Lottery):
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, lottery_id: str) -> models.Lottery:
        raise NotImplementedError


class SqlAlchemyLotteryRepository(AbstractLotteryRepository):
    def __init__(self, session):
        self.session = session

    def add(self, lottery):
        self.session.add(lottery)

    def get(self, lottery_id):
        return self.session.query(models.Lottery).filter_by(uuid=lottery_id).one()

    def list(self):
        return self.session.query(models.Lottery).all()


# Lottery Winners
class AbstractLotteryWinnerRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, pool_owner: models.LotteryWinner):
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, lottery_winner_id: str) -> models.LotteryWinner:
        raise NotImplementedError


class SqlAlchemyLotteryWinnerRepository(AbstractLotteryWinnerRepository):
    def __init__(self, session):
        self.session = session

    def add(self, lottery_winner):
        self.session.add(lottery_winner)

    def get(self, lottery_winner_id):
        return self.session.query(models.LotteryWinner).filter_by(id=lottery_winner_id).one()

    def list(self):
        return self.session.query(models.LotteryWinner).all()
