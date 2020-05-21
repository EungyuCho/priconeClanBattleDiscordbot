import asyncio
import discord
import re

client = discord.Client()

# 토큰정보를 불러옵니다. (같이 메일에 보낸 토큰정보 파일을 최상위폴더와 같은 위치에 넣어주세요(Kyarubot 폴더 밖에)
f = open("../../staticImformation", "r")
token = f.readline()    #토큰정보를 로드해서 token 변수에 저장합니다
f.close()

battleCount = 0 #전투중인 유저변수입니다
innerPeople = [] #전투에 들어가있는 유저정보가 들어가있는 배열입니다
bossName = '1넴' #현재 몇번째 보스인지 담겨있는 변수입니다
bossHp = '0만' #현재 보스 체력이 담겨있는 배열입니다


def replaceRight(original, old, new, count_right):
    repeat = 0
    text = original
    old_len = len(old)

    count_find = original.count(old)
    if count_right > count_find:  # 바꿀 횟수가 문자열에 포함된 old보다 많다면
        repeat = count_find  # 문자열에 포함된 old의 모든 개수(count_find)만큼 교체한다
    else:
        repeat = count_right  # 아니라면 입력받은 개수(count)만큼 교체한다

    while (repeat):
        find_index = text.rfind(old)  # 오른쪽부터 index를 찾기위해 rfind 사용
        text = text[:find_index] + new + text[find_index + old_len:]

        repeat -= 1

    return text

# 봇이 구동되었을 때 동작되는 코드입니다.
@client.event
async def on_ready():
    print("Logged in as ") #화면에 봇의 아이디, 닉네임이 출력됩니다.
    print(client.user.name)
    print(client.user.id)
    # 디스코드에는 현재 본인이 어떤 게임을 플레이하는지 보여주는 기능이 있습니다.
    # 이 기능을 사용하여 봇의 상태를 간단하게 출력해줄 수 있습니다.
    # await client.change_presence(game=discord.Game(name="반갑습니다 :D", type=1))

# 봇이 새로운 메시지를 수신했을때 동작되는 코드입니다.
@client.event
async def on_message(message):
    chan = message.channel
    global battleCount
    global innerPeople
    global bossHp
    global bossName
    if message.author.bot: #만약 메시지를 보낸사람이 봇일 경우에는
        return None #동작하지 않고 무시합니다.

    id = message.author.id #id라는 변수에는 메시지를 보낸사람의 ID를 담습니다.
    channel = message.channel #channel이라는 변수에는 메시지를 받은 채널의 ID를 담습니다.

    strIdCode = str(id)

    #도움말 기능입니다. embed를 출력합니다.
    if message.content.startswith('!도움말'):
        embed = discord.embeds.Embed(title='클랜배틀 도움용 봇입니다.', description='개선사항또는 문의사항이 있으면 랜서에게 문의해주세요!', color=0x8080ff)
        embed.set_author('name=프리코네 간판 캬루쟝')
        embed.set_thumbnail(url="https://ifh.cc/g/FMHeeT.jpg")
        embed.add_field(name='(명령어)', value='(설명)', inline=False)
        embed.add_field(name='!입장', value='보스에 입장 전 입력해주시면 돼요!', inline=False)
        embed.add_field(name='!퇴장', value='보스 전투가 끝나고나서 입력해주시면 돼요!', inline=False)
        embed.add_field(name='!현재인원', value='현재 보스전을 하고있는 인원을 알려줘요!', inline=False)
        embed.add_field(name='!정보입력', value='현재 보스 상태를 업데이트해줘요! Ex) !정보입력 3넴/34만) ', inline=False)
        embed.add_field(name='!보스', value='현재 보스 상태를 알려줘요!', inline=False)
        embed.add_field(name='!전투중유저', value='진입한 유저들을 알려줘요!', inline=False)
        embed.add_field(name='!딜링', value='보스가 안죽었을때 딜링시 적어주세요! Ex) !딜링 2만', inline=False)
        await  chan.send(embed=embed)

    elif message.content.startswith('!입장'):
        if(message.author in innerPeople):
            await chan.send(str(message.author) +'님은 이미 입장하셨어요!')
        else:
            battleCount += 1
            innerPeople.append(message.author)
            await chan.send(str(message.author) +'님이 전투에 입장하셨어요!')

    elif message.content.startswith('!퇴장'):
        if(message.author in innerPeople):
            battleCount -= 1
            innerPeople.remove(message.author)
            await chan.send(str(message.author) +'님이 퇴장하셨어요!')
        else:
            await  chan.send(str(message.author) +'님은 아직 입장하지 않았어요!')

    elif message.content.startswith('!현재인원'):
        await  chan.send('현재 입장인원은 ' + str(len(innerPeople)) + '명 이에요!')

    elif message.content.startswith('!정보입력'):
        bossInfo = message.content
        infoArr = bossInfo.split('/')
        if(len(infoArr)==2):
            bossName = str(infoArr[0]).replace('!정보입력', '').replace(' ', '')
            bossHp = str(infoArr[1]).replace(' ', '')
            await  chan.send('정보입력이 완료되었어요!~')
        else:
            await  chan.send('입력이 잘못되었어요! Ex) !정보입력 4넴/135만')

    elif message.content.startswith('!보스'):
        await  chan.send('현재 보스는 ' + bossName + '이고, 체력은 ' + bossHp + '남았어요! 힘내요~!')

    elif message.content.startswith('!딜링'):
        beforeHp = re.findall('\d+', str(bossHp))
        deal = re.findall('\d+', str(message.content))
        remainHp = int(beforeHp[0]) - int(deal[0])
        if(remainHp<0):
            await  chan.send('!정보입력 을 사용해서 다음보스 정보를 입력해주세요!')
        else:
            bossHp = str(int(beforeHp[0]) - int(deal[0])) + '만'
            await  chan.send('보스의 체력이' + bossHp + '만큼 남았어요!')

    elif message.content.startswith('!전투중유저'):
        if(innerPeople.__len__()==0):
            await  chan.send('현재 입장중인 인원이 없어요!')
        elif(innerPeople.__len__()==1):
            await  chan.send('현재 ' +str(innerPeople[0].name) + '님이 입장해있어요!')
        else:
            people = ''
            for person in innerPeople:
                people += str(person.name) +', '
            await  chan.send('현재 ' + replaceRight(people, ',', '', 1) + '님이 입장해있어요!')




client.run(token)