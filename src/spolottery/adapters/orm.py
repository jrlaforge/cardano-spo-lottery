from sqlalchemy import MetaData, Table, String, Column, DateTime, ForeignKey, Integer, Float, Boolean
from sqlalchemy.orm import mapper, relationship, column_property, deferred

from spolottery.domain import models

metadata = MetaData()

pools = Table(
    "pools",
    metadata,
    Column("pool_id", String, primary_key=True),
    Column("hex", String),
    Column("url", String),
    Column("ticker", String),
    Column("name", String),
    Column("description", String),
    Column("updated_at", DateTime),
)

# delegators = Table(
#     "delegators",
#     metadata,
#     Column("address_id", String, primary_key=True),
# )

pool_owners = Table(
    "pool_owners",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("address_id", String),
    Column("pool_id", ForeignKey("pools.pool_id")),
)


lottery_tickets = Table(
    "lottery_tickets",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("delegator_id", String),
    Column("winning_likelyhood", Float),
    Column("pool_owner", Boolean),
    Column("lottery_id", ForeignKey("lotteries.uuid")),
    Column("delegator_lottery_stake", Float, default=0),
)

lotteries = Table(
    "lotteries",
    metadata,
    Column("uuid", String, primary_key=True),
    Column("pool_id", ForeignKey("pools.pool_id")),
    Column("name", String),
    Column("start_epoch", Integer),
    Column("end_epoch", Integer),
    Column("count_epochs", Integer),
    Column("draw_date", DateTime),
    Column("created_at", DateTime),
    Column("lottery_strategy_type", String),
    Column("owners_allowed", Boolean),
    Column("min_live_stake", Integer, default=0),
)


lottery_winners = Table(
    "lottery_winners",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("delegator_address_id", String),
    Column("lottery_id", ForeignKey("lotteries.uuid")),
    Column("rank", Integer),
)


def start_mappers():
    # delegators_mapper = mapper(models.Delegator, delegators)
    lottery_tickets_mapper = mapper(
        models.LotteryTicket,
        lottery_tickets,
    )

    lottery_winners_mapper = mapper(models.LotteryWinner, lottery_winners)

    lotteries_mapper = mapper(
        models.Lottery,
        lotteries,
        properties={
            "winners": relationship(
                lottery_winners_mapper,
                collection_class=set,
            ),
            "lottery_tickets": relationship(
                lottery_tickets_mapper,
                collection_class=list,
            ),
        },
    )

    pool_owners_mapper = mapper(models.PoolOwner, pool_owners)
    pool_mapper = mapper(
        models.Pool,
        pools,
        properties={
            "_owners": relationship(
                pool_owners_mapper,
                collection_class=set,
            )
        },
    )
