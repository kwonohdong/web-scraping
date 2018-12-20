import sys
import os
from collections import Counter # 문자열을 기준으로 각각의 요소별 개수 찾는 라이브러리
import requests
import lxml
from time import sleep
from bs4 import BeautifulSoup
from konlpy.tag import Okt # 문장을 기준으로 명사 도출 라이브러리
from wordcloud import WordCloud # 워드클라우드 제공 라이브러리
import matplotlib.pyplot as plt # 워드클라우드를 표현하기위한 파레트


target_url_domain = "https://search.joins.com/TotalNews?page="
target_url_query = "&Keyword="
target_url_rest = "&SearchCategoryType=TotalNews"

def get_link_from_news_article(keword:str, total_page_num:int) -> list:
    """키워드에 해당하는 기사 링크 정보를 반환

    return 기사 링크 리스트.
    """
    article_link_list = []

    for curr_page_num in range(1, total_page_num + 1):
        response = requests.get(target_url_domain + str(curr_page_num) + target_url_query + keword + target_url_rest)
        html = response.text
        soup = BeautifulSoup(html, 'lxml')

        news_articles_body = soup.find('ul', attrs={'class':'list_default'}) # 키워드에 해당하는 기사 목록 접근
        news_articles = news_articles_body.find_all('li')

        for article in news_articles:
            article_link_list.append(article.a['href'])

    return article_link_list

def write_article_body_in_file(article_link_list:list, file_name:str, sleep_seconds:float):
    """기사 링크에 해당하는 본문 내용을 파일에 쓰기."""
    try:
        with open(file_name, 'wt', encoding='utf-8') as f:
            for url in article_link_list:
                f.write(get_article_body_for_url(url) + '\n')
                sleep(sleep_seconds)
    except FileNotFoundError as ex:
        print(ex)

def get_article_body_for_url(url:str) -> str:
    """URL 링크의 본문 내용 가져오기

    return 기사 본문 내용.
    """
    response = requests.get(url)
    html = response.text
    soup = BeautifulSoup(html, 'lxml')
    
    article_body = soup.find('div', attrs={'id':'article_body'})
    return article_body.text.strip()

def draw_word_cloud(read_file_name:str, most_common_keword_num:int):
    """워드클라우드 그리기

    read_file_name: 워드클라우드의 대상 데이터 파일
    most_common_keword_num: 워드클라우드로 보여주기 위한 주요 키워드 갯수.
    """
    try:
        stop_words = ['전', '등', '신', '이', '그', '바', '기자', '선', '건', '때', '흐', '것', '로', '프', '더', '고', '위']
        okt = Okt()

        with open(read_file_name, 'r', encoding='utf-8') as f:
            contents = f.readlines()
            
            all_sentence = ' '.join(contents)
            nouns = [noun for noun in okt.nouns(all_sentence) if noun not in stop_words]
            data = Counter(nouns).most_common(most_common_keword_num)
            # print(nouns)
            # print(data)

            word_cloud = WordCloud(
                font_path='/Fonts/malgun.ttf',
                relative_scaling=0.2,
                background_color='white',
                max_words=2000,
                width=1000,
                height=1000,
            ).generate_from_frequencies(
                dict(data),
                # max_font_size=35,
                )

            plt.figure(figsize=(16, 8))
            plt.imshow(word_cloud, interpolation='bilinear')
            plt.axis('off')
            plt.show()

    except FileNotFoundError as ex:
        print(ex)

def main(argv):
    """중앙일보에서 특정 키워드를 포함하는 신문기사 크롤링 메인 모듈."""
    # argv = ['데이터', '1', 'D:\\article_file2.txt', '0.0', '50']
    if len(argv) < 5:
        print('[키워드][총 페이지 개수][기사 추출 결과 저장용 파일명 - 경로 포함][sleep seconds][most common keyword number]')
        print(argv)
        return

    try:
        keword = argv[0]
        total_page_num = int(argv[1])
        article_file_name = argv[2]
        sleep_seconds = float(argv[3])
        most_common_keword_num = int(argv[4])

        article_link_list = get_link_from_news_article(keword, total_page_num)
        write_article_body_in_file(article_link_list, article_file_name, sleep_seconds)
        draw_word_cloud(article_file_name, most_common_keword_num)
    except EOFError as ex:
        print(ex)
    except KeyboardInterrupt as ex: # ctrl + c
        print(ex)

if __name__ == '__main__':
    main(sys.argv)


