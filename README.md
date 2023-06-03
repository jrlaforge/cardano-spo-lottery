# Cardano Spo Lottery Backend

Note : Work in progress

## Context

Attracting delegators to stake on their pool is not an easy task for a Cardano stake pool operator.

To help gain in visibility, stake pool operators, in addition to the regular staking rewards provided by the network, might want to give additional rewards to their delegators from time to time.

Either they give free tokens to all their active delegators in a specific epoch or they proceed to give away a very special NFT they have in their collection to a randomly selected tweeter follower.

But what if the stake pool operator wanted to reward delegators based on their loyalty and stake ?

## The tool : a Cardano SPO lottery helper
This tool aims at helping stake pool operators to provide a fair lottery draw amongst their active delegators.

The SPO can now choose a winner amongst its delegators according to the following criteria:

the number of epochs the delegator is actively staking on the pool and
the delegator’s stake amount
Every delegator has a winning likelihood weighted by its loyalty (# of active epochs delegated to the pool) and its stake (ADA amount).

A delegator is represented by his stake address. If the lottery involves a price, the delegator’s wallet address can be easily found via his stake address.

Note : the stake pool operator has also the option to create lottery where each delegator has the same winning likelyhood.

More info : https://www.hippo-pool.com/blog/how-it-works-spo-lottery/

## Install

```
source venv/bin/activate
pip install -r requirements.txt
pip install -e src/

make test
```

## Run 

```
cp .template.env cp .env
# Set your env vars
source .env
FLASK_APP=spolottery.entrypoints.flaskapp FLASK_DEBUG=1 flask run --port=4500


docker-compose build && docker-compose up -d && docker-compose logs
```

## Alembic 

```
cp alembic.ini.tpl alembic.ini 
#edit alembic.ini psql settings
alembic revision --autogenerate -m "Add min live stake"
alembic current
alembic upgrade head


alembic downgrade -1
```

