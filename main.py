import json
import os
import discord
from discord.ext import commands
import random
import sys
import asyncio


intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True  # kick/ban

bot = commands.Bot(command_prefix="!", intents=intents)

# Canal de log
LOG_CHANNEL_ID = 1380182279166361732
log_fila = []
log_canal = None

# Funções warns qC7sp8qY4q
def carregar_warns():
    try:
        with open("warns.json", "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def salvar_warns():
    with open("warns.json", "w") as f:
        json.dump(warns, f, indent=4)

warns = carregar_warns()

# print
class LogRedirector:
    def __init__(self, original):
        self.original = original

    def write(self, message):
        self.original.write(message)
        if message.strip():
            log_fila.append(message.strip())

    def flush(self):
        self.original.flush()

sys.stdout = LogRedirector(sys.stdout)

async def enviar_logs_automaticamente():
    while True:
        if log_fila and log_canal:
            mensagem = log_fila.pop(0)
            try:
                await log_canal.send(f"🔨 {mensagem}")
            except Exception:
                pass
        await asyncio.sleep(1)

ajuda_comandos = {
    "utilitarios": {
        "!ajuda": "Exibe esta mensagem",
        "!entrar": "Entra no canal de voz",
        "!sair": "Sai do canal de voz",
        "!userinfo": "Neofetch do usuario",
        "!serverinfo": "Neofetch do servidor",
    },
    "moderacao": {
        "!ban": "Bane um usuário. Uso: !ban @usuario [motivo]",
        "!kick": "Expulsa um usuário. Uso: !kick @usuario [motivo]",
        "!warn": "Avisa um usuário. Uso: !warn @usuario [motivo]",
    "!verwarns": "Veja avisos do usuário. Uso: !verwarns [@usuario]",
 "!removerwarn": "Remove um aviso. Uso: !removewarn @usuario <número>",
        
    },
    "diversao": {
        "!piada": "Conta uma piada",
        "!roleta": "Joga roleta russa (com tambor cheio)",
        "!ascii": "Faz arte ascii, Exemplo: !ascii <texto> <fonte>",
        "!fontesascii": "Lista fontes disponíveis para o !ascii. Uso: !fontesascii [página]",

    }
}

@bot.command()
async def ajuda(ctx, categoria: str = None):
    if categoria is None:
        categorias = ", ".join(ajuda_comandos.keys())
        texto = f"""
[1;35mDiscordOS Help Terminal[0m
---------------------------
[1;36mCategorias disponíveis:[0m {categorias}

Use o comando:
[1;32m!ajuda <categoria>[0m para ver os comandos específicos.
"""
        await ctx.send(f"```ansi\n{texto}\n```")
    else:
        categoria = categoria.lower()
        if categoria in ajuda_comandos:
            texto = f"[1;35mAjuda: {categoria.capitalize()}[0m\n---------------------------\n"
            for cmd, desc in ajuda_comandos[categoria].items():
                texto += f"[1;32m{cmd:12}[0m - {desc}\n"
            await ctx.send(f"```ansi\n{texto}```")
        else:
            await ctx.send("Categoria inválida.")

@bot.command()
async def entrar(ctx):
    if ctx.author.voice:
        canal = ctx.author.voice.channel
        if ctx.voice_client is None:
            await canal.connect()
            await ctx.send(f"✅ Entrei no canal: {canal.name}")
            print(f"{ctx.author} me conectou ao canal de voz {canal.name}")
        else:
            await ctx.send("⚠️ Já estou em um canal de voz.")
    else:
        await ctx.send("❗ Você precisa estar em um canal de voz.")

@bot.command()
async def sair(ctx):
    if ctx.voice_client:
        canal = ctx.voice_client.channel.name
        await ctx.voice_client.disconnect()
        await ctx.send("✅ Saí do canal de voz.")
        print(f"{ctx.author} me desconectou do canal de voz {canal}")
    else:
        await ctx.send("⚠️ Não estou em nenhum canal de voz.")

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, motivo=None):
    motivo = motivo or "Não especificado"
    if not ctx.guild.me.guild_permissions.ban_members:
        return await ctx.send("❌ Eu não tenho permissão para banir membros.")
    try:
        await member.ban(reason=motivo)
        await ctx.send(f"🚫 {member} foi banido, Motivo: {motivo}")
        print(f"{ctx.author} baniu {member} (Motivo: {motivo})")
    except Exception as e:
        await ctx.send(f"❌ Não foi possível banir {member}. Erro: {e}")
        print(f"Erro ao banir: {e}")

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, motivo=None):
    motivo = motivo or "Não especificado"
    if not ctx.guild.me.guild_permissions.kick_members:
        return await ctx.send("❌ Eu não tenho permissão para expulsar membros.")
    try:
        await member.kick(reason=motivo)
        await ctx.send(f"👢 {member} foi expulso, Motivo: {motivo}")
        print(f"{ctx.author} expulsou {member} (Motivo: {motivo})")
    except Exception as e:
        await ctx.send(f"❌ Não foi possível expulsar {member}. Erro: {e}")
        print(f"Erro ao expulsar: {e}")

# --------- COMANDOS DE WARN ---------

@bot.command()
@commands.has_permissions(kick_members=True)
async def warn(ctx, member: discord.Member, *, motivo=None):
    motivo = motivo or "Não especificado"
    if member == ctx.author:
        return await ctx.send("❌ Você não pode se avisar.")
    if member.bot:
        return await ctx.send("🤖 Não posso avisar bots.")

    warns.setdefault(str(member.id), []).append({
        "autor_id": str(ctx.author.id),
        "motivo": motivo
    })
    salvar_warns()

    await ctx.send(f"🔨​ {member.mention} foi avisado. Motivo: {motivo}")
    print(f"{ctx.author} avisou {member} (Motivo: {motivo})")

@bot.command()
async def verwarns(ctx, member: discord.Member = None):
    member = member or ctx.author
    lista = warns.get(str(member.id), [])

    if not lista:
        return await ctx.send(f"```ansi\n[1;32m✓ {member.display_name} não tem avisos registrados.\n```")

    header = f"""
[1;35m{member.display_name}@DiscordOS[0m
------------------------------
[1;36mSistema de Logs de Moderação
[1;90mData......: [0m{discord.utils.format_dt(discord.utils.utcnow(), 'F')}
[1;90mTotal.....: [0m{len(lista)} aviso(s)
"""
    corpo = ""
    for i, warn in enumerate(lista, 1):
        autor_id = int(warn["autor_id"])
        motivo = warn["motivo"]
        autor = ctx.guild.get_member(autor_id)
        autor_nome = autor.display_name if autor else "Desconhecido"
        corpo += f"\n[1;33m[{i}] [0m[1;34mAutor:[0m {autor_nome} [1;34m| Motivo:[0m {motivo}"

    await ctx.send(f"```ansi\n{header}{corpo}\n```")


@bot.command()
@commands.has_permissions(kick_members=True)
async def removerwarn(ctx, member: discord.Member, index: int):
    id_str = str(member.id)
    lista = warns.get(id_str, [])

    if not lista:
        return await ctx.send(f"✅ {member.mention} não tem avisos.")

    if index < 1 or index > len(lista):
        return await ctx.send(f"❌ Índice inválido. Use um número entre 1 e {len(lista)}.")

    removido = lista.pop(index - 1)
    salvar_warns()

    autor_id = int(removido["autor_id"])
    autor = ctx.guild.get_member(autor_id)
    autor_nome = autor.display_name if autor else "Desconhecido"

    await ctx.send(f"🔨​ Aviso {index} removido de {member.mention}. Era de {autor_nome}, motivo: {removido['motivo']}")
    print(f"{ctx.author} removeu um warn de {member}")

# -------------------------------------

piadas = [
    "O maior erro do programador é programar. (real)",
    "O meu maior erro foi ter criado esse bot. (real)",
    "Por que o Dev não atravessou a rua? Porque ele ficou preso em um loop."
]

@bot.command()
async def piada(ctx):
    p = random.choice(piadas)
    await ctx.send(f"😂 {p}")
    print(f"{ctx.author} usou !piada")

@bot.command()
async def roleta(ctx):
    resultado = random.randint(1, 6)
    if resultado == 1:
        await ctx.send("💥 PIU! tu morreu")
        print(f"{ctx.author} morreu na roleta")
    else:
        await ctx.send(f"✅ Você sobreviveu! (tirou {resultado})")
        print(f"{ctx.author} sobreviveu na roleta (tirou {resultado})")

@bot.command()
async def userinfo(ctx, membro: discord.Member = None):
    if not ctx.guild:
        return await ctx.send("❌ Este comando só funciona em servidores.")

    membro = membro or ctx.author
    nome = str(membro)
    apelido = membro.nick if membro.nick else "Nenhum"
    id_usuario = membro.id
    status = str(membro.status).capitalize()
    cargos = ', '.join([c.name for c in membro.roles if c.name != "@everyone"]) or "Nenhum"
    bot_simbolo = "✅" if membro.bot else "❌"

    ascii_tux = r"""
       [1;30m.--.
     |o_o |
     |:_/ |
    //   \ \
   (|     | )
  /'\_   _/\
  \___)=(___/
    """

    neofetch_output = f"""
```ansi
{ascii_tux}

[1;35m{nome}@DiscordOS[0m
------------------------------
[1;36mSistema......: [0;37mDiscordOS 7.8.9 (Stable)
[1;36mHost.........: [0;37m{ctx.guild.name}
[1;36mKernel.......: [0;37mAPI v10 - Gateway Intent
[1;36mPacotes......: [0;37mAtp S/A bot
[1;36mShell........: [0;37mDiscord.py {discord.__version__}
[1;36mTerminal.....: [0;37m#{ctx.channel.name}
[1;36mCargos.......: [0;37m{cargos}
[1;36mID...........: [0;37m{id_usuario}
[1;36mApelido......: [0;37m{apelido}
[1;36mStatus.......: [0;37m{status}
[1;36mBot..........: [0;37m{bot_simbolo}
```"""

    await ctx.send(neofetch_output)
    print(f"{ctx.author} usou !userinfo em {membro}")

@bot.command()
async def serverinfo(ctx):
    guild = ctx.guild
    dono = guild.owner
    membros = guild.member_count
    canais_texto = len(guild.text_channels)
    canais_voz = len(guild.voice_channels)
    total_canais = canais_texto + canais_voz
    cargos = len(guild.roles) - 1  # tirando @everyone
    criado_em = guild.created_at.strftime("%d/%m/%Y %H:%M:%S")

    info = f"""
[1;35m{guild.name}@DiscordOS[0m
-------------------------------
[1;36mSistema.......:[0m DiscordOS Server v1.0
[1;36mID do servidor:[0m {guild.id}
[1;36mDono..........:[0m {dono}
[1;36mCriado em.....:[0m {criado_em}
[1;36mMembros.......:[0m {membros}
[1;36mCanais........:[0m {total_canais} (💬 {canais_texto} texto | 🔊 {canais_voz} voz)
[1;36mCargos........:[0m {cargos}
[1;36mRegião........:[0m {guild.preferred_locale}
    """

    await ctx.send(f"```ansi\n{info}```")
    print(f"{ctx.author} usou !serverinfo em {guild.name}")

@bot.command()
async def fontesascii(ctx, pagina: int = 1): # fontes ascii
    fontes = sorted(Figlet().getFonts())
    por_pagina = 10
    total_paginas = (len(fontes) + por_pagina - 1) // por_pagina

    if pagina < 1 or pagina > total_paginas:
        return await ctx.send(f"❌ Página inválida. Use um número entre 1 e {total_paginas}.")

    inicio = (pagina - 1) * por_pagina
    fim = inicio + por_pagina
    lista_pagina = fontes[inicio:fim]

    texto = f"""
[1;35mFontes ASCII Art — Página {pagina}/{total_paginas}[0m
------------------------------
""" + '\n'.join(f"[1;36m-[0m {fonte}" for fonte in lista_pagina)

    await ctx.send(f"```ansi\n{texto}```")
    print(f"{ctx.author} usou !fontesascii (página {pagina})")

@bot.command()
async def ping(ctx):
    latency = bot.latency * 1000  # em ms
    await ctx.send(f"Seu pulso cortado! ping: {latency:.2f}ms")
    print(f"{ctx.author} usou !ping")

    @bot.event
    async def on_message(message):
        if message.author == bot.user:
            return

        # Verifica se a mensagem é exatamente "running with scissors" (sem case sensitivity)
        if message.content.strip().lower() == "running with scissors":
            await message.channel.send("Cutting Wrists")
            print(f"{message.author} ativou o easter egg")
            return  # evita processar como comando depois

        # Garante que outros comandos ainda funcionem
        await bot.process_commands(message)

from pyfiglet import Figlet

@bot.command()
async def ascii(ctx, *, args=None): #ascii
    if not args:
        return await ctx.send("❌ Uso: `!ascii <texto> [fonte]`")

    # Separar texto e (possível) fonte
    partes = args.rsplit(" ", 1)
    texto = partes[0]
    fonte = partes[1] if len(partes) > 1 and partes[1] in Figlet().getFonts() else "slant"

    try:
        f = Figlet(font=fonte)
        resultado = f.renderText(texto)
        # Enviar como bloco de código
        await ctx.send(f"```ansi\n[1;36m{resultado}```")
        print(f"{ctx.author} usou !ascii com fonte '{fonte}': {texto}")
    except Exception as e:
        fontes_disponiveis = ", ".join(random.sample(Figlet().getFonts(), 5))  # mostra 5 fontes aleatórias
        await ctx.send(f"❌ Fonte inválida. Exemplos disponíveis: `{fontes_disponiveis}`")
        print(f"Erro no !ascii: {e}")


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if bot.user in message.mentions:
        categorias = ", ".join(ajuda_comandos.keys())
        texto = f"""


        
[1;35mDiscordOS Help Terminal[0m
---------------------------
[1;36mCategorias disponíveis:[0m {categorias}

Use o comando:
[1;32m!ajuda <categoria>[0m para ver os comandos específicos.
"""
        await message.channel.send(f"```ansi\n{texto}\n```")
        print(f"{message.author} mencionou o bot no canal {message.channel}")

    await bot.process_commands(message)

@bot.event
async def on_ready():
    global log_canal
    try:
        log_canal = await bot.fetch_channel(LOG_CHANNEL_ID)
    except Exception as e:
        print(f"Erro ao obter canal de log: {e}")
    print(f"✅ Bot online como {bot.user}")
    asyncio.create_task(enviar_logs_automaticamente())

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
if not TOKEN:
    print("❌ Token não encontrado! Configure DISCORD_BOT_TOKEN nas Secrets.")
    exit(1)

try:
    from keep_alive import manter_online
    manter_online()
except ImportError:
    print("ℹ️ Modo local: keep_alive não encontrado.")


bot.run(TOKEN)
