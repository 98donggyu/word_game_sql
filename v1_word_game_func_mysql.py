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
    while game_cnt <= 5:
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

def inputDB(corr_cnt, exe_time):
    try:
        conn = pymysql.connect(host=HOST, port=PORT, user=USER, passwd=PASSWD, db=DB1, charset='utf8')
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS game_records1(
                id INT AUTO_INCREMENT PRIMARY KEY,
                corr_cnt INT,
                record VARCHAR(255),
                regdate DATETIME
            )
        ''')

        cursor.execute(
            "INSERT INTO game_records1(corr_cnt, record, regdate) VALUES (%s, %s, %s)",
            (corr_cnt, exe_time, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
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

        print("랭킹\t정답수\t걸린시간\t\t게임일시")
        print("-" * 48)

        # cursor.execute("SELECT * FROM game_records1 ORDER BY corr_cnt DESC, record ASC LIMIT 10")
        # rows = cursor.fetchall()

        # for rank, row in enumerate(rows):
            # print("{0:^6}\t{1:^6}\t{2:^8} {3:^22}".format((rank + 1), row[1], row[2], row[3]))
        
        cursor.execute("SELECT * FROM game_records1 ORDER BY corr_cnt DESC, record ASC LIMIT 10")
        rows = cursor.fetchall()  # fetchall()을 사용하여 모든 결과를 가져옵니다.

        for rank, row in enumerate(rows):
            regdate = row[3].strftime('%Y-%m-%d %H:%M:%S')
            print("{0:^6}\t{1:^6}\t{2:^8} {3:^22}".format((rank + 1), row[1], row[2], regdate))

    except pymysql.MySQLError as err:
        print(f"DB Error: {err}")
    finally:
        if conn and conn.open:
            conn.close()

if __name__ == '__main__':
    words = wordLoad()
    corr_cnt, exe_time = game_run(words)

    inputDB(corr_cnt, exe_time)
    print("-" * 48)
    if corr_cnt >= 3:
        print("결과 : 합격")
    else:
        print("불합격")
    print("게임 시간 :", exe_time, "초", "정답 개수 : {}".format(corr_cnt))
    print("-" * 48)
    getDB()
    print("-" * 48)