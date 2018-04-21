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
               'gid': oid if not dm else ''}

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
        else:
            payload[key] = text

    lHeaders = [head.lower() for head in headers]
    # Set difference: Everything included in lHeaders, but
    # not included in payload.keys()
    missingKeys = set(lHeaders).difference(set(payload.keys()))

    if len(missingKeys) != 0:
        raise ValueError("Malformed `payload` dict; missing key: {}"
                         .format(', '.join(missingKeys)))

    # write comma-delimited payload values to the file and break
    values = [payload[k] for k in lHeaders]
    await ostrm.write(','.join(values) + '\n')
    if LOG:  # if we're logging,
        # guard for author's color attribute; Users don't
        # have one, some server Members do
        if hasattr(message.author, 'color'):
            ucolor = 0  # init ucolor variable
            for i in range(3):
                # decode the color value for each step
                ucolor = (message.author.color.value // (1 << i+1))
            # map the scalar value to a terminal escape code
            ucolor = fg(ucolor)
        else:
            ucolor = attr('reset')
        gChannel = message.channel.name or ''
        gTitle = message.server.name if not dm else 'DM'
        utag = (f'{ucolor}'
                f'{message.author.name}'
                f'{attr(0)}#'
                f'{ucolor}'
                f'{message.author.discriminator}'
                f'{attr(0)}')
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


def parseparams():
    global LOG
    global AUTH

    from sys import argv
    from os import environ
    from re import match

    usage = ['usage:',
             f'{argv[0]} \'<email>\' \'<pass>\'',
             f'{argv[0]} \'<token>\'',
             f'{argv[0]} MSGBOT_TOKEN=\'<token>\'',
             f'{argv[0]} MSGBOT_EMAIL=\'<email>\' MSGBOT_PASS=\'<pass>\'']
    for i, s in enumerate(usage[1:]):
        usage[i+1] = f'    {s}'
    usage = '\n'.join(usage)

    def prnusage():
        print(usage)
        exit(0)

    if True in {x in argv for x in {'-h', '--help'}}:
        prnusage()

    if len(argv) > 1:
        cmdln = ' '.join(argv)
        logflags = {'-v', '--verbose', '-l', '--logging'}
        LOG = True in {p in cmdln for p in logflags}
        argv = [a for a in argv if a not in logflags]
        AUTH = (argv[1]) if len(argv) == 2 else tuple(argv[1:3])
    else:
        env = {k: environ.get('MSGBOT_' + k.upper())
               for k in ['email', 'pass', 'token', 'log']}
        LOG = bool(env['log'])
        if False in {bool(env.get(k)) for k in {'email', 'pass'}}:
            AUTH = (env.get('token'))
        else:
            AUTH = (env[k] for k in ('email', 'pass'))
    if not AUTH:
        prnusage()
        exit(0)


if __name__ == '__main__':
    # TODO: Add multiple verbosity levels (just file
    # handles? just messages?  both?)

    # try:
    parseparams()
    client.run(*AUTH)
    # except Exception as what:
    #     stderr.write(f'Error starting client session: {what}\n')
    #     exit(hash(what) % 0x50 + 1)

    # get rid of any remaining file handles following completion
    # of client event loop
    for k, f in ostreamHandles.items():
        print(f'{fg(1)}Close `{k}.csv`...{attr(0)}')
        get_event_loop().run_until_complete(f.close())
