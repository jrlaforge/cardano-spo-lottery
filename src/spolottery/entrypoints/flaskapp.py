import json
import logging
import traceback
import bleach
from flask import request, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from spolottery.entrypoints import create_app

import spolottery.config as config
from spolottery.adapters import dto, orm
from spolottery.adapters import repository
from spolottery.service_layer import services, unit_of_work
# from tests.conftest import wait_for_postgres_to_come_up
from spolottery.service_layer.cardano_service import BlockFrostCardanoService

orm.start_mappers()
get_session = sessionmaker(bind=create_engine(config.get_postgres_uri()))
engine = create_engine(config.get_postgres_uri())
# wait_for_postgres_to_come_up(engine)
orm.metadata.create_all(engine)
app = create_app()

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@app.route("/pool/filter", methods=["POST"])
def filter_pool():
    """
    Search a pool
    """
    # session = get_session()
    # pool_repo = repository.SqlAlchemyPoolRepository(session)

    try:
        pool_filter = bleach.clean(request.json["pool_filter"])
        pools = services.search_pool(
            pool_filter,
            unit_of_work.SqlAlchemyUnitOfWork()
        )
    except Exception as e:
        logger.exception(e)
        return {"message": str(e)}, 400

    return jsonify(pools=[p.serialize() for p in pools])


@app.route("/lottery", methods=["POST"])
async def create_lottery():
    """
    Create a lottery
    """
    logger.info("Create lottery")
    uow = unit_of_work.SqlAlchemyUnitOfWork()
    cardano_service = BlockFrostCardanoService(config)
    try:

        lottery_details = request.json["lottery_details"]
        # Sanitize input
        lottery_details = {k: bleach.clean(v) if isinstance(v, str) else v
                           for k, v in lottery_details.items()}

        lottery_input_dto = dto.LotteryInputDto(**lottery_details)
        pool_id = lottery_input_dto.pool_id
        start_epoch = lottery_input_dto.start_epoch
        end_epoch = lottery_input_dto.end_epoch
        count_epochs = lottery_input_dto.count_epochs
        draw_date = lottery_input_dto.draw_date
        lottery_strategy_name = lottery_input_dto.lottery_strategy_name
        owners_allowed = lottery_input_dto.owners_allowed
        lottery_name = lottery_input_dto.lottery_name
        min_live_stake = lottery_input_dto.min_live_stake

        lottery_dto = await services.create_lottery(pool_id, start_epoch, end_epoch, count_epochs,
                                                    draw_date, lottery_strategy_name, owners_allowed, min_live_stake,
                                                    lottery_name, uow, cardano_service)
    except Exception as e:
        logger.exception(e)
        return {"message": str(e)}, 400

    return lottery_dto.json(), 201


@app.route("/lottery/<string:lottery_id>", methods=["GET"])
async def get_lottery(lottery_id):
    """
    Get a lottery
    """
    lottery = ""
    try:
        logger.info("Get lottery : {}".format(lottery_id))
        session = get_session()
        lottery_repo = repository.SqlAlchemyLotteryRepository(session)
        lottery_dto = await services.get_lottery(lottery_id, lottery_repo, True)
    except Exception as e:
        logger.exception(e)
        return {"message": "No Lottery found"}, 400

    return lottery_dto.json(), 200
