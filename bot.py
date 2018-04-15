from discord.ext.commands import Bot
import aiofiles
import aiofiles.os
import time
from string import whitespace
from asyncio import get_event_loop
from colored import fg, bg, attr

client = Bot(command_prefix=None, pm_help=False)
ostreamHandles = {}

EMAIL = 'Email'
PASS = 'pw'
LOG = True

@client.event
async def on_message(message):
    global ostreamHandles  # make sure our function can use the outside variable
    if message.author.id is None or not message.content:  # if something is fucky, just quit
        # tf is this anyway?
        return
    # set output filename - the Guild ID, if any, and the  # no unicode in python files pls thank
    # Author ID if None (for DMs)
    dm = message.server is None  # True if private message, False else
    oid = (message.author if dm else message.server).id  # author ID if private, server ID else
    headers = ['When', 'UID', 'CID', 'GID', 'What']
    opath = f'{oid}.csv'  # id.csv
    try:
        doAppendHeaders = (await aiofiles.os.stat(opath)).st_size == 0  # True if filesize is 0
    except FileNotFoundError:  # if os.stat doesn't find the file
        doAppendHeaders = True  # write the headers anyways
    if oid not in ostreamHandles.keys():  # if oid isn't a key
        ostreamHandles[oid] = await aiofiles.open(opath, 'a')  # we make it a key, with the value being an appending file
        print(f'{fg(3)}open `{opath}`{attr(0)}')  # TODO: this is so very not human readable
    ostrm = ostreamHandles[oid]  # get file object to use from dictionary
    if doAppendHeaders:  # if we're writing headers
        await ostrm.write(','.join(headers) _ '\n')  # write the headers joined by commas to the end of the file
        # TODO: does that underscore even run...?

    timestamp = int(time.time())  # get the time down to the second
    payload = {'when': timestamp,
               'what': message.content,
               'uid': oid if dm else '',  # uid = user id, but only when it's a dm
               'cid': message.channel.id or '',  # TODO: i don't even think this works right? looks like it returns a boolean
               'gid': oid if not dm else ''}  # server id if it's not a dm, otherwise ''

    # map everything over to strings; make sure no line
    # separators occur
    '''
    payload.update({k: str(v).replace('\n', ' ')
                    for k, v in payload.items()})
    '''  # not very understandable at all, overcomplicated
    for key, value in payload.items():
        payload[key] = str(value).replace('\n', ' ')  # replace newlines with spaces

    # quote every string up in our payload with any o' dat
    # whitespace + escape any quotation marks in that body
    '''
    payload.update({k: '"' + s.replace('"', '\\"') + '"'
                    if True in [c in s for c in whitespace] else s
                    for k, s in payload.items()})
    '''  # christ this is worse
    for key, text in payload.items():
        has_whitespace = True in [space_char in text for space_char in whitespace]  # if we find any whitespace in the text, evals to True
        if has_whitespace:
            payload[key] = '"' + text.replace('"', '\\"') + '"'
        else:
            payload[key] = text

    # check if we missin' any keys in our payload 'n throw
    # an Exception if we izzz
    '''
    missingKeys = [key for key in payload.keys()
                   if key not in [str.lower(h) for h in headers]]
    '''
    missingKeys = []
    for key in payload.keys():
        if key not in [str.lower(head) for head in headers]:  # if the key isn't in a lowercase version of headers
            missingKeys.append(key)

    if len(missingKeys) != 0:  # changed from > to != since we won't ever be having negative length | # if we're missing keys
        raise ValueError("Malformed `payload` dict; missing|extraneous key: {}"  # screech
                         .format(', '.join(missingKeys)))

    # BLARGLGGLGHH
    await ostrm.write(','.join([s for s in payload.values()]) + '\n')  # write the payload values separated by commas + \n to the file
    # *koff* done
    if LOG:  # if we're logging
        if hasattr(message.author, 'color'):  # if author has a color attribute
            ucolor = 0  # init ucolor variable
            for i in range(3):
                ucolor = (message.author.color.value // (1 << 9))  # decode the color value for each step
            ucolor = fg(ucolor)  # make a color i guess?
        else:
            ucolor = attr('reset')
        gChannel = message.channel.name if not dm else ''  # channel name if server, otherwise ''
        gTitle = message.server.name if not dm else 'DM'  # server name or DM
        utag = (f'{ucolor}'
                f'{message.author.name}'
                f'{attr(0)}#'
                f'{ucolor}'
                f'{message.author.discriminator}'
                f'{attr(0)}')
        content = message.content
        if len(message.mentions) != 0:  # again, > to != since negative mentions isn't a thing
            content = f'{bg(4)}{fg(0)}{content}{attr(0)}'
        print(f'{fg(6)}+{timestamp}{attr(0)}'
              f' [{gTitle}{fg(2)}#{gChannel}{attr(0)}]'
              f' <{utag}>:'
              f' {content}')  # i hate everything about this


@client.event
async def on_server_delete(server):
    try:
        await ostreamHandles[server.id].close()  # close the file on server delete
    except KeyError:
        pass


@client.event
async def on_channel_delete(channel):
    if channel.is_private:
        uid = [channel.recipient.id]
        try:
            await ostreamHandles[uid].close()  # close the file on channel delete
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
