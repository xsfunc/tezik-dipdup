from decimal import Decimal
from typing import cast

from dipdup.context import HandlerContext
from dipdup.models import Transaction

from quipuswap import models
from quipuswap.types.fa2_token.storage import Fa2TokenStorage
from quipuswap.types.quipu_fa2.storage import QuipuFa2Storage
from quipuswap.types.fa2_token.parameter.transfer import TransferParameter
from quipuswap.types.quipu_fa2.parameter.tez_to_token_payment import (
    TezToTokenPaymentParameter,
)


async def on_fa2_tez_to_token(
    ctx: HandlerContext,
    tez_to_token_payment: Transaction[TezToTokenPaymentParameter, QuipuFa2Storage],
    transfer: Transaction[TransferParameter, Fa2TokenStorage],
) -> None:
    decimals = int(ctx.template_values["decimals"])
    symbol = cast(str, ctx.template_values["symbol"])
    trader = tez_to_token_payment.data.sender_address

    transfer_params = transfer.parameter.__root__[0].txs[0]
    token_id = int(transfer_params.token_id)
    token_amount = Decimal(transfer_params.amount) / (10**decimals)

    tez_amount = Decimal(tez_to_token_payment.data.amount) / (10**6)
    min_token = Decimal(tez_to_token_payment.parameter.min_out) / (10**decimals)

    slippage = 1 - (min_token / token_amount)
    price = tez_amount / token_amount

    trade = models.Trade(
        symbol=symbol,
        trader=trader,
        side=models.TradeSide.BUY,
        quantity=token_amount,
        price=price,
        slippage=slippage,
        token_address=f'{transfer.data.target_address}_{token_id}',
        level=transfer.data.level,
        timestamp=transfer.data.timestamp,
    )
    await trade.save()
