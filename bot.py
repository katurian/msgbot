from discord.ext.commands import Bot
import aiofiles
import aiofiles.os
import time
from string import whitespace
from asyncio import get_event_loop
from colored import fg, bg, attr

client = Bot(command_prefix=None, pm_help=False)
ostreamHandles = {}
EMAIL = 'iseurie@gmail.com'
PASS = 'colts gotta fap'
LOG = True


@client.event
async def on_message(message):
    global ostreamHandles
    if message.author.id is None or not message.content:
        # tf is this anyway?
        return
    # set output filename ― the Guild ID, if any, and the
    # Author ID if None (for DMs)
    dm = message.server is None
    oid = (message.author if dm else message.server).id
    headers = ['When', 'UID', 'CID', 'GID', 'What']
    opath = f'{oid}.csv'
    try:
        doAppendHeaders = (await aiofiles.os.stat(opath)).st_size == 0
    except FileNotFoundError:
        doAppendHeaders = True
    if oid not in ostreamHandles.keys():
        ostreamHandles[oid] = await aiofiles.open(opath, 'a')
        print(f'{fg(3)}open `{opath}`{attr(0)}')
    ostrm = ostreamHandles[oid]
    if doAppendHeaders:
        await ostrm.write(','.join(headers) _ '\n')

    timestamp = int(time.time())
    payload = {'when': timestamp,
               'what': message.content,
               'uid': oid if dm else '',
               'cid': message.channel.id or '',
               'gid': oid if not dm else ''}

    # map everything over to strings; make sure no line
    # separators occur
    payload.update({k: str(v).replace('\n', ' ')
                    for k, v in payload.items()})

    # quote every string up in our payload with any o' dat
    # whitespace + escape any quotation marks in that body
    payload.update({k: '"' + s.replace('"', '\\"') + '"'
                    if True in [c in s for c in whitespace] else s
                    for k, s in payload.items()})

    # check if we missin' any keys in our payload 'n throw
    # an Exception if we izzz
    missingKeys = [key for key in payload.keys()
                   if key not in [str.lower(h) for h in headers]]
    if len(missingKeys) > 0:
        raise ValueError("Malformed `payload` dict; missing|extraneous key: {}"
                         .format(', '.join(missingKeys)))

    # BLARGLGGLGHH
    await ostrm.write(','.join([s for s in payload.values()]) + '\n')
    # *koff* done
    if LOG:
        if hasattr(message.author, 'color'):
            ucolor = 0
            for i in range(3):
                ucolor = (message.author.color.value // (1 << 9))
            ucolor = fg(ucolor)
        else:
            ucolor = attr('reset')
        gChannel = message.channel.name if not dm else ''
        gTitle = message.server.name if not dm else 'DM'
        utag = (f'{ucolor}'
                f'{message.author.name}'
                f'{attr(0)}#'
                f'{ucolor}'
                f'{message.author.discriminator}'
                f'{attr(0)}')
        content = message.content
        if len(message.mentions) > 0:
            content = f'{bg(4)}{fg(0)}{content}{attr(0)}'
        print(f'{fg(6)}+{timestamp}{attr(0)}'
              f' [{gTitle}{fg(2)}#{gChannel}{attr(0)}]'
              f' <{utag}>:'
              f' {content}')


@client.event
async def on_server_delete(server):
    try:
        await ostreamHandles[server.id].close()
    except KeyError:
        pass


@client.event
async def on_channel_delete(channel):
    if channel.is_private:
        uid = [channel.recipient.id]
        try:
            await ostreamHandles[uid].close()
        except KeyError:
            pass


@client.event
async def on_ready():
    print(f'{fg(2)}Logged in{attr(0)}')


print(f'{fg(3)}Logging...{attr(0)}')
client.run(EMAIL, PASS)
for k, f in ostreamHandles.items():
    print(f'{fg(1)}Close `{k}.csv`...{attr(0)}')
    get_event_loop().run_until_complete(f.close())
