
import streamlit as st
import json
import os
import pandas as pd
import uuid

FILE = 'drink_orders.json'

# =========================
# 讀取與儲存資料
# =========================
def load_records():
    if not os.path.exists(FILE):
        return []
    with open(FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_records(records):
    with open(FILE, 'w', encoding='utf-8') as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

st.set_page_config(page_title='飲料訂單管理系統', page_icon='🧋', layout='wide')

st.title('🧋 飲料訂單管理系統')
st.caption('輕鬆登記訂單、自動計算杯數與金額')

records = load_records()

# =========================
# 新增訂單
# =========================
st.subheader('📝 新增飲料訂單')

with st.form('add_form', clear_on_submit=True):

    col1, col2 = st.columns(2)

    with col1:
        name = st.text_input('訂購人姓名')
        drink = st.text_input('飲料名稱', placeholder='例如：珍珠奶茶')

        sweetness = st.selectbox(
            '甜度',
            ['無糖', '微糖', '少糖', '半糖', '正常糖', '全糖']
        )

    with col2:
        ice = st.selectbox(
            '冰塊',
            ['去冰', '微冰', '少冰', '正常冰', '完全去冰', '熱飲']
        )

        quantity = st.number_input(
            '數量（杯）', min_value=1, step=1
        )

        price = st.number_input(
            '單價（元）', min_value=0, step=5
        )

    note = st.text_input('備註', placeholder='例如：加珍珠、不要吸管')

    submitted = st.form_submit_button('➕ 新增訂單')

if submitted:
    if name.strip() == '' or drink.strip() == '':
        st.error('請填寫訂購人姓名及飲料名稱！')
    elif price <= 0:
        st.error('飲料單價必須大於 0！')
    else:
        amount = int(quantity * price)

        records.append({
            'ID': str(uuid.uuid4()),
            '姓名': name.strip(),
            '飲料': drink.strip(),
            '甜度': sweetness,
            '冰塊': ice,
            '數量': int(quantity),
            '單價': int(price),
            '金額': amount,
            '備註': note
        })

        save_records(records)
        st.success(f'已新增 {name} 的 {drink} 訂單，共 {quantity} 杯！')
        st.rerun()

st.divider()

# =========================
# 訂單統計
# =========================
st.subheader('📊 訂單統計')

total_cups = sum(r['數量'] for r in records)
total_amount = sum(r['金額'] for r in records)
total_orders = len(records)

col1, col2, col3 = st.columns(3)

col1.metric('🧋 總杯數', f'{total_cups} 杯')
col2.metric('💰 總金額', f'{total_amount:,} 元')
col3.metric('👥 訂單筆數', f'{total_orders} 筆')

st.divider()

# =========================
# 訂單明細
# =========================
st.subheader('📋 訂單明細')

if records:

    df = pd.DataFrame(records)

    # 搜尋訂購人
    keyword = st.text_input('🔍 搜尋訂購人姓名或飲料名稱')

    filtered_df = df[
        df['姓名'].astype(str).str.contains(keyword, case=False, na=False)
        | df['飲料'].astype(str).str.contains(keyword, case=False, na=False)
    ] if keyword else df

    st.dataframe(
        filtered_df.drop(columns=['ID'], errors='ignore'),
        use_container_width=True,
        hide_index=True
    )

    # 匯出 CSV
    csv = filtered_df.drop(
        columns=['ID'], errors='ignore'
    ).to_csv(index=False).encode('utf-8-sig')

    st.download_button(
        '📥 匯出訂單 Excel 可讀 CSV',
        data=csv,
        file_name='飲料訂單.csv',
        mime='text/csv'
    )

    st.divider()

    # =========================
    # 每種飲料統計
    # =========================
    st.subheader('🥤 各飲料統計')

    drink_stats = df.groupby('飲料').agg(
        總杯數=('數量', 'sum'),
        總金額=('金額', 'sum')
    ).reset_index()

    st.dataframe(
        drink_stats,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    # =========================
    # 每人應付金額
    # =========================
    st.subheader('👤 每人應付金額')

    person_stats = df.groupby('姓名').agg(
        訂購杯數=('數量', 'sum'),
        應付金額=('金額', 'sum')
    ).reset_index()

    st.dataframe(
        person_stats,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    # =========================
    # 刪除訂單
    # =========================
    st.subheader('🗑️ 刪除訂單')

    selected_id = st.selectbox(
        '選擇要刪除的訂單',
        options=[r['ID'] for r in records],
        format_func=lambda x: next(
            f"{r['姓名']} - {r['飲料']} ({r['數量']}杯)"
            for r in records if r['ID'] == x
        )
    )

    if st.button('刪除選取訂單', type='secondary'):
        records = [r for r in records if r['ID'] != selected_id]
        save_records(records)
        st.success('訂單已刪除！')
        st.rerun()

else:
    st.info('目前還沒有任何飲料訂單，請先新增訂單！')
