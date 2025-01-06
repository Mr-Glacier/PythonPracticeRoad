import os
import random
import time
from datetime import datetime
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import SageJournals_Sql
import wonderfulTools


# 解析每本期刊的 年列表
def analysis_all_volumes():
    conn = SageJournals_Sql.connect_to_sql_server(server='192.168.0.253', database='DB_2025_xk', username='sa',
                                                  password='Zeda#Server#2022@123')
    dict_file = {
        'jer': 'https://journals.sagepub.com/loi/jer',
        'pif': 'https://journals.sagepub.com/loi/pif',
        'pid': 'https://journals.sagepub.com/loi/pid',
        'trr': 'https://journals.sagepub.com/loi/trr'
    }
    save_path = 'E:\\ZKZD2025\\Journal\\journals.sagepub.com\\'
    list_data = []
    for key, value in dict_file.items():
        html_str_txt = wonderfulTools.read_text_from_file(f"{save_path}\\{key}\\{key}.html")
        print(key)
        journal_name = key
        soup = BeautifulSoup(html_str_txt, 'html.parser')
        items = (soup.find('div', class_='loi__banner-list')).find('div', class_='tab__content')
        for item in items:
            for li in item.find_all('li', class_='tab__nav__item'):
                year = li.find('a').text
                url = 'https://journals.sagepub.com' + li.find('a').get('href')
                print(year, url)
                one_object = (journal_name, year, url, '否', '-')
                list_data.append(one_object)
    SageJournals_Sql.insert_to_sql_server_volumes(list_data, conn)


# 下载每年的期刊分卷页面
def down_all_years_volumes(main_path: str):
    conn = SageJournals_Sql.connect_to_sql_server(server='192.168.0.253', database='DB_2025_xk', username='sa',
                                                  password='Zeda#Server#2022@123')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sage_journals_issues")
    rows = cursor.fetchall()
    for row in rows:
        status = row[4]
        if status == '否':
            url = row[3]
            year = row[2]
            journal_name = row[1]
            html_str_txt = launch_browser_with_defaults(url, 'div#pb-page-content')
            if html_str_txt == 'Error':
                continue
            else:
                wonderfulTools.save_text_to_file(html_str_txt,
                                                 f"{main_path}\\{journal_name}\\{journal_name}_{year}.html")
    cursor.close()


# 解析每年的期刊分卷页面
def analysis_issues_page(save_path: str):
    try:
        conn = SageJournals_Sql.connect_to_sql_server(server='192.168.0.253', database='DB_2025_xk', username='sa',
                                                      password='Zeda#Server#2022@123')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sage_journals_issues")
        rows = cursor.fetchall()
        list_data = []
        for row in rows:
            status = row[4]
            url = row[3]
            year = row[2]
            journal_name = row[1]
            html_text = wonderfulTools.read_text_from_file(f"{save_path}\\{journal_name}\\{journal_name}_{year}.html")
            print(f"{journal_name} {year}")
            html_issue = BeautifulSoup(html_text, 'html.parser')
            items = (html_issue.find_all('div', class_='loi__issues'))
            print(len(items))
            for item in items:
                for issue in item.find_all('div', class_='loi__issue'):
                    issue_url = 'https://journals.sagepub.com' + issue.find('a').get('href')
                    volume_issue_year = issue.find('a').text
                    print(f"{volume_issue_year} {issue_url}")
                    volume = (volume_issue_year.split(',')[0]).replace('Volume', '').replace(' ', '')
                    issue_ = (volume_issue_year.split(',')[1]).replace('Issue ', '').replace(' ', '')
                    page_number = issue.find('div', class_='loi__issue__page-range')
                    data_line = (journal_name, year, volume, issue_, issue_url, "否", "-")
                    list_data.append(data_line)
                    print("---------")
            print("END")

        SageJournals_Sql.insert_to_sql_server_pages(list_data, conn)
        cursor.close()
        conn.close()

    except Exception as e:
        print("Caught a ValueError:", e)


# 获取页面信息返回
def launch_browser_with_defaults(dict_url: str, wait_thing: str):
    try:
        with sync_playwright() as p:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
                # "Referer": dict_url,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"'
                # "cookie": "cf_clearance=Xj7E.zLDayVNGMmhgMeImsI_Jc8LH1YYKEV9ONnlRMk-1735827947-1.2.1.1-OPNPeVg0G2xEMA75JeMuMYsjhdzj9LEdAl9PBOuEHiXCwC4OmXMrJx.Q0lg_7u12dYOlQSMIlHvPrMrim4DQUSSqtsXmCq3gc2afbdNj3u.KaT50uhb79lbXcBhH_2dwz566rAZTlm6yW4Vc2_L.rkUoy_6XsqLq0EhcH6epaxa.VJ7qZ6p8uIkebXpQbE0Vb5ibo0tms32LMWPBgU_d7j4v10ZOzETG9M9rsM_WhmVO0MxJrzisZ3KaxE8XIcbCCrmag17QlulCfMgsNEADbj7gNIoQWpN8_bFJdaAg7L2Y2eit5B.AbY62qK60kZ7kos0ozAj4e.spL74UmBbHgBLsgtHx3P0zojX01KOTJCDht6wReAWMuI_j20RaOHLFVl.t49jEq5B6l53gpXsPyeiR3o3VFuhz6bb.PUUB_AfdUQPlOVetuwG6M3pbKYLG	;MAID=6eQZ1ACuuflYInKv9+9EHA==; _gcl_au=1.1.675769707.1735780634; _ga=GA1.1.120898910.1735780634; sbt_i=7NWFjMzY3YjYtYTM0OS00YzA2LTk5OGItMWRmMDg0YzRiOWNhOzNWJiM2ViNmItMDg4My00MjdlLWEzOGEtNDNlZTBlYTJjZDkyOzsA=; th_u=7gn~MYfX3-OX5%24hp%26Mbc; OptanonAlertBoxClosed=2025-01-02T03:39:09.570Z;"
            }
            browser = p.chromium.launch(proxy={
                "server": "http://127.0.0.1:7890"},
                headless=False,  # 设置为 True 以启用无头模式
                slow_mo=500,  # 慢动作模式，延迟 500ms，有助于调试
                args=["--window-size=1920,1080"]  # 设置窗口大小
            )
            content = browser.new_context(extra_http_headers=headers)
            page = content.new_page()
            page.goto(dict_url, wait_until='load', timeout=300000)  # 等待直到网络空闲
            page.wait_for_selector(wait_thing, timeout=300000)
            html_str = page.content()
            title = page.title()
            print(f"Page title: {title}")
            content.close()
            browser.close()
            if '请稍候…' in html_str:
                return 'Error'
            # 其他操作...
            return html_str
    except Exception as e:
        print(f"An error occurred: {e}")
        return 'Error'


# 下载每本的列表文章页面
def down_issues_page():
    try:
        conn = SageJournals_Sql.connect_to_sql_server(server='192.168.0.253', database='DB_2025_xk', username='sa',
                                                      password='Zeda#Server#2022@123')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sage_journal_pages")
        rows = cursor.fetchall()
        for row in rows:
            status = row[6]
            if status == '否':
                print(f"{row[0]}")
                url = row[5]
                journal_name = row[1]
                year = row[2]
                volume = row[3]
                issue = row[4]
                html_str_txt = launch_browser_with_defaults(url, 'div#pb-page-content')
                if html_str_txt == 'Error':
                    continue
                else:
                    wonderfulTools.save_text_to_file(html_str_txt,
                                                     f"{main_path}\\{journal_name}\\pages\\{journal_name}_{year}_{volume}_{issue}.html")
                    SageJournals_Sql.update_status_to_sql_server("sage_journal_pages", '是', row[0])
                sleep_time = random.uniform(1, 10)
                time.sleep(sleep_time)
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == '__main__':
    # 解析每天拥有多少
    # analysis_all_volumes()

    main_path = 'E:\\ZKZD2025\\Journal\\journals.sagepub.com\\'
    # 下载每年的分卷页面
    # down_all_years_volumes(main_path)

    # 解析详情issues页
    # analysis_issues_page(main_path)

    # 下载每卷的详情页
    # down_issues_page()
