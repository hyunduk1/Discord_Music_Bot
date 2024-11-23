import discord
import os
import asyncio
import yt_dlp
from dotenv import load_dotenv

token = "봇 토큰"

intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents)

voice_clients = {}

#yt_dl_options = {"format": "bestaudio/best", "noplaylist": "True"}
yt_dl_options = {
    "format": "bestaudio/best",
    "noplaylist": "True",
    "nocheckcertificate": True,
    "cachedir": False
}

ytdl = yt_dlp.YoutubeDL(yt_dl_options)

#ffmpeg_options = {'options': '-vn'}
ffmpeg_options = {
    'options': '-vn -reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'
}

#-----------------------------------------------------------------------
# 봇 세팅 영역
@bot.event
async def on_ready():
    print(f'{bot.user} 에 로그인하였습니다!')
    await bot.change_presence(status=discord.Status.online, activity=discord.Game("프로그래밍"))

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

#-------------------------------------------------------------------------
#봇 기능소개 영역


#--------------------------------------------------------------------------------------------------
#이벤트 입력 영역
    # 노래입력 명령어 처리
    if message.content.startswith('/플레이'):
        query = message.content[len('/플레이 '):].strip()  # ?play 뒤의 키워드 또는 URL 추출
        
        if not query:
            await message.channel.send("재생할 키워드나 URL을 입력하세요!")
            return

        try:
            # 사용자가 음성 채널에 있는지 확인
            if not message.author.voice or not message.author.voice.channel:
                await message.channel.send("음성 채널에 먼저 접속하세요!")
                return

            # 봇이 음성 채널에 연결
            if message.guild.id not in voice_clients or not voice_clients[message.guild.id].is_connected():
                voice_client = await message.author.voice.channel.connect()
                voice_clients[message.guild.id] = voice_client
            else:
                voice_client = voice_clients[message.guild.id]

            # 유튜브 검색 또는 URL 처리
            if "http" in query:  # URL 처리
                video_info = await asyncio.get_event_loop().run_in_executor(None, lambda: ytdl.extract_info(query, download=False))
            else:  # 키워드 검색
                search_query = f"ytsearch:{query}"
                video_info = await asyncio.get_event_loop().run_in_executor(None, lambda: ytdl.extract_info(search_query, download=False)['entries'][0])

            # 유튜브 URL 추출 및 재생
            url = video_info['url']
            title = video_info.get('title', '알 수 없는 제목')
            await message.channel.send(f"🎵 재생 중: **{title}**")

            player = discord.FFmpegPCMAudio(url, **ffmpeg_options)
            voice_client.play(player)

        except Exception as e:
            print(e)
            await message.channel.send("노래를 재생하는 도중 오류가 발생했습니다.")

    # 봇 아웃 명령어 처리
    elif message.content.startswith('/나가라'):
        if message.guild.id in voice_clients:
            await voice_clients[message.guild.id].disconnect()
            del voice_clients[message.guild.id]
            await message.channel.send("음성 채널을 떠났습니다!")
        else:
            await message.channel.send("봇이 음성 채널에 연결되어 있지 않습니다.")
#----------------------------------------------------------------------------------------------------------
# 봇 실행
bot.run(token)