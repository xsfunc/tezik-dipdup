from decimal import Decimal
from typing import cast

from dipdup.context import HandlerContext
from dipdup.models import OperationData
from dipdup.models import Transaction

from quipuswap import models
from quipuswap.types.fa12_token.storage import Fa12TokenStorage
from quipuswap.types.quipu_fa12.storage import QuipuFa12Storage
from quipuswap.types.fa12_token.parameter.transfer import TransferParameter
from quipuswap.types.quipu_fa12.parameter.token_to_tez_payment import (
    TokenToTezPaymentParameter,
)


async def on_fa12_token_to_tez(
    ctx: HandlerContext,
    token_to_tez_payment: Transaction[TokenToTezPaymentParameter, QuipuFa12Storage],
    transfer: Transaction[TransferParameter, Fa12TokenStorage],
    tansaction: OperationData,
) -> None:
    symbol = cast(str, ctx.template_values["symbol"])
    decimals = int(ctx.template_values["decimals"])
    trader = token_to_tez_payment.data.sender_address
    token_id = 0

    min_tez = Decimal(token_to_tez_payment.parameter.min_out) / (10**6)
    token_amount = Decimal(token_to_tez_payment.parameter.amount) / (10**decimals)
    tez_amount = Decimal(tansaction.amount) / (10**6)

    price = tez_amount / token_amount
    slippage = 1 - (min_tez / tez_amount)

    trade = models.Trade(
        symbol=symbol,
        trader=trader,
        side=models.TradeSide.SELL,
        quantity=token_amount,
        price=price,
        slippage=slippage,
        token_address=f'{transfer.data.target_address}_{token_id}',
        level=transfer.data.level,
        timestamp=transfer.data.timestamp,
    )
    await trade.save()
