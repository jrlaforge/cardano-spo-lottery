import asyncio
from collections import namedtuple
from datetime import datetime, timezone
import logging
from typing import Set, List
from spolottery.adapters import data_mappers
from spolottery.adapters.data_mappers import pool_model_to_entity
from spolottery.adapters import dto

from spolottery.domain import models
from spolottery.adapters.repository import AbstractPoolRepository, AbstractLotteryRepository, PoolDoesntExist

from spolottery.service_layer import unit_of_work
from spolottery.service_layer.cardano_service import AbstractCardanoService


logger = logging.getLogger(__name__)


class InvalidDrawDate(Exception):
    pass


class InvalidLottery(Exception):
    pass


async def add_pools(uow: unit_of_work.AbstractUnitOfWork, cardano_service: AbstractCardanoService):

    with uow:
        pools_stored = uow.pools.list()
        fresh_pools = await cardano_service.get_all_pools(pools_stored)
        uow.pools.add_multiple(fresh_pools)
        uow.commit()
        logger.info("{} new pools stored".format(len(fresh_pools)))
    pass


def search_pool(pool_filter: str, uow: unit_of_work.AbstractUnitOfWork) -> Set[models.Pool]:
    list_matched_pools = set()
    with uow:
        pools = uow.pools.list()

        for pool in pools:
            if pool.is_pool_a_match(pool_filter):
                list_matched_pools.add(pool)

    return list_matched_pools


async def create_lottery(pool_id: str, start_epoch: int, end_epoch: int, count_epochs: int,
                         draw_date: str, lottery_strategy_name: str, owners_allowed: bool,
                         min_live_stake: int, lottery_name: str, uow: unit_of_work.AbstractUnitOfWork, cardano_service: AbstractCardanoService) -> dto.LotteryDto:

    # Create lottery
    utc_now = datetime.utcnow()
    logger.info("Start new lottery : {} - {} - {}".format(lottery_name,
                                                          pool_id, lottery_strategy_name))

   # draw_date_dt = datetime.strptime(draw_date, "%Y-%m-%d %H:%M:%S")

    try:
        draw_date_isoformat = datetime.fromisoformat(draw_date)
        # draw_date_locale_utc =  draw_date_locale.astimezone(datetime.timezone(timedelta(minutes=timezone_used)))
        draw_date_dt = draw_date_isoformat.astimezone(tz=timezone.utc)
    except Exception as e:
        logger.exception(e)
        raise InvalidDrawDate(
            "The draw date format is not correct {}".format(draw_date))

    lottery_strategy_factory = models.LotteryStrategyFactory()
    lottery_strategy = lottery_strategy_factory.createLotteryStrategy(
        lottery_strategy_name, min_live_stake)

    lottery = models.Lottery(
        uuid=models.generate_uuid(),
        pool_id=pool_id,
        name=lottery_name,
        lottery_tickets=[],
        start_epoch=start_epoch,
        end_epoch=end_epoch,
        count_epochs=count_epochs,
        draw_date=draw_date_dt,
        created_at=utc_now,
        lottery_strategy_type=lottery_strategy_name,
        lottery_strategy=lottery_strategy,
        owners_allowed=owners_allowed,
        min_live_stake=min_live_stake
    )

    # Get delegators with history
    delegators = await cardano_service.get_pool_delegators(pool_id)
    logger.info("{} delegators for lottery : {}".format(
        len(delegators), lottery.uuid))

    logger.info("Get delegators history for lottery : {}".format(lottery.uuid))
    # Get delegators history
    if lottery_strategy_name == models.LotteryStrategyType.STAKE.value:
        delegators = await cardano_service.get_delegators_history(delegators)

    # Get pool
    with uow:

        try:
            pool = uow.pools.get(pool_id)

            logger.info("Get pool {} - {} - for lottery : {}".format(pool_id,
                                                                     pool.name, lottery.uuid))

            logger.info(
                "Prepare lottery tickets - for lottery : {}".format(lottery.uuid))

            # Prepare lottery tickets
            lottery.lottery_tickets = models.prepare_lottery_tickets_list(
                delegators, lottery, pool)

            logger.info("Winners draw - for lottery : {}".format(lottery.uuid))

            # Run lottery
            lottery.raffle_draw()

            logger.info(
                "{} Winners - for lottery : {}".format(len(lottery.winners), lottery.uuid))

            # Save lottery
            uow.lottery.add(lottery)

            lottery_dto = data_mappers.lottery_entity_to_dto(
                lottery, detailed=True)

        except PoolDoesntExist as e:
            raise e

        except Exception as e:
            logger.exception(e)
            raise InvalidLottery(
                "The lottery couldn't be created")

    return lottery_dto


async def get_lottery(lottery_id: str, lottery_repo: AbstractLotteryRepository, detailed: bool) -> dto.LotteryDto:
    lottery = lottery_repo.get(lottery_id=lottery_id)
    lottery_dto = data_mappers.lottery_entity_to_dto(
        lottery, detailed=detailed)
    return lottery_dto
