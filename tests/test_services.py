from typing import List

import pytest
from spolottery.domain import models
from spolottery.service_layer import services, unit_of_work
from tests.conftest import make_delegators, make_pool, make_pool_block, make_fake_duplicate_hippo_pool, make_lottery
from spolottery.adapters.repository import AbstractPoolRepository, AbstractLotteryRepository
from spolottery.service_layer.cardano_service import AbstractCardanoService


class FakeSession:
    committed = False

    def commit(self):
        self.committed = True


class FakePoolRepository(AbstractPoolRepository):
    def __init__(self, pools):
        self._pools = set(pools)

    def add(self, pool: models.Pool):
        self._pools.add(pool)

    def add_multiple(self, pools: List[models.Pool]):
        self._pools.update(pools)

    def get(self, pool_id: str) -> models.Pool:
        return next(p for p in self._pools if p.pool_id == pool_id)

    def list(self):
        return self._pools


class FakeLotteryRepository(AbstractLotteryRepository):
    def __init__(self, lotteries):
        self._lotteries = set(lotteries)

    def add(self, lottery: models.Lottery):
        self._lotteries.add(lottery)

    def get(self, lottery_id: str) -> models.Lottery:
        return next(lot for lot in self._lotteries if lot.uuid == lottery_id)

    def list(self):
        return self._lotteries


class FakeUnitOfWork(unit_of_work.AbstractUnitOfWork):
    def __init__(self, pools, lottery):
        self.pools = FakePoolRepository(pools)
        self.lottery = FakeLotteryRepository(lottery)
        self.committed = False

    def commit(self):
        self.committed = True

    def rollback(self):
        pass


class FakeCardanoService(AbstractCardanoService):
    def __init__(self, pools):
        self._pools = set(pools)

    async def get_all_pools(self, pool_stored: List[models.Pool]) -> List[models.Pool]:
        return self._pools

    async def get_pool_delegators(self, pool_id: str) -> List[models.Delegator]:
        return make_delegators()

    async def get_delegators_history(self, stake_address: str):
        return make_delegators()


def test_return_pools():
    hippo_pool = make_pool()

    block_pool = make_pool_block()

    hippo_fake_pool = make_fake_duplicate_hippo_pool()

    all_pools = [hippo_pool, block_pool, hippo_fake_pool]

    uow = FakeUnitOfWork(all_pools, [])

    cardano_service = FakeCardanoService(all_pools)
    # TO be changed
    services.add_pools(uow, cardano_service)

    search_block_pools = services.search_pool("block", uow)
    search_hippo_pools = services.search_pool("hippo", uow)

    assert set([block_pool]) == search_block_pools
    assert set([hippo_pool, hippo_fake_pool]) == search_hippo_pools


@pytest.mark.asyncio
async def test_return_create_lottery():
    hippo_pool = make_pool()

    block_pool = make_pool_block()

    hippo_fake_pool = make_fake_duplicate_hippo_pool()

    all_pools = [hippo_pool, block_pool, hippo_fake_pool]

    cardano_service = FakeCardanoService([])

    uow = FakeUnitOfWork(all_pools, [])

    lottery = make_lottery()

    draw_date_str = lottery.draw_date.strftime(format="%Y-%m-%d %H:%M:%S")

    lottery_completed = await services.create_lottery(lottery.pool_id, lottery.start_epoch,
                                                      lottery.end_epoch, lottery.count_epochs,
                                                      draw_date_str, models.LotteryStrategyType.FIXED.value,
                                                      lottery.owners_allowed, lottery.lottery_strategy.min_live_stake,
                                                      lottery.name, uow, cardano_service)

    expected_lottery = uow.lottery.get(lottery_completed.uuid)

    assert lottery_completed.uuid == expected_lottery.uuid


@pytest.mark.asyncio
async def test_return_create_lottery_min_live_stake():
    hippo_pool = make_pool()

    block_pool = make_pool_block()

    hippo_fake_pool = make_fake_duplicate_hippo_pool()

    all_pools = [hippo_pool, block_pool, hippo_fake_pool]

    uow = FakeUnitOfWork(all_pools, [])

    cardano_service = FakeCardanoService([])

    lottery = make_lottery(min_live_stake=1005)

    draw_date_str = lottery.draw_date.strftime(format="%Y-%m-%d %H:%M:%S")
    try:
        lottery_completed = await services.create_lottery(lottery.pool_id, lottery.start_epoch,
                                                          lottery.end_epoch, lottery.count_epochs,
                                                          draw_date_str, models.LotteryStrategyType.FIXED.value,
                                                          lottery.owners_allowed, lottery.lottery_strategy.min_live_stake,
                                                          lottery.name, uow, cardano_service)
        assert False
    except models.OutOfDelegator:
        assert True


@pytest.mark.asyncio
async def test_return_create_lottery_stake_strategy():
    hippo_pool = make_pool()

    block_pool = make_pool_block()

    hippo_fake_pool = make_fake_duplicate_hippo_pool()

    all_pools = [hippo_pool, block_pool, hippo_fake_pool]

    uow = FakeUnitOfWork(all_pools, [])

    cardano_service = FakeCardanoService([])

    lottery = make_lottery(
        strategy_type=models.LotteryStrategyType.STAKE.value, different_live_stakes=True)

    draw_date_str = lottery.draw_date.strftime(format="%Y-%m-%d %H:%M:%S")

    lottery_completed = await services.create_lottery(lottery.pool_id, lottery.start_epoch,
                                                      lottery.end_epoch, lottery.count_epochs,
                                                      draw_date_str, lottery.lottery_strategy_type, lottery.owners_allowed,
                                                      lottery.lottery_strategy.min_live_stake,
                                                      lottery.name, uow, cardano_service)

    expected_lottery = uow.lottery.get(lottery_completed.uuid)

    assert lottery_completed.uuid == expected_lottery.uuid
