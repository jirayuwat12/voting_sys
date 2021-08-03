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

#check passcode and logo
def checkpasscode(passcode,logo_id):
    #have that logoid?
    logo_id = str(logo_id)
    passcode  = str(passcode)
    if not logo_id in logo_id_list:
        return False
    #is passcode match logoid? ----- same logic
    #is that passcode valid?   --/
    dt = firebase.child('passcode').get().val()
    if logo_id[:2] == '60' and not passcode in str(dt['y60']):
        return False
    elif logo_id[:2] == '61' and not passcode in str(dt['y61']):
        return False
    elif logo_id[:2] == '62' and not passcode in str(dt['y62']):
        return False
    elif logo_id[:2] == '63' and not passcode in str(dt['y63']):
        return False
    elif logo_id[:2] == '64' and not passcode in str(dt['y64']):
        return False
    elif logo_id[:2] == '00' and not passcode in str(dt['ygraduate']):
        return False
    return True
def is_passcode_vote(passcode,logo_id):
    dt = firebase.child('voted_user').get()
    for x in dt.each():
        if str(x.key()) == passcode and str(logo_id) != str(x.val()):
            return True
    return False
#vote command 
@bot.command()
@commands.dm_only()
async def vote(ctx,passcode,logo_id):
    if firebase.child('can_vote').get().val():
        if(checkpasscode(passcode,logo_id)):
            if is_passcode_vote(passcode,logo_id):
                voted_logo_id = firebase.child('voted_user').child(passcode).get().val()
                data = {
                    "sumary_vote/{0}".format(logo_id): 1 + int(firebase.child('sumary_vote').child(logo_id).get().val()),
                    "sumary_vote/{0}".format(voted_logo_id): int(firebase.child('sumary_vote').child(voted_logo_id).get().val()) - 1,
                    "voted_user/{0}".format(passcode):str(logo_id)
                }
                firebase.update(data)
                await ctx.author.send("คุณได้โหวด {0} ด้วยpasscode {1} เรียบร้อย!!!".format(logo_id,passcode))
            elif str(logo_id) != firebase.child('voted_user').child(passcode).get().val():
                data = {
                    "sumary_vote/{0}".format(logo_id): 1 + firebase.child('sumary_vote').child(logo_id).get().val(),
                    "sumary_vote/all_vote": 1 + firebase.child('sumary_vote').child('all_vote').get().val(),
                    "voted_user/{0}".format(passcode):str(logo_id)
                }
                firebase.update(data)
                await ctx.author.send("คุณได้โหวด {0} ด้วยpasscode {1} เรียบร้อย!!!".format(logo_id,passcode))
            else:
                embed = discord.Embed(title = 'ไม่สามารถโหวดได้ เพราะ',color = 0xFF0032)
                embed.add_field(name = '1.ไม่สามารถโหวดข้ามปีได้',value='----------------------',inline=False)
                embed.add_field(name = '2.passcode ไม่ถูกต้อง',value='----------------------',inline=False)
                embed.add_field(name = '3.เคยโหวตlogoนี้ไปแล้ว',value='----------------------',inline=False)
                embed.add_field(name = '4.logo id ไม่ถูกต้อง',value='----------------------',inline=False)
                embed.add_field(name = 'กรุณาติดต่อ อ.นัทที หรือ อ.เจษฏา',value='----------------------',inline=False)
                
                await ctx.author.send(embed = embed)
        else:
            embed = discord.Embed(title = 'ไม่สามารถโหวดได้ เพราะ',color = 0xFF0032)
            embed.add_field(name = '1.ไม่สามารถโหวดข้ามปีได้',value='----------------------',inline=False)
            embed.add_field(name = '2.passcode ไม่ถูกต้อง',value='----------------------',inline=False)
            embed.add_field(name = '3.เคยโหวตlogoนี้ไปแล้ว',value='----------------------',inline=False)
            embed.add_field(name = '4.logo id ไม่ถูกต้อง',value='----------------------',inline=False)
            embed.add_field(name = 'กรุณาติดต่อ อ.นัทที หรือ อ.เจษฏา',value='----------------------',inline=False)
            
            await ctx.author.send(embed = embed)
    else:
        await ctx.channel.send('Can\'t vote now')

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

#return did user vote
@bot.command()
async def didivote(ctx,passcode):
    i = firebase.child('voted_user').get()
    for x in i.each():
        if(int(passcode) == int(x.key())):
            await ctx.author.send("{0} has been voted for {1}".format(passcode,x.val()))
            break
    else:
        await ctx.author.send("{0} hasn't vote yet".format(passcode))

@bot.command()
async def backup(ctx):
    bu.backup()
    await ctx.channel.send('success')

#delete what that passcode vote
@bot.command()
async def devote(ctx,passcode):
    temp = firebase.child('voted_user').child(str(passcode)).get().val()
    if temp == None:
        await ctx.channel.send('{0} didn\'t vote yet'.format(passcode))
    else:
        temp_num_vote = firebase.child('sumary_vote').child(temp).get().val()
        temp_all_vote = firebase.child('sumary_vote').child('all_vote').get().val()
        firebase.child('sumary_vote').child(temp).set(int(temp_num_vote)-1)
        firebase.child('sumary_vote').child('all_vote').set(int(temp_all_vote)-1)
        firebase.child('voted_user').child(passcode).remove()
        await ctx.channel.send('deleted')

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