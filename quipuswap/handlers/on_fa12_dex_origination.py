from typing import cast

# from demo_quipuswap.models import Position
from dipdup.exceptions import ContractAlreadyExistsError
from dipdup.models import Origination
from dipdup.context import HandlerContext

from quipuswap.types.quipu_fa12_factory.storage import QuipuFa12FactoryStorage


async def on_fa12_dex_origination(
    ctx: HandlerContext,
    origination: Origination[QuipuFa12FactoryStorage],
) -> None:
    # metadata = ctx.get_metadata_datasource("metadata")

    dex_contract_address = cast(str, origination.data.originated_contract_address)
    token_contract_address = cast(str, origination.storage.storage.token_address)

    try:
        # res = await metadata.get_token_metadata(token_contract_address, 0)
        # symbol = res["symbol"]  # type: ignore
        # decimals = res["decimals"]  # type: ignore

        dex_contract_name = f"dex:fa12:{dex_contract_address[-5:]}"
        token_contract_name = f"fa12:{token_contract_address[-5:]}"

        await ctx.add_contract(
            name=token_contract_name,
            address=token_contract_address,
            typename="fa12_token",
        )
        await ctx.add_contract(
            name=dex_contract_name, address=dex_contract_address, typename="quipu_fa12"
        )
        await ctx.add_index(
            name=dex_contract_name,
            template="quipuswap_fa12_dex",
            values=dict(
                dex_contract=dex_contract_name,
                token_contract=token_contract_name,
                # decimals=decimals,
                # symbol=symbol,
            ),
        )
    except ContractAlreadyExistsError:
        ctx.logger.warning("Contract already exists")

    # for address, value in origination.storage.storage.ledger.items():
    #   shares_qty = value.balance
    #   await Position(trader=address, symbol=symbol, shares_qty=shares_qty).save()
