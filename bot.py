from discord.ext.commands import Bot
import aiofiles
import aiofiles.os
import time
from string import whitespace
from asyncio import get_event_loop
from colored import fg, bg, attr

client = Bot(command_prefix=None, pm_help=False)
ostreamHandles = {}


@client.event
async def on_message(message):
    global ostreamHandles  # declare mutation to global handle store
    global LOG
    headers = ['When', 'UID', 'CID', 'GID', 'What']

    if message.author.id is None or not message.content:
        # if something is fucky, just quit
        return
    dm = message.server is None  # True if private message, False else

    # set output filename ― the Guild ID, if any, and the
    # Author ID if None (for DMs)
    oid = (message.author if dm else message.server).id
    opath = f'{oid}.csv'  # id.csv
    try:
        doAppendHeaders = (await aiofiles.os.stat(opath)).st_size == 0
    except FileNotFoundError:
        # ensure that headers will be appended upon creation
        doAppendHeaders = True
    if oid not in ostreamHandles.keys():  # if oid isn't a key
        ostreamHandles[oid] = await aiofiles.open(opath, 'a')
        if LOG:
            print(f'{fg(3)}open `{opath}`{attr(0)}')
    ostrm = ostreamHandles[oid]
    if doAppendHeaders:
        await ostrm.write(','.join(headers) + '\n')

    timestamp = int(time.time())
    payload = {'when': timestamp,
               'what': message.content,
               'uid': message.author.id,
               'cid': message.channel.id or '',
               'gid': '' if dm else oid}

    # map everything over to strings; make sure no line
    # separators occur
    for key, value in payload.items():
        payload[key] = str(value).replace('\n', ' ')

    # quote every string up in our payload with any
    # whitespace + escape any quotation marks in that body
    for key, text in payload.items():
        has_whitespace = True in {ws in text for ws in whitespace}
        if has_whitespace:
            payload[key] = '"' + text.replace('"', '\\"') + '"'

    lHeaders = [head.lower() for head in headers]
    # Set difference: Everything included in lHeaders, but
    # not included in payload.keys()
    missingKeys = set(lHeaders) - set(payload.keys())

    if len(missingKeys) != 0:
        raise ValueError("Malformed `payload` dict; missing key: {}"
                         .format(', '.join(missingKeys)))

    # write comma-delimited payload values to the file and break
    values = [payload[k] for k in lHeaders]
    await ostrm.write(','.join(values) + '\n')
    if LOG:  # if we're logging,
        gChannel = message.channel.name or ''
        gTitle = message.server.name if not dm else 'DM'
        utag = (
                # f'{ucolor}'
                f'{message.author.name}'
                # f'{attr(0)}#'
                # f'{ucolor}'
                f'{message.author.discriminator}'
                # f'{attr(0)}'
                )
        content = message.content
        if len(message.mentions) != 0:
            content = f'{bg(4)}{fg(0)}{content}{attr(0)}'
        # $ $ $
        print(f'{fg(6)}+{timestamp}{attr(0)}'
              f' [{gTitle}{fg(2)}#{gChannel}{attr(0)}]'
              f' <{utag}>:'
              f' {content}')


@client.event
async def on_server_delete(server):
    try:
        # clean up file handle
        await ostreamHandles[server.id].close()
    except KeyError:
        pass


@client.event
async def on_channel_delete(channel):
    if channel.is_private:
        uid = [channel.recipient.id]
        try:
            # clean up file handle
            await ostreamHandles[uid].close()
        except KeyError:
            pass


@client.event
async def on_ready():
    if LOG:
        print(f'{fg(2)}Logged in{attr(0)}')

if __name__ == '__main__':
    import argparse
    from sys import stderr
    parser = argparse.ArgumentParser(
        description='Collect discord message data in .csv files')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Enable verbose logging', dest='log')
    parser.add_argument('--token', '-t', help='Your auth token', required=True)
    args = parser.parse_args()
    global LOG
    LOG = args.log
    # TODO: Add multiple verbosity levels (just file
    # handles? just messages?  both?)
    try:
        client.run(args.token, bot=False)
    except Exception as what:
        stderr.write(f'Fail starting client session: {what}\n')
        exit(hash(what) % 0x50 + 1)

    for k, f in ostreamHandles.items():
        print(f'{fg(1)}Close `{k}.csv`...{attr(0)}')
        get_event_loop().run_until_complete(f.close())
