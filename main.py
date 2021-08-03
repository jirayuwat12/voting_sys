import discord
import json
from discord import channel
from discord import embeds
from discord import permissions
from discord.ext import commands
from discord.utils import get
from datetime import date,datetime
import pyrebase
import backup as bu
import secret as sc
#bot init
bot = commands.Bot(command_prefix='.',intents = discord.Intents.all())

logo_id_list = []

firebase = pyrebase.initialize_app(sc.config).database( )

#send embed in form of logo show
async def send_embed(channel_id,logo_id,name = '',img_url = '++++',desc = '++++',author_name = "++++",author_link = '++++',author_avatar='++++',year = '++'):
    embed=  discord.Embed(title=name,
        url=img_url,
        description = desc)
    
    embed.set_author(name = author_name,
        url = author_link,
        icon_url=author_avatar)
    
    embed.set_thumbnail(url=img_url)
    embed.set_image(url=img_url)
    embed.add_field(name = "logo id" ,value="{0}".format(logo_id),inline=False)
    embed.add_field(name = "link" ,value="{0}".format(img_url))
    
    channel = bot.get_channel(channel_id)
    await channel.send(embed = embed)

#delete msg before that 10 msges
@bot.command()
async def clear(ctx,num):
    await ctx.channel.purge(limit =int(num))

#open vote show all logo and allow to vote 
@bot.command()
async def open_vote(ctx): 
    channel_ids = {
        'y64' :870647497670934630
        # 'y64':870274577962528838,
        # 'y63':870684868890202172,
        # 'y62':871034841032949801
        # 'y61':871034858854576149,
        # 'y60':871034878148362350,
        # 'ygraduate':871034953889116282,
    }
    for key in channel_ids:
        embed = discord.Embed(title = "โปรดอ่าน")
        embed.add_field(name = "การโหวต",value="ใช้คำสั่ง {0}govote".format('.'))
        ch = bot.get_channel(channel_ids[key])
        await ch.send(embed = embed)
        # data = gotdata[key].val()
        data= firebase.child(key).get().val()
        for x in data:
            await send_embed(channel_ids[key],x['logo_id'],name=x['name'],desc=x['desc'],img_url=x['img_url'],author_name=x['author_name'],author_link=x['author_link'],author_avatar=x['author_avatar'],year=key)
    firebase.child('can_vote').set(True)

#bot DM to user to start vote
@bot.command()
async def govote(ctx):
    await ctx.author.send('ใช้คำสั่งได้แค่ในห้องนี้เท่านั้น')    
    await ctx.author.send("command>> {0}vote passcode logo-id ex-> {0}vote 1234567890 123".format('.'))

@bot.command()
@commands.dm_only()
async def vote(ctx,passcode,logo_id):
    id_voted = False
    for x in firebase.child('voted_user').get().each():
        if x.key() == str(ctx.author.id):
            id_voted = True
            break
    #have this logo id
    if str(logo_id) in str(logo_id_list):
        year = 'y' + logo_id[:2]
        if year == 'y00':
            year = 'ygraduate'
        passcodelist = []
        for x in firebase.child('passcode').child(year).get().each():
            passcodelist.append(x.val())
        #can vote this year
        if str(passcode) in str(passcodelist):
            #never vote before
            if firebase.child('voted_user').child(ctx.author.id).get().val() == None:
                data = {
                    'voted_user/{0}'.format(ctx.author.id) : {
                        "logo_id" : logo_id,
                        "passcode": passcode
                    },
                    "sumary_vote/{0}".format(logo_id) : int (firebase.child('sumary_vote').child(logo_id).get().val() )+1,
                    "sumary_vote/all_vote" : int(firebase.child('sumary_vote').child('all_vote').get().val() )+ 1
                }
                firebase.update(data)
                await ctx.author.send('ได้โหวต {0} ด้วย passcode {1} สำเร็จ'.format(logo_id,passcode))
            #voted user
            else:
                #wrong passcode
                if firebase.child('voted_user').child(ctx.author.id).get().val()['passcode'] != str(passcode):
                    await ctx.author.send('passcode ผิด')
                #correct passcoed
                else:
                    voted_logo_id = firebase.child('voted_user').child(ctx.author.id).child('logo_id').get().val() 
                    data = {
                        'voted_user/{0}/logo_id'.format(ctx.author.id) : logo_id,
                        "sumary_vote/{0}".format(logo_id) : int (firebase.child('sumary_vote').child(logo_id).get().val() )+1,
                        "sumary_vote/{0}".format(voted_logo_id) : int (firebase.child('sumary_vote').child(voted_logo_id).get().val())-1,
                    }
                    firebase.update(data)
                    await ctx.author.send('ได้โหวต {0} ด้วย passcode {1} สำเร็จ'.format(logo_id,passcode))
        else:
            await ctx.author.send('passcode นี้ไม่สามารถโหวดชั้นปีนี้ได้')
    else:
        await ctx.author.send('ไม่มี logo id นี้')

@bot.command()
@commands.dm_only()
async def myvote(ctx):
    if( firebase.child('voted_user').child(ctx.author.id).get().val() == None ):
        await ctx.author.send('คุณยังไม่ได้โหวต')
    else:
        await ctx.author.send("passcode ของคุณคือ {0} และได้โหวต {1}".format(firebase.child('voted_user').child(ctx.author.id).get().val()['passcode'],firebase.child('voted_user').child(ctx.author.id).get().val()['logo_id']))

#make other can vote
@bot.command()
async def continuevote(ctx):
    firebase.child('can_vote').set(True)
    await ctx.channel.send("can vote now.")

#make other can't vote
@bot.command()
async def pausevote(ctx):
    firebase.child('can_vote').set(False)
    await ctx.channel.send("can't vote now.")

#show how much vote so far
@bot.command()
async def all_votes(ctx):
    all_vote = firebase.child('sumary_vote').get().val()['all_vote']
    await ctx.channel.send("โหวตไป {0} ครั้งแล้ว".format(all_vote))

@bot.command()
async def backup(ctx):
    bu.backup()
    await ctx.channel.send('success')

#delete govote msg command
@bot.event
async def on_message(msg):
    await bot.process_commands(msg)
    #avoid massive msg in main room
    if msg.content == '.govote':
        await msg.delete()
    elif str(msg.content).startswith('.vote'):
        await msg.delete()

#must use comtinue vote everytime after bot open
@bot.event
async def on_ready():
    firebase.child('can_vote').set(True)
    data = firebase.child('y60').get().val()
    #fetch all logo id
    for x in data:
        logo_id_list.append(x['logo_id'])
    data = firebase.child('y61').get().val()
    for x in data:
        logo_id_list.append(x['logo_id'])
    data = firebase.child('y62').get().val()
    for x in data:
        logo_id_list.append(x['logo_id'])
    data = firebase.child('y63').get().val()
    for x in data:
        logo_id_list.append(x['logo_id'])
    data = firebase.child('y64').get().val()
    for x in data:
        logo_id_list.append(x['logo_id'])
    data = firebase.child('ygraduate').get().val()
    for x in data:
        logo_id_list.append(x['logo_id'])

bot.run(sc.bot_key)