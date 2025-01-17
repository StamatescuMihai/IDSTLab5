#!./.bot/bin/python
 
import discord      # base discord module
import code         # code.interact
import os           # environment variables
import inspect      # call stack inspection
import random       # dumb random number generator
 
from discord.ext import commands    # Bot class and utils
 
################################################################################
############################### HELPER FUNCTIONS ###############################
################################################################################
 
# log_msg - fancy print
#   @msg   : string to print
#   @level : log level from {'debug', 'info', 'warning', 'error'}
def log_msg(msg: str, level: str):
    # user selectable display config (prompt symbol, color)
    dsp_sel = {
        'debug'   : ('\033[34m', '-'),
        'info'    : ('\033[32m', '*'),
        'warning' : ('\033[33m', '?'),
        'error'   : ('\033[31m', '!'),
    }
 
    # internal ansi codes
    _extra_ansi = {
        'critical' : '\033[35m',
        'bold'     : '\033[1m',
        'unbold'   : '\033[2m',
        'clear'    : '\033[0m',
    }
 
    # get information about call site
    caller = inspect.stack()[1]
 
    # input sanity check
    if level not in dsp_sel:
        print('%s%s[@] %s:%d %sBad log level: "%s"%s' % \
            (_extra_ansi['critical'], _extra_ansi['bold'],
             caller.function, caller.lineno,
             _extra_ansi['unbold'], level, _extra_ansi['clear']))
        return
 
    # print the damn message already
    print('%s%s[%s] %s:%d %s%s%s' % \
        (_extra_ansi['bold'], *dsp_sel[level],
         caller.function, caller.lineno,
         _extra_ansi['unbold'], msg, _extra_ansi['clear']))
 
################################################################################
############################## BOT IMPLEMENTATION ##############################
################################################################################
 
# bot instantiation
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)
 
# on_ready - called after connection to server is established
@bot.event
async def on_ready():
    log_msg('logged on as <%s>' % bot.user, 'info')
 
# on_message - called when a new message is posted to the server
#   @msg : discord.message.Message
@bot.event
async def on_message(msg):
    # filter out our own messages
    if msg.author == bot.user:
        return
 
    log_msg('message from <%s>: "%s"' % (msg.author, msg.content), 'debug')
 
    # overriding the default on_message handler blocks commands from executing
    # manually call the bot's command processor on given message
    await bot.process_commands(msg)
	
 
# roll - rng chat command
#   @ctx     : command invocation context
#   @max_val : upper bound for number generation (must be at least 1)
@bot.command(brief='Generate random number between 1 and <arg>')
async def roll(ctx, max_val: int):
    # argument sanity check
    if max_val < 1:
        raise Exception('argument <max_val> must be at least 1')
 
    await ctx.send(random.randint(1, max_val))
 
# roll_error - error handler for the <roll> command
#   @ctx     : command that crashed invocation context
#   @error   : ...
@roll.error
async def roll_error(ctx, error):
    await ctx.send(str(error))
    
@bot.command(brief='Joins the voice chat you are currently in')
async def join(ctx):
	if ctx.author.voice is None:
		raise Exception('You must join a voice channel first')
	await ctx.author.voice.channel.connect()
	await ctx.send("Joined voice channel")
    
@join.error
async def join_error(ctx, error):
    await ctx.send(str(error))
    
@bot.command(brief='Leaves the voice chat the bot is currently in')
async def leave(ctx):
    if ctx.voice_client is None:
        raise Exception('Bot must be connected to a voice channel first (HINT: !join)')
    await ctx.voice_client.disconnect()
    await ctx.send("Left voice channel")
 
@leave.error
async def leave_error(ctx, error):
    await ctx.send(str(error))
    
@bot.command(brief='Plays a special song')
async def play(ctx):
    if ctx.voice_client is None:
        raise Exception('Bot must be connected to a voice channel first (HINT: !join)')
    source = discord.FFmpegPCMAudio('./song.mp3')
    ctx.voice_client.play(source)
    await ctx.send("Started playing")

@play.error
async def play_error(ctx, error):
    await ctx.send(str(error))
    
@bot.command(brief='Stops playing the song')
async def stop(ctx):
    if ctx.voice_client is None:
        raise Exception('Bot must be connected to a voice channel first (HINT: !join)')
    ctx.voice_client.stop()
    await ctx.send("Stopped playing")

@stop.error
async def stop_error(ctx, error):
    await ctx.send(str(error))

################################################################################
############################# PROGRAM ENTRY POINT ##############################
################################################################################
 
if __name__ == '__main__':
    # check that token exists in environment
    if 'BOT_TOKEN' not in os.environ:
        log_msg('save your token in the BOT_TOKEN env variable!', 'error')
        exit(-1)
 
    # launch bot (blocking operation)
    bot.run(os.environ['BOT_TOKEN'])