from sqlalchemy import MetaData, Table, String, Column, DateTime, ForeignKey, Integer, Float, Boolean
from sqlalchemy.orm import mapper, relationship

import models

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

delegators = Table(
    "delegators",
    metadata,
    Column("address_id", String, primary_key=True),
)

pool_owners = Table(
    "pool_owners",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("address_id", ForeignKey("delegators.address_id")),
    Column("pool_id", ForeignKey("pools.pool_id")),
)


lottery_tickets = Table(
    "lottery_tickets",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("delegator", ForeignKey("delegators.address_id")),
    Column("winning_likelyhood", Float),
    Column("pool_owner", Boolean),
    Column("lottery_id", ForeignKey("lotteries.uuid")),
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
    Column("delegator", ForeignKey("delegators.address_id")),
    Column("lottery_strategy", ForeignKey("lottery_strategies.id")),
    Column("winning_likelyhood", Float),
    Column("owners_allowed", Boolean),
)

lottery_strategy_types = Table(
    "lottery_strategy_types",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("name", String)
)


lottery_winners = Table(
    "lottery_winners",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("lottery_ticket_id", ForeignKey("lottery_tickets.id")),
    Column("lottery_id", ForeignKey("lotteries.uuid")),
    Column("rank", Integer),
)


def start_mappers():
    delegators_mapper = mapper(models.Delegator, delegators)
    lottery_tickets_mapper = mapper(models.LotteryTicket, lottery_tickets)
    lottery_winners_mapper = mapper(models.LotteryWinner, lottery_winners)
    lottery_strategy_types_mapper = mapper(models.LotteryStrategyType, lottery_strategy_types)
    lotteries_mapper = mapper(models.Lottery,
                              lotteries,
                              properties={
        "winners": relationship(
            lottery_winners_mapper,
            collection_class=set,),
      "lottery_tickets": relationship(
          lottery_tickets_mapper,
          collection_class=set, ),

        })



    pool_owners_mapper = mapper(models.PoolOwner, pool_owners)
    mapper(
        models.Pool,
        pools,
        properties={
            "_owners": relationship(
                pool_owners_mapper,
                collection_class=set,
            )
        },
    )
