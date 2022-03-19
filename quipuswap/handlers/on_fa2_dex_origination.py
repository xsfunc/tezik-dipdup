from typing import cast

from dipdup.models import Origination
from dipdup.context import HandlerContext
from dipdup.exceptions import ContractAlreadyExistsError

# from demo_quipuswap.models import Position
from quipuswap.types.quipu_fa12_factory.storage import QuipuFa12FactoryStorage


async def on_fa2_dex_origination(
    ctx: HandlerContext,
    origination: Origination[QuipuFa12FactoryStorage],
) -> None:
    standard = str(ctx.template_values.get("standard", "fa12"))
    metadata = ctx.get_metadata_datasource("metadata")

    dex_contract_address = cast(str, origination.data.originated_contract_address)
    token_contract_address = cast(str, origination.storage.storage.token_address)

    try:
        res = await metadata.get_token_metadata(token_contract_address, 0)
        default_symbol = f"unknown_{standard}"
        default_decimals = "0"

        if res is None:
            symbol = default_symbol
            decimals = default_decimals
        else:
            symbol = res.get("symbol", default_symbol)  # type: ignore
            decimals = res.get("decimals", default_decimals)  # type: ignore

        dex_contract_name = f"dex_{standard}_{symbol}:{dex_contract_address[-5:]}"
        token_contract_name = f"{standard}_{symbol}:{token_contract_address[-5:]}"

        await ctx.add_contract(
            name=token_contract_name,
            address=token_contract_address,
            typename=f"{standard}_token",  # <-
        )
        await ctx.add_contract(
            name=dex_contract_name,
            address=dex_contract_address,
            typename=f"quipu_{standard}",  # <-
        )
        await ctx.add_index(
            name=dex_contract_name,
            template=f"quipuswap_{standard}_dex",  # <-
            values=dict(
                dex_contract=dex_contract_name,
                token_contract=token_contract_name,
                decimals=decimals,
                symbol=symbol,
            ),
        )
    except ContractAlreadyExistsError:
        pass
    except TypeError:
        pass
    except KeyError:
        pass
