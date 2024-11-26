import discord
import asyncio
import yt_dlp
import configparser
from discord import app_commands
import Ai_Image

def run_bot():
    # 초기화
    config = configparser.ConfigParser()
    config.read("config.ini")
    ##======================================================
    #디코 
    TOKEN = config["DISCORD"]["HELLO_WORLD_BOT_TOKEN"]
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)
    tree = app_commands.CommandTree(client)


    #유튭 헤더
    queues = {}
    voice_clients = {}
    yt_dl_options = {"format": "bestaudio/best"}
    ytdl = yt_dlp.YoutubeDL(yt_dl_options)

    #ffmpeg 헤더
    ffmpeg_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

    @client.event
    async def on_ready():
        print(f'{client.user} 준비 완')
        await client.change_presence(status=discord.Status.online, activity=discord.Game("프로그래밍"))
        await tree.sync()  # 슬래시 커맨드 동기화

    # =======================================================================================================
    #명령어별 이벤트

    #------------------------------------------------------------------------
    #Play
    #-------------[Do]------------------
    #디스코드 메세지 창에 현재 재생중인 음악, 시간초, 
    #아래의 기능들을 버튼으로 만들예정 {술팽봇 참고 예정}
    #-------------[To Do]------------------

    #-------------[Done]------------------
    #음악 호출에 필요한 api 호출및 메세지 전송
    
    #-------------------------------------------------
    #미드져니 같은 AI이미지 생성 이벤트
     # 미드저니 같은 AI 이미지 생성 이벤트
    @tree.command(name="이미지만들기", description="Ai 이미지 생성!")
    async def 이미지만들기(interaction: discord.Interaction, prompt: str):
        await interaction.response.send_message("이미지 생성 중... 잠시만 기다려주세요!")

        try:
            # Ai 알고리즘 클래스입니다.
            image = await Ai_Image.Create_image(prompt)
            
            if image:
                # 이미지를 Discord 메시지로 전송
                output_path = "generated_image.png"
                image.save(output_path)
                with open(output_path, "rb") as file:
                    await interaction.followup.send(file=discord.File(file, "generated_image.png"))
            else:
                ErrorMessage = await interaction.followup.send("이미지 생성에 실패했습니다. 다시 시도해주세요.")

        except Exception as e:
            print(f"이미지 생성 오류: {e}")
            #await interaction.followup.send("이미지 생성 중 오류가 발생했습니다.")


    #------------------------------------음악재생 이벤트들
    @tree.command(name="플레이", description="음악을 재생합니다.")
    async def play_command(interaction: discord.Interaction, music: str):
        if not music:
            test = await interaction.response.send_message("재생할 음악이나, URL을 입력하세요! 삐빅..!")
            await test.delete(delay=2)
            return
        
        try:
            if not interaction.user.voice or not interaction.user.voice.channel:
                OutBotmsg = await interaction.response.send_message("음성 채널에 먼저 접속하세요! 삐빅..!")
                return
            
            Playing_msg = await interaction.response.send_message("음악을 재생 중입니다. 잠시만 기다려 주세요...")
            
            

            # 봇이 음성 채널에 연결
            if interaction.guild.id not in voice_clients or not voice_clients[interaction.guild.id].is_connected():
                voice_client = await interaction.user.voice.channel.connect()
                voice_clients[interaction.guild.id] = voice_client
            else:
                voice_client = voice_clients[interaction.guild.id]

            # 유튜브 검색 또는 URL 처리
            if "http" in music:  # URL 처리
                video_info = await asyncio.get_event_loop().run_in_executor(None, lambda: ytdl.extract_info(music, download=False))
            else:  # 키워드 검색
                search_query = f"ytsearch:{music}"
                video_info = await asyncio.get_event_loop().run_in_executor(None, lambda: ytdl.extract_info(search_query, download=False)['entries'][0])

            # 유튜브 URL 추출
            url = video_info['url']
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))

            song = data['url']
            youtube_url = video_info.get('webpage_url', 'URL을 찾을 수 없습니다.')
            player = discord.FFmpegOpusAudio(song, **ffmpeg_options)
            await interaction.followup.send(f"🎵 재생 중: **{youtube_url}**")
            voice_clients[interaction.guild.id].play(player)
            await asyncio.sleep(2)  # <= 유튜브 서치 되기전 바로 시작하면 URL은 null이 되기 때문에 2초정도의 딜레이가 적당 

            voice_clients[interaction.guild.id].play(player)
            await asyncio.sleep(2)
            await Playing_msg.delete()

        except Exception as e:
            print(e)
            #await interaction.followup.send("노래를 재생하는 중 에러가 발생했습니다. ERROR CODE -404")


    # /음악멈춰 명령어
    @tree.command(name="음악멈춰", description="음악을 멈춥니다.")
    async def stop_command(interaction: discord.Interaction):
        try:
            voice_clients[interaction.guild.id].pause()
            #await interaction.response.send_message("음악을 멈췄습니다.")
        except Exception as e:
            print(f"음악 멈추기 실패: {e}")
            #await interaction.response.send_message("음악을 멈추는 중 오류가 발생했습니다.")

    # /음악재개 명령어
    @tree.command(name="음악재개", description="음악을 재개합니다.")
    async def resume_command(interaction: discord.Interaction):
        try:
            voice_clients[interaction.guild.id].resume()
            #await interaction.response.send_message("음악을 재개했습니다.")
        except Exception as e:
            print(f"음악 재개 실패: {e}")
            #await interaction.response.send_message("음악을 재개하는 중 오류가 발생했습니다.")

    # /나가기 명령어
    @tree.command(name="나가기", description="음악을 정지하고 음성 채널을 떠납니다.")
    async def stop_music_command(interaction: discord.Interaction):
        try:
            voice_clients[interaction.guild.id].stop()
            await voice_clients[interaction.guild.id].disconnect()
            del voice_clients[interaction.guild.id]
            outmsg = await interaction.response.send_message("음악이 정지되었습니다. 음성 채널을 떠납니다.")
            await asyncio.sleep(2)
            await outmsg.delete()
        except Exception as e:
            print(f"음악 정지 실패: {e}")
            #await interaction.response.send_message("음악을 정지하는 중 오류가 발생했습니다.")

    # =======================================================================================================

    

    client.run(TOKEN)