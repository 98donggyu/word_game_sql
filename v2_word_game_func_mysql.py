import random
import time
import pymysql
import datetime
from dotenv import load_dotenv
import os
from pygame import mixer
mixer.init()

load_dotenv()

# MySQL 설정
HOST = os.getenv("HOST")
PORT = int(os.getenv("PORT"))
USER = os.getenv("USER")
PASSWD = os.getenv("PASSWD")
DB1 = os.getenv("DB1")
DB2 = os.getenv("DB2")

game_round = 5

def wordLoad():
    words = []
    try:
        with open('./data/word.txt', 'r') as f:
            for word in f:
                words.append(word.strip())
    except FileNotFoundError:
        print("word.txt 파일이 없습니다.")
        exit()
    return words

def getTime(start, end):
    exe_time = end - start
    exe_time = format(exe_time, ".3f")
    return exe_time

def game_run(words):
    input("Ready? Press Enter Key!")
    game_cnt = 1
    corr_cnt = 0

    start = time.time()
    while game_cnt <= game_round:
        random.shuffle(words)
        que_word = random.choice(words)

        print()
        print("*Question # {}".format(game_cnt))
        print(que_word)

        input_word = input()
        print()

        if str(que_word).strip() == str(input_word).strip():
            mixer.music.load('good.wav')
            mixer.music.play()
            print("Pass!")
            corr_cnt += 1
        else:
            mixer.music.load('bad.wav')
            mixer.music.play()
            print("Wrong!")

        game_cnt += 1
        end = time.time()

    return corr_cnt, getTime(start, end)

def inputDB(userid, corr_cnt, exe_time):
    try:
        conn = pymysql.connect(host=HOST, port=PORT, user=USER, passwd=PASSWD, db=DB1, charset='utf8')
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS game_records2(
                userid VARCHAR(255) PRIMARY KEY NOT NULL,
                corr_cnt INTEGER,
                record VARCHAR(255),
                regdate DATETIME
            )
        ''')

        cursor.execute("SELECT EXISTS(SELECT * FROM game_records2 WHERE userid = %s)", (userid,))
        user_exist = cursor.fetchone()[0]

        if user_exist:
            cursor.execute(
                "UPDATE game_records2 SET corr_cnt = %s, record = %s, regdate = %s WHERE userid = %s AND corr_cnt < %s",
                (corr_cnt, exe_time, datetime.datetime.now(), userid, corr_cnt)
            )
        else:
            cursor.execute(
                "INSERT INTO game_records2(userid, corr_cnt, record, regdate) VALUES (%s, %s, %s, %s)",
                (userid, corr_cnt, exe_time, datetime.datetime.now())
            )

        conn.commit()
    except pymysql.MySQLError as err:
        print(f"DB Error: {err}")
    finally:
        if conn and conn.open:
            cursor.close()
            conn.close()

def getDB():
    try:
        conn = pymysql.connect(host=HOST, port=PORT, user=USER, passwd=PASSWD, db=DB1, charset='utf8')
        cursor = conn.cursor()

        print("순번\t선수id\t정답수\t걸린시간\t게임일시")
        print("-" * 60)

        cursor.execute("SELECT * FROM game_records2 ORDER BY corr_cnt DESC, record ASC LIMIT 10")
        rows = cursor.fetchall()

        for rank, row in enumerate(rows):
            regdate = row[3].strftime('%Y-%m-%d %H:%M:%S')
            print("{0:^4}\t{1:^6}\t{2:^6}\t{3:^8} {4:^22}".format((rank + 1), row[0], row[1], row[2], regdate))

    except pymysql.MySQLError as err:
        print(f"DB Error: {err}")
    finally:
        if conn and conn.open:
            cursor.close()
            conn.close()

def passOrFailPrint(corr_cnt, exe_time):
    if corr_cnt >= 3:
        print("결과 : 합격")
    else:
        print("불합격")
    print("게임 시간 :", exe_time, "초", "정답 개수 : {}".format(corr_cnt))

if __name__ == '__main__':
    words = wordLoad()
    userid = input("게임 선수 id를 입력하세요. : ")
    corr_cnt, exe_time = game_run(words)
    inputDB(userid, corr_cnt, exe_time)
    print("-" * 60)
    passOrFailPrint(corr_cnt, exe_time)
    print("-" * 60)
    getDB()
    print("-" * 60)