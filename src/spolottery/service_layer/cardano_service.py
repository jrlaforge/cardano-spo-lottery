from http import HTTPStatus
import abc
import asyncio
import datetime
from functools import wraps
import logging
import pprint
from typing import Coroutine, List, Sequence
from spolottery.domain import models
from blockfrost import BlockFrostApi, ApiUrls, ApiError
from aiohttp import ClientSession
import httpx

log = logging.getLogger(__name__)


class MaxPoolDelegators(Exception):
    pass


async def make_one_request(url: str, num: int, headers: dict, params: dict, limit, id, client) -> dict:

    # No more than 3 concurrent workers will be able to make
    # get request at the same time.
    async with limit:
        log.info(f"Making request {num}")

        r = await client.get(url, params=params, headers=headers)

        # When workers hit the limit, they'll wait for a second
        # before making more requests.
        if limit.locked():
            log.info("Concurrency limit reached, waiting ...")
            await asyncio.sleep(1)

        if r.status_code == HTTPStatus.OK:
            return {"result": r, "id": id}

    raise ValueError(
        f"Unexpected Status: Http status code is {r.status_code}.",
    )


async def prepare_delegators_requests(url: str, delegators: List[models.Delegator], headers: dict, params: dict) -> list[httpx.Response]:
    tasks = []
    i = 0
    limit = asyncio.Semaphore(25)
    transport = httpx.AsyncHTTPTransport(retries=3)
    client = httpx.AsyncClient(transport=transport)
    for delegator in delegators:
        i = i + 1
        url_delegator = f"{url}{delegator.address_id}/history"
        task = asyncio.create_task(make_one_request(
            url_delegator, i, headers, params, limit, delegator.address_id, client))
        tasks.append(task)

    results = await asyncio.gather(*tasks)

    return results


async def prepare_pool_metadata_requests(url: str, pools: List[models.Pool], headers: dict, params: dict) -> list[httpx.Response]:
    tasks = []
    i = 0
    limit = asyncio.Semaphore(10)
    client = httpx.AsyncClient()
    for pool_id in pools:
        i = i + 1
        url_delegator = f"{url}/pools/{pool_id}/metadata"
        task = asyncio.create_task(make_one_request(
            url_delegator, i, headers, params, limit, pool_id, client))
        tasks.append(task)

    results = await asyncio.gather(*tasks)

    return results


class AbstractCardanoService(abc.ABC):
    @abc.abstractmethod
    async def get_all_pools(self, pool_stored: List[models.Pool]) -> List[models.Pool]:
        raise NotImplementedError

    async def get_pool_delegators(self, pool_id: str) -> List[models.Delegator]:
        raise NotImplementedError

    async def get_delegators_history(self, delegators: List[models.Delegator]) -> List[models.Delegator]:
        raise NotImplementedError


class BlockFrostCardanoService(AbstractCardanoService):

    counter = 0

    def __init__(self, config):
        self.api = BlockFrostApi(
            project_id=config.get_blockfrost_project_id(),
            # or export environment variable BLOCKFROST_PROJECT_ID
            # optional: pass base_url or export BLOCKFROST_API_URL to use testnet, defaults to ApiUrls.mainnet.value
            base_url=ApiUrls.mainnet.value,
        )
        self.api_account_url = ApiUrls.mainnet.value + "/v0/accounts/"
        self.api_pool_metadata_url = ApiUrls.mainnet.value + "/v0/"
        self.max_delegators_allowed = config.max_delegators_allowed

    async def get_all_pools(self, pool_stored: List[models.Pool]) -> List[models.Pool]:
        pools = []
        try:

            pools_ids = self.api.pools(page=1, gather_pages=True)
            i = 0

            # Delete pools id already stored
            pool_ids_stored = [pool.pool_id for pool in pool_stored]

            count_fresh_pool_ids = len(pools_ids)
            pools_ids = [
                pool_id for pool_id in pools_ids if pool_id not in pool_ids_stored]
            log.info("{} pools already encoded".format(
                count_fresh_pool_ids - len(pools_ids)))

            blockfrost_url = self.api_pool_metadata_url
            default_headers = {'project_id': self.api.project_id,
                               'User-Agent': 'blockfrost-python 0.3.0'}
            query_parameters = {'count': 50, "order": "desc"}

            pools_metadata = await prepare_pool_metadata_requests(blockfrost_url, pools_ids,
                                                                  default_headers, query_parameters)
            log.info("{} pools metadata found".format(len(pools_metadata)))

            # for pool_metadata in pools_metadata:
            #     pm = pool_metadata['result'].json()
            #     if "pool_id" in pm:
            #         p = models.Pool(pool_id=pm["pool_id"], hex=pm["hex"], url=pm["url"],
            #                         ticker=pm["ticker"], name=pm["name"], description=pm["description"],
            #                         updated_at=datetime.datetime.utcnow())

            for pool_metadata in pools_metadata:
                pm = pool_metadata['result'].json()

                if "pool_id" in pm:
                    p = models.Pool(pool_id=pm["pool_id"], hex=pm["hex"], url=pm["url"],
                                    ticker=pm["ticker"], name=pm["name"], description=pm["description"],
                                    updated_at=datetime.datetime.utcnow())

                    pool_with_owners = self.api.pool(
                        pool_id=pm["pool_id"], page=1, gather_pages=True)

                    owners = []

                    if hasattr(pool_with_owners, "pool_id") and hasattr(pool_with_owners, "owners"):
                        for po in pool_with_owners.owners:
                            p.add_pool_owner(models.PoolOwner(
                                address_id=po, pool_id=pool_with_owners.pool_id))

                    pools.append(p)
                else:
                    log.info("No metada for this pool : {}".format(
                        pool_metadata['id']))

                i = i+1

        except ApiError as e:
            log.exception(e)

        return pools

    async def get_pool_delegators(self, pool_id: str) -> List[models.Delegator]:
        delegators = []

        try:

            pool_delegators = self.api.pool_delegators(
                pool_id, page=1, gather_pages=True)
            count_delegators = len(pool_delegators)
            if count_delegators > self.max_delegators_allowed:
                raise MaxPoolDelegators(
                    "The maximum numbers of delegators has been reached : {} - {}".format(count_delegators, pool_id))
            for delegator in pool_delegators:
                delegators.append(models.Delegator(
                    address_id=delegator.address, live_stake=int(delegator.live_stake)))

        except ApiError as e:
            log.exception(e)

        return delegators

    async def get_delegators_history(self, delegators: List[models.Delegator]) -> List[models.Delegator]:
        blockfrost_url = self.api_account_url
        default_headers = {'project_id': self.api.project_id,
                           'User-Agent': 'blockfrost-python 0.3.0'}
        query_parameters = {'count': 50, "order": "desc"}

        account_delegations_histories = await prepare_delegators_requests(blockfrost_url, delegators,
                                                                          default_headers, query_parameters)

        for account_delegation_history in account_delegations_histories:
            try:
                account_history_raw = account_delegation_history['result'].json(
                )
                account_history = set()
                for history in account_history_raw:

                    account_history.add(models.Delegation(pool_id=history['pool_id'], amount=history['amount'],
                                        epoch_no=history['active_epoch']))  # No need of the pool id in the delegation
                delegator = next(
                    x for x in delegators if x.address_id == account_delegation_history['id'])
                delegator.delegation_history = account_history
            except Exception as e:
                print(e)

            return delegators
