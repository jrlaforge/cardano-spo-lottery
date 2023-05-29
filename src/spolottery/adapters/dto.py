from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

from spolottery.domain.models import LotteryStrategy, LotteryTicket, LotteryWinner


class LotteryInputDto(BaseModel):
    pool_id: str
    start_epoch: int
    end_epoch: int
    count_epochs: int
    min_live_stake: int
    draw_date: str
    lottery_strategy_name: str
    owners_allowed: bool
    lottery_name: str


class LotteryTicketDto(BaseModel):
    delegator_id: str
    winning_likelyhood: float
    pool_owner: bool
    lottery_id: Optional[str]
    delegator_lottery_stake: Optional[float]

    class Config:
        allow_mutation = False


class LotteryWinnerDto(BaseModel):
    delegator_address_id: str
    rank: int

    class Config:
        allow_mutation = False


class LotteryDto(BaseModel):
    uuid: str
    pool_id: str
    name: str
    start_epoch: int
    end_epoch: int
    count_epochs: int
    draw_date: datetime
    created_at: datetime
    lottery_strategy_type: str
    owners_allowed: bool
    min_live_stake: int
    tickets: Optional[List[LotteryTicketDto]]
    winners: Optional[List[LotteryWinnerDto]]

    class Config:
        allow_mutation = False
