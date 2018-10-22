from trezor import config, ui, wire
from trezor.crypto import bip39

from trezor.messages.ButtonRequest import ButtonRequest
from trezor.messages.ButtonRequestType import MnemonicInput, MnemonicWordCount, Other
from trezor.messages.MessageType import ButtonAck
from trezor.messages.Success import Success
from trezor.pin import pin_to_int
from trezor.ui.mnemonic import MnemonicKeyboard
from trezor.ui.text import Text
from trezor.ui.word_select import WordSelector
from trezor.ui.share_word_select import ShareWordSelector
from trezor.utils import format_ordinal

from apps.common import storage
from apps.common.confirm import confirm, require_confirm
from apps.management.change_pin import request_pin_confirm
from apps.common.ssss import Collector

async def recovery_device(ctx, msg):
    """
    Recover BIP39 seed into empty device.

    1. Ask for the number of words in recovered seed.
    2. Let user type in the mnemonic words one by one.
    3. Optionally check the seed validity.
    4. Optionally ask for the PIN, with confirmation.
    5. Save into storage.
    """
    if not msg.dry_run and storage.is_initialized():
        raise wire.UnexpectedMessage("Already initialized")

    # ask for the number of words
    recover_shared = await recover_from_shares(ctx)

    # ask for the number of words
    wordcount = None
    
    mnemonic = None
    if not recover_shared:
        # ask for mnemonic words one by one
        wordcount = await request_wordcount(ctx)
        mnemonic = await request_mnemonic(ctx, wordcount) 

        # check mnemonic validity
        if msg.enforce_wordlist or msg.dry_run:
            if not bip39.check(mnemonic):
                raise wire.ProcessError("Mnemonic is not valid")
    else:
        wordcount = await request_share_wordcount(ctx)

        collector = Collector()
        while collector.sharesRemaining() > 0:

            share_mnemonic = await request_mnemonic(ctx, wordcount)
            share_entropy = bip39.entropy(share_mnemonic)
            collector.collectShare(share_entropy)
            remaining = collector.sharesRemaining()
            if remaining > 0:
                await require_confirm_shares_remaining(ctx, remaining)

        entropy = collector.recoverSecret()
        mnemonic = bip39.from_data(entropy)

    # ask for pin repeatedly
    if msg.pin_protection:
        newpin = await request_pin_confirm(ctx, cancellable=False)

    # save into storage
    if not msg.dry_run:
        if msg.pin_protection:
            config.change_pin(pin_to_int(""), pin_to_int(newpin), None)
        storage.load_settings(label=msg.label, use_passphrase=msg.passphrase_protection)
        storage.load_mnemonic(mnemonic=mnemonic, needs_backup=False, no_backup=False)
        return Success(message="Device recovered")
    else:
        if storage.get_mnemonic() == mnemonic:
            return Success(
                message="The seed is valid and matches the one in the device"
            )
        else:
            raise wire.ProcessError(
                "The seed is valid but does not match the one in the device"
            )


async def recover_from_shares(ctx):
    text = Text("Device recovery", ui.ICON_RECOVERY)
    text.normal("Recover from", "shared secret?")
    return await confirm(ctx, text, Other)


@ui.layout
async def request_wordcount(ctx):
    await ctx.call(ButtonRequest(code=MnemonicWordCount), ButtonAck)

    text = Text("Device recovery", ui.ICON_RECOVERY)
    text.normal("Number of words?")
    count = await ctx.wait(WordSelector(text))

    return count

@ui.layout
async def request_share_wordcount(ctx):
    await ctx.call(ButtonRequest(code=MnemonicWordCount), ButtonAck)

    text = Text("Device recovery", ui.ICON_RECOVERY)
    text.normal("Number of words?")
    count = await ctx.wait(ShareWordSelector(text))

    return count

@ui.layout
async def request_mnemonic(ctx, count: int) -> str:
    await ctx.call(ButtonRequest(code=MnemonicInput), ButtonAck)

    words = []
    board = MnemonicKeyboard()
    for i in range(count):
        board.prompt = "Type the %s word:" % format_ordinal(i + 1)
        word = await ctx.wait(board)
        words.append(word)

    return " ".join(words)

async def require_confirm_shares_remaining(ctx, remaining):
    text = Text("Device recovery", ui.ICON_RECOVERY)
    text.normal("{:d} shares to go".format(remaining))
    await confirm(ctx, text, Other, cancel=None)
