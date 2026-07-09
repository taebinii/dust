import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 페이지 설정
st.set_page_config(page_title="서울시 미세먼지 대시보드", layout="wide")

# 2. 데이터 불러오기 (한글 인코딩 문제 해결 버전)
@st.cache_data
def load_data():
    file_name = "서울시 시간별 (초)미세먼지_2025년.csv"
    try:
        # 1차 시도: UTF-8-BOM (한글 깨짐 방지용 가장 범용적인 설정)
        df = pd.read_csv(file_name, encoding="utf-8-sig")
    except UnicodeDecodeError:
        try:
            # 2차 시도: CP949 (윈도우 엑셀 생성 파일용)
            df = pd.read_csv(file_name, encoding="cp949")
        except UnicodeDecodeError:
            # 3차 시도: EUC-KR (구형 한글 인코딩)
            df = pd.read_csv(file_name, encoding="euc-kr")
    
    # '일시' 컬럼을 datetime 객체로 변환
    df['일시'] = pd.to_datetime(df['일시'])
    
    # 시간순 정렬
    df = df.sort_values(by='일시')
    return df

df = load_data()

# 3. 사이드바 UI (검색 및 필터 옵션)
st.sidebar.header("🔍 검색 및 필터 옵션")

# 구(지역) 선택 (데이터의 '구분' 컬럼 활용)
districts = df['구분'].unique()
selected_district = st.sidebar.selectbox("구(지역)를 선택하세요:", districts)

# 선택한 구에 맞춰 데이터 1차 필터링
filtered_df = df[df['구분'] == selected_district]

# 날짜 범위 선택
min_date = filtered_df['일시'].min().date()
max_date = filtered_df['일시'].max().date()

start_date, end_date = st.sidebar.date_input(
    "날짜 범위를 선택하세요:",
    [min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

# 선택한 날짜에 맞춰 데이터 최종 필터링
mask = (filtered_df['일시'].dt.date >= start_date) & (filtered_df['일시'].dt.date <= end_date)
final_df = filtered_df.loc[mask]

# 4. 메인 화면 UI (시각화)
st.title("🏙️ 2025년 서울시 구별 (초)미세먼지 시각화")
st.markdown(f"**{selected_district}**의 미세먼지 및 초미세먼지 변화 추이입니다.")

if not final_df.empty:
    # 탭을 사용하여 그래프 분리
    tab1, tab2, tab3 = st.tabs(["미세먼지(PM10) 차트", "초미세먼지(PM2.5) 차트", "데이터 표 확인"])
    
    with tab1:
        fig_pm10 = px.line(final_df, x='일시', y='미세먼지(PM10)', 
                           title=f"{selected_district} 미세먼지(PM10) 추이",
                           labels={'미세먼지(PM10)': 'PM10 (㎍/㎥)'},
                           color_discrete_sequence=['#1f77b4'])
        st.plotly_chart(fig_pm10, use_container_width=True)
        
    with tab2:
        # 데이터의 컬럼명이 '초미세먼지(PM25)' 형태인지 확인 후 적용
        fig_pm25 = px.line(final_df, x='일시', y='초미세먼지(PM25)', 
                           title=f"{selected_district} 초미세먼지(PM2.5) 추이",
                           labels={'초미세먼지(PM25)': 'PM2.5 (㎍/㎥)'},
                           color_discrete_sequence=['#ff7f0e'])
        st.plotly_chart(fig_pm25, use_container_width=True)
        
    with tab3:
        st.dataframe(final_df.reset_index(drop=True))
else:
    st.warning("선택한 날짜 범위에 해당하는 데이터가 없습니다.")
