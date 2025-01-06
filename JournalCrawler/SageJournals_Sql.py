from datetime import datetime

import pymssql


# 连接数据库
def connect_to_sql_server(server, database, username, password):
    try:
        conn = pymssql.connect(server=server, database=database, user=username, password=password)
        return conn
    except Exception as e:
        print(f"An error occurred: {e}")


# 插入每年每卷期刊URL
def insert_to_sql_server_volumes(list_data, conn):
    try:
        cursor = conn.cursor()
        cursor.executemany(
            "INSERT INTO sage_journals_issues (journal_name, year, issues_url,down_status,down_time) VALUES (%s, %s, %s,%s,%s)",
            list_data)
        conn.commit()
        cursor.close()
        print("Data inserted successfully.")
    except Exception as e:
        print("Caught a ValueError:", e)


# 插入每本期刊的URL(列表存放的是每卷的页面URL)
def insert_to_sql_server_pages(list_data, conn):
    try:
        cursor = conn.cursor()
        cursor.executemany(
            "INSERT INTO sage_journal_pages (journal_name, year, volume,issue,page_url,down_status,down_time) VALUES (%s, %s, %s,%s,%s,%s,%s)",
            list_data)
        conn.commit()
        cursor.close()
        print("Data inserted successfully.")
    except Exception as e:
        print("Caught a ValueError:", e)


# 更新下载状态 以及下载时间
def update_status_to_sql_server(table_name, status, id):
    conn = connect_to_sql_server(server='192.168.0.253', database='DB_2025_xk', username='sa',
                                 password='Zeda#Server#2022@123')
    cursor = conn.cursor()
    cursor.execute(f"UPDATE {table_name} SET down_status = %s WHERE id = %d", (status, id))
    # 更新时间
    time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(f"UPDATE {table_name} SET down_time = %s WHERE id = %d", (time_now, id))
    conn.commit()
    cursor.close()
    conn.close()
