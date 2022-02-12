import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime

import numpy as np


class OutOfDelegator(Exception):
    pass


class OutOfEpoch(Exception):
    pass


@dataclass(unsafe_hash=True)
class Delegation:
    address_id: str  # Stake address id
    pool_id: str  # Pool id
    amount: float
    epoch_no: int

    def __gt__(self, other):
        if self.epoch_no is None:
            return False
        if other.epoch_no is None:
            return True
        return self.epoch_no > other.epoch_no


class Delegator:
    def __init__(self, address_id: str, delegation_history: set[Delegation] = None):  # Stake address id
        self.address_id = address_id
        self.delegation_history = set()  # type Set[Delegation] List of Deletation(s)
        if delegation_history:
            self.delegation_history = delegation_history

    def add_delegation_history(self, delegation: Delegation):
        self.delegation_history.add(delegation)

    def __repr__(self):
        return f"<Delegator {self.address_id}>"

    def __eq__(self, other):
        if not isinstance(other, Delegator):
            return False
        return other.address_id == self.address_id

    def __hash__(self):
        return hash(self.address_id)


class PoolOwner(Delegator):
    pool_id: str  # Pool id


class Pool:
    def __init__(
        self,
        pool_id: str,  # Bech32 encoded pool ID
        hex: str,
        url: str,
        ticker: str,
        name: str,
        description: str,
        updated_at: datetime,
    ):
        self.pool_id = pool_id
        self.hex = hex
        self.url = url
        self.ticker = ticker
        self.name = name
        self.description = description
        self.updated_at = updated_at
        self._owners = set()  # type Set[PoolOwner] List of stake address

    @property
    def owners(self):
        return self._owners

    def add_pool_owner(self, owner: PoolOwner):
        self._owners.add(owner)

    def __repr__(self):
        return f"<Pool {self.pool_id}>"

    def __eq__(self, other):
        if not isinstance(other, Pool):
            return False
        return other.pool_id == self.pool_id

    def __hash__(self):
        return hash(self.pool_id)


def is_eligible(delegator: Delegator, target_pool_id: str, current_epoch: int, min_count_active_epochs: int) -> bool:
    """
    Given a delegator history, a pool id, a number of past epochs
    Check if the delegator address was loyal to the pool during "number_epochs"
    and provide what was its first delegation amount
    """

    min_epoch = current_epoch - min_count_active_epochs

    delegator_eligible_status = True

    for delegation in sorted(delegator.delegation_history):
        if min_epoch <= delegation.epoch_no <= current_epoch and delegation.pool_id != target_pool_id:
            delegator_eligible_status = False
            break

    return delegator_eligible_status


def first_delegation_amount(delegator: Delegator, target_pool_id: str) -> int:
    """
    Get first delegation amount on target_pool_id
    """
    return next(dh.amount for dh in sorted(delegator.delegation_history) if dh.pool_id == target_pool_id)


def curent_live_stake(delegator: Delegator, target_pool_id: str) -> int:
    """
    Get current active stake on target_pool_id
    """
    return next(dh.amount for dh in sorted(delegator.delegation_history, reverse=True) if dh.pool_id == target_pool_id)


class LotteryTicket:
    def __init__(
        self,
        delegator: Delegator,
        winning_likelyhood: float,
        pool_owner: bool,
        lottery_id: Optional[str],
    ):
        self.delegator = delegator
        self.winning_likelyhood = winning_likelyhood
        self.pool_owner = pool_owner
        if lottery_id:
            self.lottery_id = lottery_id


def get_lottery_ticket_likelyhood(lottery_ticket: LotteryTicket, target_pool_id: str) -> int:
    """
    Calculate likelyhood of a lottery ticket based on delegator history
    """
    return 0


def generate_uuid():
    return str(uuid.uuid4())


@dataclass(unsafe_hash=True)
class LotteryStrategyType:
    id: int
    name: str


class LotteryStrategy(ABC):

    lottery_tickets: List[LotteryTicket]

    def init_strategy(
        self, delegators: List[Delegator], owners_allowed: bool, lottery_id: str, pool: Pool, count_epochs: int
    ):
        self.delegators = delegators
        self.owners_allowed = owners_allowed
        self.lottery_id = lottery_id
        self.pool = pool
        self.count_epochs = count_epochs
        self.lottery_tickets = []

    @abstractmethod
    def prepare_lottery(self):
        raise NotImplementedError

    @abstractmethod
    def calculate_likelyhood(self) -> List[LotteryTicket]:
        raise NotImplementedError


class FixedLotteryStrategy(LotteryStrategy):
    def prepare_lottery(self):
        count_delegators = len(self.delegators)
        # If no delegator, no lottery
        if count_delegators == 0:
            raise OutOfDelegator(f"Out of Delegator for lottery {self.lottery_id}")
        # If no delegator, no lottery
        if self.count_epochs < 1:
            raise OutOfEpoch(f"Count epochs should be >= 1 for lottery  {self.lottery_id}")

    def calculate_likelyhood(self):

        count_delegators = len(self.delegators)

        winning_likelyhood = 1 / count_delegators
        for delegator in self.delegators:
            is_pool_owner = is_delegator_pool_owner(delegator, self.pool)
            if not (is_pool_owner and not self.owners_allowed):
                self.lottery_tickets.append(
                    LotteryTicket(
                        delegator=delegator,
                        winning_likelyhood=winning_likelyhood,
                        pool_owner=is_pool_owner,
                        lottery_id=self.lottery_id,
                    )
                )

        return self.lottery_tickets


class StakeLotteryStrategy(LotteryStrategy):
    delegators_stake = []
    total_mean_stake = 0

    def prepare_lottery(self):
        self.delegators_stake = []
        self.total_mean_stake = 0

        count_delegators = len(self.delegators)
        # If no delegator, no lottery
        if count_delegators == 0:
            raise OutOfDelegator(f"Out of Delegator for lottery {self.lottery_id}")

        # If no delegator, no lottery
        if self.count_epochs < 1:
            raise OutOfEpoch(f"Count epochs should be >= 1 for lottery  {self.lottery_id}")

        for delegator in self.delegators:
            current_live_stake = curent_live_stake(delegator, self.pool.pool_id)
            if self.count_epochs == 1:
                mean_delegation_by_epoch = current_live_stake
            else:
                first_stake_amount = first_delegation_amount(delegator, self.pool.pool_id)
                mean_delegation_by_epoch = round(
                    abs(int(first_stake_amount) + int(current_live_stake)) / (self.count_epochs), 2
                )

                self.delegators_stake.append((delegator, mean_delegation_by_epoch))

            self.total_mean_stake += mean_delegation_by_epoch

    def calculate_likelyhood(self):

        for delegator_stake in self.delegators_stake:
            delegator, mean_delegation_by_epoch = delegator_stake
            winning_likelyhood = mean_delegation_by_epoch / self.total_mean_stake
            is_pool_owner = is_delegator_pool_owner(delegator, self.pool)
            if not (is_pool_owner and not self.owners_allowed):
                lottery_tickets = LotteryTicket(
                    delegator=delegator,
                    winning_likelyhood=winning_likelyhood,
                    pool_owner=is_pool_owner,
                    lottery_id=self.lottery_id,
                )
                self.lottery_tickets.append(lottery_tickets)

        return self.lottery_tickets


class LotteryStrategyFactory:
    def createLotteryStrategy(self, lottery_strategy_name: str):
        lottery_strategy: LotteryStrategy = None
        if lottery_strategy_name == "Fixed":
            lottery_strategy = FixedLotteryStrategy()
        if lottery_strategy_name == "Stake":
            lottery_strategy = StakeLotteryStrategy()

        return lottery_strategy


@dataclass(unsafe_hash=True)
class LotteryWinner:
    lottery_ticket_id: str
    lottery_id: str
    rank: int


class Lottery:
    def __init__(
        self,
        uuid: str,
        pool_id: str,
        name: str,
        start_epoch: int,
        end_epoch: int,
        count_epochs: int,
        draw_date: datetime,
        created_at: datetime,
        lottery_strategy_type: LotteryStrategyType,
        lottery_strategy: LotteryStrategy,
        owners_allowed: bool,
        lottery_tickets: List[LotteryTicket] = None,
        winners: Optional[List[LotteryWinner]] = None,
    ):
        self.uuid = uuid
        if winners:
            self.winners = winners  # Ordered list of winners
        self.pool_id = pool_id
        self.name = name
        self.start_epoch = start_epoch
        self.end_epoch = end_epoch
        self.count_epochs = count_epochs
        self.lottery_strategy = lottery_strategy
        self.lottery_strategy_type = lottery_strategy_type
        self.owners_allowed = owners_allowed
        self.draw_date = draw_date
        self.created_at = created_at
        self.lottery_tickets = lottery_tickets

    def __repr__(self):
        return f"<Lottery {self.uuid}>"

    def __eq__(self, other):
        if not isinstance(other, Lottery):
            return False
        return other.uuid == self.uuid

    def __hash__(self):
        return hash(self.uuid)

    def raffle_draw(self):
        # Default seed with lottery uuid to keep the same results if same parameters
        rng = np.random.default_rng(int("".join(filter(str.isdigit, self.uuid))))
        delegator_keys = [lt.delegator.address_id for lt in self.lottery_tickets]
        delegator_winning_likelyhoods = [lt.winning_likelyhood for lt in self.lottery_tickets]

        self.winners = rng.choice(
            delegator_keys, len(delegator_keys), replace=False, p=delegator_winning_likelyhoods
        ).tolist()



def is_delegator_pool_owner(delegator: Delegator, pool: Pool):
    """
    Is "delegator" an owner of the "pool"
    """
    for pool_owner in pool.owners:
        if delegator.address_id in pool_owner.address_id:
            return True
    return False


def prepare_lottery_tickets_list(delegators: [Delegator], lottery: Lottery, pool: Pool) -> [LotteryTicket]:
    """
    Prepare a list of LotteryTicket based on a list of Delegators
    Get total mean stake
    Get mean stake accros epochs by delegator
    :rtype: object
    """

    eligible_delegators = [
        delegator
        for delegator in delegators
        if is_eligible(delegator, pool.pool_id, lottery.start_epoch, lottery.count_epochs)
    ]
    lottery.lottery_strategy.init_strategy(
        eligible_delegators, lottery.owners_allowed, lottery.uuid, pool, lottery.count_epochs
    )
    lottery.lottery_strategy.prepare_lottery()
    lottery_tickets = lottery.lottery_strategy.calculate_likelyhood()

    return lottery_tickets


def create_lottery(lottery_tickets: [LotteryTicket], target_pool_id: str) -> Lottery:
    """
    Create lottery based on a list of LotteryTickets
    """
    pass
