from trezor import config, ui, wire
from trezor.messages.Success import Success
from trezor.crypto import bip39
from trezor.messages.ButtonRequest import ButtonRequest
from trezor.messages import ButtonRequestType
from trezor.messages.ButtonRequestType import Other
from trezor.messages.MessageType import ButtonAck
from trezor.ui.text import Text
from trezor.ui.share_select import ShareSelector

from apps.common import storage
from apps.common.confirm import confirm
from apps.management.reset_device import (
    check_mnemonic,
    show_mnemonic,
    show_warning,
    show_wrong_entry,
)
from apps.common.ssss import Dealer 

async def backup_device(ctx, msg):
    if not storage.is_initialized():
        raise wire.ProcessError("Device is not initialized")
    if not storage.needs_backup():
        raise wire.ProcessError("Seed already backed up")

    mnemonic = storage.get_mnemonic()

    # warn user about mnemonic safety
    await show_warning(ctx)

    # ask for the number of words
    sharecount = await request_sharecount(ctx)

    storage.set_unfinished_backup(True)
    storage.set_backed_up()

    if sharecount == 1:
        while True:
            # show mnemonic and require confirmation of a random word
            await show_mnemonic(ctx, mnemonic)
            if await check_mnemonic(ctx, mnemonic):
                break
            await show_wrong_entry(ctx)

        storage.set_unfinished_backup(False)
        return Success(message="Seed successfully backed up")

    else:
        entropy = bip39.entropy(storage.get_mnemonic())
        dealer = Dealer(entropy, sharecount)
        shares = 0
        while True:
            share_entropy = dealer.dealShare()
            shares += 1

            share_mnemonic = bip39.from_data(share_entropy)
            await show_mnemonic(ctx, share_mnemonic)
            if dealer.dealingDone():
                if not await confirm_more_shares(ctx):
                    break
        
        storage.set_unfinished_backup(False)
        return Success(message="Seed successfully shared")

@ui.layout
async def request_sharecount(ctx):
    await ctx.call(ButtonRequest(code=Other), ButtonAck)

    text = Text("Backup device", ui.ICON_RECOVERY)
    text.normal("Parts required for restore?")
    count = await ctx.wait(ShareSelector(text))

    return count


async def confirm_more_shares(ctx):
    text = Text("Generate Shares", ui.ICON_CONFIG)
    text.normal("Do want to", "generate more shares?")
    return await confirm(ctx, text, ButtonRequestType.Other)

