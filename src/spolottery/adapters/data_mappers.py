import datetime
from typing import List
from spolottery.adapters import dto, orm
from spolottery.domain import models


def pool_model_to_entity(instance: orm.pools) -> models.Pool:
    return models.Pool(
        pool_id=instance.pool_id,
        hex=instance.hex,
        url=instance.url,
        ticker=instance.ticker,
        name=instance.name,
        description=instance.description,
        updated_at=instance.updated_at
    )


def lottery_tickets_entity_to_dto(tickets: List[models.LotteryTicket]) -> List[dto.LotteryTicketDto]:
    return [dto.LotteryTicketDto(
        delegator_id=ticket.delegator_id,
        winning_likelyhood=ticket.winning_likelyhood,
        pool_owner=ticket.pool_owner,
        delegator_lottery_stake=ticket.delegator_lottery_stake if ticket.delegator_lottery_stake else None,
    ) for ticket in tickets]


def lottery_winners_entity_to_dto(winners: List[models.LotteryWinner]) -> List[dto.LotteryWinnerDto]:
    return [dto.LotteryWinnerDto(
        delegator_address_id=winner.delegator_address_id,
        rank=winner.rank
    ) for winner in winners]


def lottery_entity_to_dto(lottery: models.Lottery, detailed: bool) -> dto.LotteryDto:
    min_live_stake = lottery.min_live_stake if lottery.min_live_stake else 0
    tickets_dto = []
    winners_dto = []
    if detailed:
        tickets_dto = lottery_tickets_entity_to_dto(lottery.lottery_tickets)
        if lottery.is_lottery_result_available():
            winners_dto = lottery_winners_entity_to_dto(lottery.winners)
    return dto.LotteryDto(
        uuid=lottery.uuid,
        pool_id=lottery.pool_id,
        name=lottery.name,
        start_epoch=lottery.start_epoch,
        end_epoch=lottery.end_epoch,
        count_epochs=lottery.count_epochs,
        draw_date=lottery.draw_date,
        created_at=lottery.created_at,
        lottery_strategy_type=lottery.lottery_strategy_type,
        owners_allowed=lottery.owners_allowed,
        min_live_stake=min_live_stake,
        winners=winners_dto,
        tickets=tickets_dto
    )
