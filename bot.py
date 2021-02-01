import discord
from discord.ext import commands, tasks
from discord.utils import get
import youtube_dl
import os
import random
import asyncio
import sys
import re
import functools
from itertools import cycle
import math
from colorama import Fore, Back, Style, init
import youtube_dl
from async_timeout import timeout
from db import DB
from concurrent.futures import ThreadPoolExecutor

#####################################
ver=6.0
build=123.1

init()

client = commands.Bot(command_prefix = '$')
client.remove_command( 'help' )
TOKEN = open('config/token.txt' , 'r').readline()
warnDB = DB("databases/main.db")
usrsDB = DB("databases/main.db")
mainDB = DB("databases/main.db")
gamesDB = DB("databases/main.db")
gamesDB.set("GUESS_NUM", random.randrange(1,10,1))
usrsDB.set("Deftry_name", "Deftry")
usrsDB.set("Deftry_pass", "A6F4h8KK")
usrsDB.set("Deftry_admin", "1")
usrsDB.set("Guest_name", "Guest")
usrsDB.set("Guest_pass", "")
usrsDB.set("Guest_admin", "0")
with open("config/bad-words.txt") as file: 
	bad_words = [bad_word.strip().lower() for bad_word in file.readlines()]
status=cycle(['$help'])
guilds=0
@client.event
async def on_guild_join(guild):
	print("New guild connected!")
	#mainDB.set("guilds", len(await client.fetch_guilds(limit = None).flatten()))
	
async def ainput(prompt: str = "") -> str:
    with ThreadPoolExecutor(1, "AsyncInput") as executor:
        return await asyncio.get_event_loop().run_in_executor(executor, input, prompt)

@client.event
async def on_message(message):
	with open("config/bad-words.txt") as file: 
		bad_words = [bad_word.strip().lower() for bad_word in file.readlines()]
	print(Fore.WHITE)
	print(Back.BLACK)
	print("----------------------------------")
	print(Fore.CYAN)
	print("Chat message:")
	
	print("Guild: " + str(message.guild))
	print("Channel: " + str(message.channel))
	print("Author: " + str(message.author))
	print("Message: " + str(message.content))
	print(Fore.WHITE)
	print(Back.BLACK)
	print("----------------------------------")

	msg = message.content.lower()
	for word in bad_words:
		if word in msg:
			await message.delete()
			

	await client.process_commands(message)

@client.event
async def on_ready():
	#mainDB.set("guilds", len(await client.fetch_guilds(limit = None).flatten()))
	print('Logged in as')
	print(f"Username:  {client.user.name}")
	print(f"User ID:  {client.user.id}")
	print("Firebot " + str(ver) + "(build " + str(build) + ") started")
	print('---------------------------------')
	await client.change_presence(activity=discord.Activity(type=discord.ActivityType.playing,name="$help"))
	change_status.start()
	inputget.start()



@tasks.loop(seconds=10)
async def change_status():
	
	guilds = await client.fetch_guilds(limit = None).flatten()
	await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f'за {len(guilds)} серверами.'))

@tasks.loop(seconds=1)
async def inputget():
	ch = await ainput("channelID: ")
	channel = client.get_channel(id=int(ch))
	await channel.send(await ainput("message: "))
	


@client.command( pass_context = True)
async def login( ctx, username, password=""):
	user = usrsDB.get(username+"_name")
	passget = usrsDB.get(username+"_pass")
	isadmin = usrsDB.get(username+"_admin")
	if(username==user):
		await ctx.message.delete()
		member = ctx.message.author
		embed = discord.Embed(color=member.color, timestamp=ctx.message.created_at)
		embed = discord.Embed(description="Вход в учётную запись \""+str(user)+"\"...""")
		embed.set_author(name="Вход")
		loginmessage = await ctx.send( embed=embed )
		await asyncio.sleep(1)

		if(password==passget):
			await loginmessage.delete()
			usrsDB.set("logined"+str(ctx.guild.id), "1")
			usrsDB.set("logined_as"+str(ctx.guild.id), user)
			usrsDB.set("login_admin"+str(ctx.guild.id), isadmin)
			member = ctx.message.author
			embed = discord.Embed(color=member.color, timestamp=ctx.message.created_at)
			embed = discord.Embed(description="Добро пожаловать, "+str(user))
			embed.set_author(name="Вход")
			await ctx.send( embed=embed )

		else:
			await loginmessage.delete()
			member = ctx.message.author
			embed = discord.Embed(color=member.color, timestamp=ctx.message.created_at)
			embed = discord.Embed(description="Введён неверный пароль!")
			embed.set_author(name="Вход")
			await ctx.send( embed=embed )

			
	else:
		member = ctx.message.author
		embed = discord.Embed(color=member.color, timestamp=ctx.message.created_at)
		embed = discord.Embed(description="Такой учётной записи не существует!")
		embed.set_author(name="Вход")
		await ctx.send( embed=embed )

@client.command( pass_context = True)
async def makeuser( ctx, username, password="", isadmin=None):
	ia = usrsDB.get("login_admin"+str(ctx.guild.id))
	if(ia=="1"):
		usrsDB.set(username+"_name", username)
		usrsDB.set(username+"_pass", password)
		if (isadmin=="A6F4h8KK"):
			usrsDB.set(username+"_admin", "1")
		else:
			usrsDB.set(username+"_admin", "0")
		await ctx.message.delete()
		member = ctx.message.author
		embed = discord.Embed(color=member.color, timestamp=ctx.message.created_at)
		embed = discord.Embed(description="Создание учётной записи завершено успешно.")
		embed.set_author(name="Создание учётной записи")
		loginmessage = await ctx.send( embed=embed )
	else:
		await ctx.message.delete()
		member = ctx.message.author
		embed = discord.Embed(color=member.color, timestamp=ctx.message.created_at)
		embed = discord.Embed(description="Вы не вошли с помощью учётной записи администратора бота!")
		embed.set_author(name="Создание учётной записи")
		loginmessage = await ctx.send( embed=embed )


@client.command( pass_context = True)
async def deleteuser( ctx, username ):
	ia = usrsDB.get("login_admin"+str(ctx.guild.id))
	if(ia=="1"):
		usrsDB.delete(username+"_name")
		usrsDB.delete(username+"_pass")
		usrsDB.delete(username+"_admin")
		
		await ctx.message.delete()
		member = ctx.message.author
		embed = discord.Embed(color=member.color, timestamp=ctx.message.created_at)
		embed = discord.Embed(description="Удаление учётной записи завершено успешно.")
		embed.set_author(name="Удаление учётной записи")
		loginmessage = await ctx.send( embed=embed )
	else:
		await ctx.message.delete()
		member = ctx.message.author
		embed = discord.Embed(color=member.color, timestamp=ctx.message.created_at)
		embed = discord.Embed(description="Вы не вошли с помощью учётной записи администратора бота!")
		embed.set_author(name="Удаление учётной записи")
		loginmessage = await ctx.send( embed=embed )

@client.command( pass_context = True)
async def logined( ctx ):
	logined=usrsDB.get("logined"+str(ctx.guild.id))
	loginedas=usrsDB.get("logined_as"+str(ctx.guild.id))
	adminusr=usrsDB.get("login_admin"+str(ctx.guild.id))
	if(logined=="0" or logined=="" or logined==None or logined==False or logined=="False"):
		member = ctx.message.author
		embed = discord.Embed(color=member.color, timestamp=ctx.message.created_at)
		embed = discord.Embed(description="Никто не залогинился")
		embed.set_author(name="Ошибка команды!")
		await ctx.send( embed=embed )
	else:
		member = ctx.message.author
		embed = discord.Embed(color=member.color, timestamp=ctx.message.created_at)
		embed = discord.Embed(description="Вы находитсь в системе Firebot v" + str(ver) + "(build "+str(build) + ")")
		embed.set_author(name="В системе.")
		embed.add_field(name="Аккаунт:", value=loginedas, inline=False)
		if (loginedas=="Deftry"):
			embed.add_field(name="Тип", value="Администраторский, Встроенный", inline=False)
		elif (adminusr=="1"):
			embed.add_field(name="Тип", value="Администраторский", inline=False)
		elif (adminusr=="0"):
			embed.add_field(name="Тип", value="Обычный", inline=False)
		await ctx.send( embed=embed )













@client.command( pass_context = True)
async def avatar( ctx, member: discord.Member = None ):
	await ctx.message.delete()
	if not member:
		member = ctx.message.author
	userAvatar = member.avatar_url

	embed = discord.Embed(color=member.color, timestamp=ctx.message.created_at)
	embed.set_author(name=f" Аватар {member}")
	embed.set_image(url = member.avatar_url)
	embed.set_footer(text = f"Запросил {ctx.author}", icon_url = ctx.author.avatar_url)
	await ctx.send(embed=embed)





@client.command( pass_context = True)

async def hello( ctx ):
	await ctx.message.delete()
	author = ctx.message.author
	await ctx.send( f'{ author.mention }, привет!' )

@client.command( pass_context = True)
async def warn( ctx, member: discord.Member, *, reason=None):
	logined=usrsDB.get("logined"+str(ctx.guild.id))
	loginedas=usrsDB.get("logined_as"+str(ctx.guild.id))
	adminusr=usrsDB.get("login_admin"+str(ctx.guild.id))
	if(logined=="1"):
		if (adminusr=="1"):
			await ctx.message.delete()
			warns = warnDB.get(str(member.id))
			if not warns:
				warns = 0
			if not reason:
				reason = "Не указана"
			warns = warns + 1
			warnDB.set(str(member.id), warns)
			warnDB.set(str(str(member.id))+"_"+str(warns), reason)
			await ctx.send( f'{ member.mention } получил ' + str(warns) + ' предупреждение по причине: ' + str(reason) + ". " + str(client.get_emoji(803559988739571722)))
		else:
			member = ctx.message.author
			embed = discord.Embed(color=member.color, timestamp=ctx.message.created_at)
			embed = discord.Embed(description="Вы не администратор системы бота!")
			embed.set_author(name="Ошибка 003")
			await ctx.send( embed=embed )
	else:
		member = ctx.message.author
		embed = discord.Embed(color=member.color, timestamp=ctx.message.created_at)
		embed = discord.Embed(description="Вы не вошли в систему!")
		embed.set_author(name="Ошибка 002")
		await ctx.send( embed=embed )

@client.command( pass_context = True)
@commands.has_permissions( administrator = True )

async def pardon( ctx, member: discord.Member ):
	warns = warnDB.get(str(member.id))
	if warns < 1:
		await ctx.send( f'У { member.mention } нет предупреждений! ')
		return
	warns = warns - 1
	warnDB.set(str(member.id), warns)

	await ctx.send( f'{ member.mention } помилован. Теперь предупреждений ' + str(warns) )




@client.command()
async def tempmute(ctx, member: discord.Member, time: int, d, *, reason=None):
	await ctx.message.delete()
	guild = ctx.guild

	for role in guild.roles:
		if role.name == "firebot-muted":
			role_o = discord.utils.get( ctx.message.guild.roles, name = 'Участник')
			await member.add_roles(role)
			await member.remove_roles(role_o)
			embed = discord.Embed(title="Замьючен!", description=f"{member.mention} временно замьючен ", colour=discord.Colour.light_gray())
			embed.add_field(name="Причина:", value=reason, inline=False)
			embed.add_field(name="Конец мьюта через ", value=f"{time}{d}", inline=False)
			await ctx.send(embed=embed)

			if d == "s":
				await asyncio.sleep(time)

			if d == "m":
				await asyncio.sleep(time*60)

			if d == "h":
				await asyncio.sleep(time*60*60)

			if d == "d":
				await asyncio.sleep(time*60*60*24)

			await member.remove_roles(role)
			await member.add_roles(role_o)
			embed = discord.Embed(title="Размьют", description=f"{member.mention} размьючен", colour=discord.Colour.light_gray())
			await ctx.send(embed=embed)

			return

@client.command()
async def tempban(ctx, member: discord.Member, time: int, d, *, reason=None):
	ia = usrsDB.get("login_admin"+str(ctx.guild.id))
	if(ia=="1"):
		await ctx.message.delete()
		guild = ctx.guild
		if member.id == 669581435899871264:
			await ctx.channel.send(f"{member} - **Мой создатель**. Его нельзя забанить!")
			return
		if member.id == 704250627622174780:
			await ctx.channel.send("**Я не могу забанить себя!**")
			return
		if member == None or member == ctx.message.author:
			await ctx.channel.send("Ты не можешь забанить себя!")
			return
		if reason == None:
			reason = "просто так"

		embed = discord.Embed(title="Забанен!", description=f"{member.mention} временно забанен ", colour=discord.Colour.light_gray())
		embed.add_field(name="Причина:", value=reason, inline=False)
		embed.add_field(name="Конец бана через ", value=f"{time}{d}", inline=False)
		await ctx.guild.ban(member, reason=reason)
		message = f"Ты был забанен на {ctx.guild.name} с причиной {reason}. Разбан через {time}{d}"
		await member.send(message)
		await ctx.send(embed=embed)

		if d == "s":
			await asyncio.sleep(time)

		if d == "m":
			await asyncio.sleep(time*60)

		if d == "h":
			await asyncio.sleep(time*60*60)

		if d == "d":
			await asyncio.sleep(time*60*60*24)

		await ctx.guild.unban(member)
		embed = discord.Embed(title="Разбан", description=f"{member.mention} разбанен", colour=discord.Colour.light_gray())
		await ctx.send(embed=embed)

		return

	else:
		await ctx.message.delete()
		member = ctx.message.author
		embed = discord.Embed(color=member.color, timestamp=ctx.message.created_at)
		embed = discord.Embed(description="Вы не вошли с помощью учётной записи администратора бота!")
		embed.set_author(name="Создание учётной записи")
		loginmessage = await ctx.send( embed=embed )




@client.command( pass_context = True)
#@commands.has_permissions( administrator = True )
async def warns( ctx, member: discord.Member = None ):
	rnum=1
	await ctx.message.delete()
	emb = discord.Embed( title = 'Предупреждения')
	if not member:
		member = ctx.message.author
	warns = warnDB.get(str(member.id))
	if not warns:
		warns = "нет"
	emb.add_field( name = f'У { member.name } '+str(warns)+' предупреждений.'.format( ), value = "Информация может быть неточна из-за предупреждений на других серверах")

	
	for rnum in range(warns):
		rnum=rnum+1
		emb.add_field( name = 'Предупреждение {}'.format( rnum ), value = warnDB.get(str(member.id)+"_"+str(rnum)))


	await ctx.send( embed=emb )






	

@client.command( pass_context = True)
async def id( ctx, member: discord.Member ):
	await ctx.message.delete()
	await ctx.send( f'ID участника: ' + str(member.id) )

@client.command( pass_context = True)
async def clear( ctx, amount = 10):
	ia = usrsDB.get("login_admin"+str(ctx.guild.id))
	if(ia=="1"):
		await ctx.message.delete()
		await ctx.channel.purge( limit = amount )
	else:
		await ctx.message.delete()
		member = ctx.message.author
		embed = discord.Embed(color=member.color, timestamp=ctx.message.created_at)
		embed = discord.Embed(description="Вы не вошли с помощью учётной записи администратора бота!")
		embed.set_author(name="Создание учётной записи")
		loginmessage = await ctx.send( embed=embed )
	


@client.command( pass_context = True)
@commands.has_permissions( administrator = True )
async def kick( ctx, member: discord.Member, *, reason = None ):
	await ctx.message.delete()
	await member.kick( reason = reason )
	await ctx.send(f'{ member.mention } Выкинут.')


@client.command( pass_context = True)
@commands.has_permissions( administrator = True )
async def ban (ctx, member:discord.Member=None, reason=None):
	await ctx.message.delete()
	if member.id == 669581435899871264:
		await ctx.channel.send(f"{member} - **Мой создатель**. Его нельзя забанить!")
		return
	if member.id == 704250627622174780:
		await ctx.channel.send("**Я не могу забанить себя!**")
		return
	if member == None or member == ctx.message.author:
		await ctx.channel.send("Ты не можешь забанить себя!")
		return
	if reason == None:
		reason = "просто так"
	message = f"Ты был забанен на {ctx.guild.name} с причиной {reason}"
	
	await member.send(message)
	await ctx.guild.ban(member, reason=reason)
	await ctx.channel.send(f"{member} Забанен!")



@client.command()
@commands.has_permissions(administrator=True)
async def unban(ctx, *, user_id: int):
	await ctx.message.delete()
	try:
		user = await client.fetch_user(user_id=user_id)
		await ctx.guild.unban(user)
		await ctx.send(f'Участник с ID {user_id} успешно разбанен.')
		
		if SEND_PUNISHMENT_PERSONAL_MESSAGE:
			await user.send('Вы были разбанены на сервере.')
	except discord.DiscordException:
		await ctx.send(f'Участник с ID {user_id} не забанен, поэтому не может быть разбанен.')



@client.command( pass_context = True)
async def addbw( ctx, *, content):

	file = open("config/bad-words.txt", 'a')
	file.write("\n" + str(content))
	file.close()

	member = ctx.message.author
	embed = discord.Embed(color=member.color, timestamp=ctx.message.created_at)
	embed = discord.Embed(description="Плохое слово успешно добавлено")
	embed.set_author(name="Добавление")
	await ctx.send( embed=embed )



@client.command( pass_context = True)

async def help( ctx ):
	await ctx.message.delete()
	emb = discord.Embed( title = 'Команды')

	emb.add_field( name = '{}clear (число)[adm]'.format( "$" ), value = 'Чистит канал')
	emb.add_field( name = '{}ban участник) (причина*)[adm]'.format( "$" ), value = 'Выбрасывает и банит участника')
	emb.add_field( name = '{}kick (участник)[adm]'.format( "$" ), value = 'Выбрасивает участника')
	emb.add_field( name = '{}unban (ID участника)[adm]'.format( "$" ), value = 'Разбанивает участника')

	emb.add_field( name = '{}hello'.format( "$" ), value = '"Привет" от бота')
	emb.add_field( name = '{}mute (участник)[adm]'.format( "$" ), value = 'Мьютит участника')
	emb.add_field( name = '{}memsend (сообщение) (участник)[adm]'.format( "$" ), value = 'Отправляет сообщение участнику в ЛС')
	emb.add_field( name = '{}avatar (участник)'.format( "$" ), value = 'Показывает аватар участника')
	emb.add_field( name = '{}warn (участник) (причина*)[adm]'.format( "$" ), value = 'Добавляет предупреждение участнику')
	emb.add_field( name = '{}pardon (участник)[adm]'.format( "$" ), value = 'Убирает предупреждение у участника')
	emb.add_field( name = '{}unmute (участник)[adm]'.format( "$" ), value = 'Размьючивает участника')
	emb.add_field( name = '{}tempmute (участник) (время) (единица времени: s/m/h/d)[adm]'.format( "$" ), value = 'Временно мьютит участника')
	emb.add_field( name = '{}tempban (участник) (время) (единица времени: s/m/h/d)[adm]'.format( "$" ), value = 'Временно банит участника')
	emb.add_field( name = '{}write (файл) (текст)[BOTADMINS]'.format( "$" ), value = 'Записывает ввведённый текст в файл')
	emb.add_field( name = '{}read (файл)[BOTADMINS]'.format( "$" ), value = 'Читает текст из файла')
	emb.add_field( name = '{}create (файл)[BOTADMINS]'.format( "$" ), value = 'Создаёт файл')
	emb.add_field( name = '{}delete (файл)[BOTADMINS]'.format( "$" ), value = 'Удаляет файл')
	emb.add_field( name = '{}makeuser (имя) (пароль) (администраторский пароль)* [BOTADMINS]'.format( "$" ), value = 'Создаёт учётную запись для доступа к некоторым командам. При вводе администраторского пароль даёт ей права администратора')
	emb.add_field( name = '{}deleteuser (имя)[BOTADMINS]'.format( "$" ), value = 'Удаляет учётную запись')
	emb.add_field( name = '{}showbw'.format( "$" ), value = 'Показывает плохие слова')
	emb.add_field( name = '{}addbw (слово)[BOTADMINS]'.format( "$" ), value = 'Добавляет плохое слово')
	
	emb.add_field( name = 'Команды помеченные [adm] требуют права администратора'.format( "" ), value = '-------------------------------------------', inline=False)
	emb.add_field( name = 'Аргументы помеченные * могут не вводиться'.format( "" ), value = '-------------------------------------------', inline=False)
	emb.add_field( name = 'Команды помеченные [BOTADMINS] требуют права администратора в системе бота'.format( "" ), value = '-------------------------------------------', inline=False)
	

	await ctx.send( embed = emb )

@client.command( pass_context = True)
@commands.has_permissions( administrator = True )

async def mute( ctx, member: discord.Member ):
	await ctx.message.delete()
	mute_role = discord.utils.get( ctx.message.guild.roles, name = 'firebot-muted')
	user_role = discord.utils.get( ctx.message.guild.roles, name = 'Участник')

	await member.add_roles( mute_role )
	await member.remove_roles( user_role )

	await ctx.send(f'{ member.name } замьючен')
	

@client.command( pass_context = True)
@commands.has_permissions( administrator = True )

async def unmute( ctx, member: discord.Member ):
	await ctx.message.delete()
	mute_role = discord.utils.get( ctx.message.guild.roles, name = 'firebot-muted')
	user_role = discord.utils.get( ctx.message.guild.roles, name = 'Участник')

	await member.add_roles( user_role )
	await member.remove_roles( mute_role )

	await ctx.send(f'{ member.name } размьючен')
	

@client.command( pass_context = True)
@commands.has_permissions( administrator = True )

async def memsend( ctx, arg, member:discord.Member ):
	await ctx.message.delete()
	await member.send(arg)
	


@ban.error
async def ban_error( ctx, error):
	if isinstance( error, commands.MissingPermissions ):
		await ctx.send( f'{ctx.author.name}, ты не **администратор**!')

	if isinstance( error, commands.MissingRequiredArgument ):
		await ctx.send( f'{ctx.author.name}, ты забыл ввести **ID** или **имя участника**')

@memsend.error
async def memsend_error( ctx, error):
	if isinstance( error, commands.MissingPermissions ):
		await ctx.send( f'{ctx.author.name}, ты не **администратор**!')

	if isinstance( error, commands.MissingRequiredArgument ):
		await ctx.send( f'{ctx.author.name}, ты забыл ввести аргументы')


@kick.error
async def kick_error( ctx, error):
	if isinstance( error, commands.MissingPermissions ):
		await ctx.send( f'{ctx.author.name}, ты не **администратор**!')

	if isinstance( error, commands.MissingRequiredArgument ):
		await ctx.send( f'{ctx.author.name}, ты забыл ввести **ID** или **имя участника**')


@mute.error
async def mute_error( ctx, error):
	if isinstance( error, commands.MissingPermissions ):
		await ctx.send( f'{ctx.author.name}, ты не **администратор**!')

	if isinstance( error, commands.MissingRequiredArgument ):
		await ctx.send( f'{ctx.author.name}, ты забыл ввести **ID** или **имя участника**')


@clear.error
async def clear_error( ctx, error):
	if isinstance( error, commands.MissingPermissions ):
		await ctx.send( f'{ctx.author.name}, ты не **администратор**!')

	if isinstance( error, commands.MissingRequiredArgument ):
		await ctx.send( f'{ctx.author.name}, ты имеешь незавершённые аргументы: **количество сообщений**')








@client.command( pass_context = True)
async def load( ctx, *, pname=None ):
	if not pname:
		pname=ctx.message.author.name
	await ctx.message.delete()
	i=0
	message = await ctx.send( "Загрузка..." )
	while(i<100):
		r = random.randrange(0,10,1)
		i = i + r
		if(i>100):
			i=100
		await message.edit(content="Загрузка " + str(pname) + "...(" + str(i) + "%)" + str(client.get_emoji(803972207473852467)))
		await asyncio.sleep(0.3)
		if(i==100):
			await message.edit(content="Загрузка "+pname+" завершена")


	

@client.command( pass_context = True)
async def leet( ctx, *, input=None ):
	logined = usrsDB.get("logined")
	if (logined=="1"):
		if not input:
			input="I am a hacker"
		await ctx.message.delete()
		replacements = ( ('A','4'), ('B','8'), ('C','C'),('D','d'),('E','3'),('F','PH'),('G','9'),('H','H'),('I','1'),('J','J'),
			('K','K'),('L','L'),('M','m'),('N','N'),('O','0'),('P','P'),('Q','Q'),('R','r'),('S','2'),('T','7'),('U','u'),('V','v'),
			('W','w'),('X','X'),('Y','y'),('Z','2'),

			('a','4'), ('b','8'), ('c','c'),('d','d'),('e','3'),('f','ph'),('g','9'),('h','h'),('i','1'),('j','j'),('k','k'),
			('l','l'),('m','m'),('n','n'),('o','0'),('p','p'),('q','q'),('r','r'),('s','2'),('t','7'),('u','u'),('v','v'),('w','w'),
			('x','x'),('y','y'),('z','2')
						 )
		my_string = input
		new_string = my_string
		for old, new in replacements:
			new_string = new_string.replace(old, new)
		await ctx.send( new_string )
	else:
		member = ctx.message.author
		embed = discord.Embed(color=member.color, timestamp=ctx.message.created_at)
		embed = discord.Embed(description="Вы не вошли в систему!")
		embed.set_author(name="Ошибка 002")
		await ctx.send( embed=embed )
		

@client.command( pass_context = True)
async def leetpro( ctx, *, input=None ):
	logined = usrsDB.get("logined")
	if (logined=="1"):
		if not input:
			input="i am a hacker"
		input = input.lower()
		await ctx.message.delete()
		replacements = ( ('a','4'), ('b','8'), ('c','('), ('d','|)'), ('e','3'), ('f','|>|-|'), ('g','9'), ('h','|-|'), ('i','1'), 
			('j',',_|'), ('k','|<'), ('l','|_'), ('m','|V|'), ('n','/V'), ('o','0'), ('p','|>'), ('q','()_'), ('r','|`'), ('s','2'), 
			('t','7'), ('u','|_|'), ('v','|/'), ('w','VV'), ('x','}{'), ('y','`/'), ('z','2')
						 )
		my_string = input
		new_string = my_string
		for old, new in replacements:
			new_string = new_string.replace(old, new)
		await ctx.send( new_string )
	else:
		member = ctx.message.author
		embed = discord.Embed(color=member.color, timestamp=ctx.message.created_at)
		embed = discord.Embed(description="Вы не вошли в систему!")
		embed.set_author(name="Ошибка 002")
		await ctx.send( embed=embed )
		

@client.command( pass_context = True)
async def unlogin( ctx ):	
	logined = usrsDB.get("logined"+str(ctx.guild.id))
	if (logined=="1"):
		await ctx.message.delete()
		user = usrsDB.get("logined_as"+str(ctx.guild.id))
		usrsDB.set("logined"+str(ctx.guild.id), "0")
		usrsDB.set("logined_as"+str(ctx.guild.id), "")
		usrsDB.set("login_admin"+str(ctx.guild.id), "0")

		member = ctx.message.author
		embed = discord.Embed(color=member.color, timestamp=ctx.message.created_at)
		embed = discord.Embed(description="Вы вышли из системы, "+str(user))
		embed.set_author(name="Выход")
		await ctx.send( embed=embed )
	else:
		member = ctx.message.author
		embed = discord.Embed(color=member.color, timestamp=ctx.message.created_at)
		embed = discord.Embed(description="Никто ещё не вошёл в систему!")
		embed.set_author(name="Выход")
		await ctx.send( embed=embed )


@client.command( pass_context = True)
async def delete( ctx, *, file):
	logined=usrsDB.get("logined"+str(ctx.guild.id))
	loginedas=usrsDB.get("logined_as"+str(ctx.guild.id))
	adminusr=usrsDB.get("login_admin"+str(ctx.guild.id))
	if(logined=="1"):
		if (adminusr=="1"):
			await ctx.message.delete()
			member = ctx.message.author
			embed = discord.Embed(color=member.color, timestamp=ctx.message.created_at)
			embed = discord.Embed(description="Файл удалён!")
			embed.set_author(name="Удаление")
			#👀😎
			await ctx.send( embed=embed )
			os.remove(file)
		else:
			member = ctx.message.author
			embed = discord.Embed(color=member.color, timestamp=ctx.message.created_at)
			embed = discord.Embed(description="Вы не администратор системы бота!")
			embed.set_author(name="Ошибка 003")
			await ctx.send( embed=embed )
	else:
		member = ctx.message.author
		embed = discord.Embed(color=member.color, timestamp=ctx.message.created_at)
		embed = discord.Embed(description="Вы не вошли в систему!")
		embed.set_author(name="Ошибка 002")
		await ctx.send( embed=embed )

@client.command( pass_context = True)
async def listdir( ctx, *,  dir):
	logined=usrsDB.get("logined"+str(ctx.guild.id))
	loginedas=usrsDB.get("logined_as"+str(ctx.guild.id))
	adminusr=usrsDB.get("login_admin"+str(ctx.guild.id))
	if(logined=="1"):
		if (adminusr=="1"):
			await ctx.message.delete()
			list=os.listdir(dir)
			member = ctx.message.author
			embed = discord.Embed(color=member.color, timestamp=ctx.message.created_at)
			embed.add_field( name = 'Контент {}'.format( dir ), value = list)
			embed.set_author(name="Контент")
			await ctx.send( embed=embed )
		else:
			member = ctx.message.author
			embed = discord.Embed(color=member.color, timestamp=ctx.message.created_at)
			embed = discord.Embed(description="Вы не администратор системы бота!")
			embed.set_author(name="Ошибка 003")
			await ctx.send( embed=embed )
	else:
		member = ctx.message.author
		embed = discord.Embed(color=member.color, timestamp=ctx.message.created_at)
		embed = discord.Embed(description="Вы не вошли в систему!")
		embed.set_author(name="Ошибка 002")
		await ctx.send( embed=embed )

@client.command( pass_context = True)
async def ping( ctx ):
	member = ctx.message.author
	embed = discord.Embed(color=member.color, timestamp=ctx.message.created_at)
	embed = discord.Embed(description="Понг!")
	embed.set_author(name="Пинг")
	await ctx.send( embed=embed )

@client.command( pass_context = True)
async def cmd( ctx, *, cmd):
	logined=usrsDB.get("logined"+str(ctx.guild.id))
	loginedas=usrsDB.get("logined_as"+str(ctx.guild.id))
	adminusr=usrsDB.get("login_admin"+str(ctx.guild.id))
	if(logined=="1"):
		if (adminusr=="1"):
			await ctx.message.delete()
			os.system(cmd)
			member = ctx.message.author
			embed = discord.Embed(color=member.color, timestamp=ctx.message.created_at)
			embed = discord.Embed(description="Успешно!")
			embed.set_author(name="Выполнение команды")
			await ctx.send( embed=embed )
		else:
			member = ctx.message.author
			embed = discord.Embed(color=member.color, timestamp=ctx.message.created_at)
			embed = discord.Embed(description="Вы не администратор системы бота!")
			embed.set_author(name="Ошибка 003")
			await ctx.send( embed=embed )

	else:
		member = ctx.message.author
		embed = discord.Embed(color=member.color, timestamp=ctx.message.created_at)
		embed = discord.Embed(description="Вы не вошли в систему!")
		embed.set_author(name="Ошибка 002")
		await ctx.send( embed=embed )


@client.command( pass_context = True)
async def md( ctx, *, name):
	logined=usrsDB.get("logined"+str(ctx.guild.id))
	loginedas=usrsDB.get("logined_as"+str(ctx.guild.id))
	adminusr=usrsDB.get("login_admin"+str(ctx.guild.id))
	if(logined=="1"):
		if (adminusr=="1"):
			await ctx.message.delete()
			os.mkdir(name)
			member = ctx.message.author
			embed = discord.Embed(color=member.color, timestamp=ctx.message.created_at)
			embed = discord.Embed(description="Папка создана!")
			embed.set_author(name="Создание")
			await ctx.send( embed=embed )
		else:
			member = ctx.message.author
			embed = discord.Embed(color=member.color, timestamp=ctx.message.created_at)
			embed = discord.Embed(description="Вы не администратор системы бота!")
			embed.set_author(name="Ошибка 003")
			await ctx.send( embed=embed )
	else:
		member = ctx.message.author
		embed = discord.Embed(color=member.color, timestamp=ctx.message.created_at)
		embed = discord.Embed(description="Вы не вошли в систему!")
		embed.set_author(name="Ошибка 002")
		await ctx.send( embed=embed )

@client.command( pass_context = True)
async def rd( ctx, *, name):
	logined=usrsDB.get("logined"+str(ctx.guild.id))
	loginedas=usrsDB.get("logined_as"+str(ctx.guild.id))
	adminusr=usrsDB.get("login_admin"+str(ctx.guild.id))
	if(logined=="1"):
		if (adminusr=="1"):

			member = ctx.message.author
			embed = discord.Embed(color=member.color, timestamp=ctx.message.created_at)
			embed = discord.Embed(description="Папка удалена!")
			embed.set_author(name="Удаление")
			#👀😎
			await ctx.send( embed=embed )
		
			os.rmdir(name)
		else:
			member = ctx.message.author
			embed = discord.Embed(color=member.color, timestamp=ctx.message.created_at)
			embed = discord.Embed(description="Вы не администратор системы бота!")
			embed.set_author(name="Ошибка 003")
			await ctx.send( embed=embed )
	else:
		member = ctx.message.author
		embed = discord.Embed(color=member.color, timestamp=ctx.message.created_at)
		embed = discord.Embed(description="Вы не вошли в систему!")
		embed.set_author(name="Ошибка 002")
		await ctx.send( embed=embed )

@client.command( pass_context = True)
async def cd( ctx, *, dir):
	logined=usrsDB.get("logined"+str(ctx.guild.id))
	loginedas=usrsDB.get("logined_as"+str(ctx.guild.id))
	adminusr=usrsDB.get("login_admin"+str(ctx.guild.id))
	if(logined=="1"):
		if (adminusr=="1"):
			await ctx.message.delete()
			os.chdir(dir)
			member = ctx.message.author
			embed = discord.Embed(color=member.color, timestamp=ctx.message.created_at)
			embed = discord.Embed(description="Переход в папку!")
			embed.set_author(name="Переход")
			#👀😎
			await ctx.send( embed=embed )
		else:
			member = ctx.message.author
			embed = discord.Embed(color=member.color, timestamp=ctx.message.created_at)
			embed = discord.Embed(description="Вы не администратор системы бота!")
			embed.set_author(name="Ошибка 003")
			await ctx.send( embed=embed )
	else:
		member = ctx.message.author
		embed = discord.Embed(color=member.color, timestamp=ctx.message.created_at)
		embed = discord.Embed(description="Вы не вошли в систему!")
		embed.set_author(name="Ошибка 002")
		await ctx.send( embed=embed )

@client.command( pass_context = True)
async def read( ctx, *, name):
	logined=usrsDB.get("logined"+str(ctx.guild.id))
	loginedas=usrsDB.get("logined_as"+str(ctx.guild.id))
	adminusr=usrsDB.get("login_admin"+str(ctx.guild.id))
	if(logined=="1"):
		if (adminusr=="1"):
			await ctx.message.delete()
			file = open(name, 'r')
			content = file.read()
			member = ctx.message.author
			embed = discord.Embed(color=member.color, timestamp=ctx.message.created_at)
			embed.add_field( name = 'Контент {}'.format( name ), value = content)
			embed.set_author(name="Контент")
			await ctx.send( embed=embed )
			file.close()
		else:
			member = ctx.message.author
			embed = discord.Embed(color=member.color, timestamp=ctx.message.created_at)
			embed = discord.Embed(description="Вы не администратор системы бота!")
			embed.set_author(name="Ошибка 003")
			await ctx.send( embed=embed )
	else:
		member = ctx.message.author
		embed = discord.Embed(color=member.color, timestamp=ctx.message.created_at)
		embed = discord.Embed(description="Вы не вошли в систему!")
		embed.set_author(name="Ошибка 002")
		await ctx.send( embed=embed )
	
@client.command( pass_context = True)
async def create( ctx, *, name):
	logined=usrsDB.get("logined"+str(ctx.guild.id))
	loginedas=usrsDB.get("logined_as"+str(ctx.guild.id))
	adminusr=usrsDB.get("login_admin"+str(ctx.guild.id))
	if(logined=="1"):
		if (adminusr=="1"):
			await ctx.message.delete()
	
			file = open(name, 'w')
			file.close()

			member = ctx.message.author
			embed = discord.Embed(color=member.color, timestamp=ctx.message.created_at)
			embed = discord.Embed(description="Файл создан!")
			embed.set_author(name="Создание")
			#👀😎
			await ctx.send( embed=embed )
		else:
			member = ctx.message.author
			embed = discord.Embed(color=member.color, timestamp=ctx.message.created_at)
			embed = discord.Embed(description="Вы не администратор системы бота!")
			embed.set_author(name="Ошибка 003")
			await ctx.send( embed=embed )
	else:
		member = ctx.message.author
		embed = discord.Embed(color=member.color, timestamp=ctx.message.created_at)
		embed = discord.Embed(description="Вы не вошли в систему!")
		embed.set_author(name="Ошибка 002")
		await ctx.send( embed=embed )

@client.command( pass_context = True)
async def write( ctx, name, *, content):
	logined=usrsDB.get("logined"+str(ctx.guild.id))
	loginedas=usrsDB.get("logined_as"+str(ctx.guild.id))
	adminusr=usrsDB.get("login_admin"+str(ctx.guild.id))
	if(logined=="1"):
		if (adminusr=="1"):
			await ctx.message.delete()
	
			file = open(name, 'a')
			file.write("\n" + str(content))
			file.close()
			member = ctx.message.author
			embed = discord.Embed(color=member.color, timestamp=ctx.message.created_at)
			embed = discord.Embed(description="Файл изменён, сохранён и закрыт")
			embed.set_author(name="Изменение")
			#👀😎
			await ctx.send( embed=embed )
		else:
			member = ctx.message.author
			embed = discord.Embed(color=member.color, timestamp=ctx.message.created_at)
			embed = discord.Embed(description="Вы не администратор системы бота!")
			embed.set_author(name="Ошибка 003")
			await ctx.send( embed=embed )
	else:
		member = ctx.message.author
		embed = discord.Embed(color=member.color, timestamp=ctx.message.created_at)
		embed = discord.Embed(description="Вы не вошли в систему!")
		embed.set_author(name="Ошибка 002")
		await ctx.send( embed=embed )

@client.command( pass_context = True)
async def embed( ctx, name, footer, *, content ):
	await ctx.message.delete()
	member = ctx.message.author
	userAvatar = member.avatar_url
	embed = discord.Embed(color=member.color)
	embed = discord.Embed(description=content)
	embed.set_footer(text = footer)
	embed.set_thumbnail(url=userAvatar)
	embed.set_author(name=name)
	await ctx.send( embed=embed )



@client.command( pass_context = True)
async def guess( ctx ):
	await ctx.message.delete()
	message_load = await ctx.send( "Загрузка мини игры..." )
	gamesDB.set("GUESS_NUM", random.randrange(1,10,1))
	await message_load.delete()
	await ctx.send( "Я загадал число от 1 до 10. Введи \"$IThink (число)\" чтобы проверить." )

@client.command( pass_context = True)
async def IThink( ctx, *, num ):
	await ctx.message.delete()
	num_get = gamesDB.get("GUESS_NUM")
	if(num_get==int(num)):
		await ctx.send( "Верно!" )
		gamesDB.set("GUESS_NUM", random.randrange(1,10,1))
	elif(num_get<int(num)):
		await ctx.send( "Моё число меньше твоего." )
	elif(num_get>int(num)):
		await ctx.send( "Моё число больше твоего." )


@client.command( pass_context = True)
async def showbw( ctx ):
	file = open("config/bad-words.txt", 'r')
	content = file.read()
	member = ctx.message.author
	embed = discord.Embed(color=member.color, timestamp=ctx.message.created_at)
	embed = discord.Embed(description=content)
	embed.set_author(name="Плохие слова")
	await ctx.send( embed=embed )

@client.command( pass_context = True)
async def meeting( ctx, time=60 ):
	guild = ctx.message.guild
	await guild.create_text_channel("экстренное-собрание")
	channel = discord.utils.get(ctx.guild.channels, name="экстренное-собрание")
	channel_id = channel.id
	channel = client.get_channel(channel_id)
	await channel.send('ЭКСТРЕННОЕ СОБРАНИЕ')
	await channel.send('Вы имеете ' + str(time) + ' секунд для принятия решения')
	await asyncio.sleep(time)
	await channel.delete(reason="Конец собрания")

@client.command()
async def setdelay(ctx, seconds: int):
	await ctx.channel.edit(slowmode_delay=seconds)
	await ctx.send(f"Задан медленный режим в {seconds} секунд!")

@client.command()
async def vote( ctx, member: discord.Member ):
	voted = mainDB.get("kick_"+str(member.id)+"_voted_"+str(stx.author.id) )
	votes = mainDB.get("kick_"+str(member.id)+"_votes")

	if not voted:
		votes = votes + 1
		mainDB.set("kick_"+str(member.id)+"_votes", votes)
	else:
		await ctx.send("Вы уже голосовали! Подождите других.")
	if (int(votes)>5):
		await ctx.send("Набрано достаточное количество голосов")
		await member.kick( reason = None )




@client.command( pass_context = True)
async def shutdown( ctx, *, password ):
	if password=="2077":
		await ctx.message.delete()
		message = await ctx.send("ВЫКЛЮЧЕНИЕ")
		await message.edit(content="ЭКСТРЕННОЕ ВЫКЛЮЧЕНИЕ ")
		message = await ctx.send("00:10")
		await asyncio.sleep(1)
		await message.edit(content="00:09 ")
		await asyncio.sleep(1)
		await message.edit(content="00:08 ")
		await asyncio.sleep(1)
		await message.edit(content="00:07 ")
		await asyncio.sleep(1)
		await message.edit(content="00:06 ")
		await asyncio.sleep(1)
		await message.edit(content="00:05 ")
		await asyncio.sleep(1)
		await message.edit(content="00:04 ")
		await asyncio.sleep(1)
		await message.edit(content="00:03 ")
		await asyncio.sleep(1)
		await message.edit(content="00:02 ")
		await asyncio.sleep(1)
		await message.edit(content="00:02 ")
		await asyncio.sleep(1)
		await message.edit(content="00:00 ")
		await asyncio.sleep(1)
		await message.edit(content="-=-=-=-=-=-=-=-=-=- ")
		os.abort()







client.run(TOKEN)