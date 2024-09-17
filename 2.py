import streamlit as st
import plotly.express as px
import pandas as pd
import os
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="Superstore!!!", page_icon=":bar_chart:", layout="wide")

st.title(" :bar_chart: Sample SuperStore EDA")
st.markdown('<style>div.block-container{padding-top:1rem;}</style>', unsafe_allow_html=True)

fl = st.file_uploader(":file_folder: Upload a file", type=(["csv", "txt", "xlsx", "xls"]))
if fl is not None:
    filename = fl.name
    st.write(filename)
    df = pd.read_csv(fl, encoding="ISO-8859-1")
else:
    os.chdir(os.getcwd())
    df = pd.read_csv("sample/subscribe.csv", encoding="ISO-8859-1")

st.write(df.head())

st.subheader("제거할 컬럼 선택")
columns = df.columns.tolist()
selected_columns = st.multiselect("선택 가능한 컬럼들:", columns)

if selected_columns:
    df1 = df[df.columns.difference(selected_columns)]
    st.write(df1.head())
else:
    df1 = df.copy()
    st.write("No columns selected for filtering.")

st.subheader('결측치를 포함한 컬럼')
# Check missing values for each column and display in a bar chart
missing_counts = df1.isnull().sum()
missing_counts = missing_counts[missing_counts > 0]

if not missing_counts.empty:
    fig = px.bar(missing_counts, x=missing_counts.index, y=missing_counts.values,
                 labels={'x': 'Columns', 'y': 'Number of Missing Values'},
                 title='Missing Values per Column')
    fig.update_traces(text=missing_counts.values, textposition='outside')
    st.plotly_chart(fig)
else:
    st.write("No missing values in the selected columns.")

st.subheader('이상치 제거')
outlier_column = st.selectbox('이상치를 제거할 컬럼을 선택하세요:', df1.columns)
# 임계값 입력
threshold_value = st.number_input('임계값을 입력하세요:', value=0)
# 이상 또는 이하 선택
outlier_condition = st.radio('임계값 이상 또는 이하 값들을 제거합니다:', ['이상', '이하'])

# 필터링 및 제거
butt = st.button('이상치 제거')
if butt:
    if outlier_condition == '이상':
        # 임계값 이상인 값을 제거
        df2 = df1[df1[outlier_column] < threshold_value]
    else:
        # 임계값 이하인 값을 제거
        df2 = df1[df1[outlier_column] > threshold_value]
    
    st.write(f'{outlier_column}에서 {outlier_condition} {threshold_value}인 값을 제거했습니다.')

    st.write(df2.head())
else:
    df2 = df1.copy()

# Categorical variable visualization
st.subheader('범주형 변수 시각화')

# selected_cat_column = st.selectbox('Select a column to visualize:', filtered_df.columns)
categorical_columns = df2.select_dtypes(include=['object', 'category']).columns.tolist()
selected_cat_columns = st.multiselect("Select Sub-Categories:", categorical_columns)


if selected_cat_columns:
    for selected_cat_column in selected_cat_columns:

        category_counts_df = df2[selected_cat_column].value_counts().reset_index()
        category_counts_df.columns = [selected_cat_column, 'count']

        ################ 데이터 시각화 1.
        # 페이지를 2개로 나누어 
        col1, col2 = st.columns(2)
        # 왼쪽(첫번째 열)에는 카테고리별 판매량 
        with col1:
            st.subheader("{} 카운트".format(selected_cat_column))
            fig = px.bar(category_counts_df, x = selected_cat_column, y = "count", color=selected_cat_column,
                        template = "seaborn")
            st.plotly_chart(fig,use_container_width=True, height = 200)
            
        with col2:
            st.subheader("{} 카운트".format(selected_cat_column))
            pie_fig = px.pie(category_counts_df, names=selected_cat_column, values='count',
                            title=f'Percentage of each category in {selected_cat_column}')
            st.plotly_chart(pie_fig, use_container_width=True)
            
        categorical_columns.remove(selected_cat_column)
        
numerical_columns = df2.select_dtypes(include=['number']).columns.tolist()
st.subheader('수치형 변수 시각화')

selected_num_columns = st.multiselect("Select Sub-Categories:", numerical_columns)

if selected_num_columns:
    for selected_num_column in selected_num_columns:
        
        num_category_counts_df = df2[selected_num_column].value_counts().reset_index()
        num_category_counts_df.columns = [selected_num_column, 'count']
        
        st.subheader("{} 카운트".format(selected_num_column))
        fig = px.bar(num_category_counts_df, x = selected_num_column, y = "count", color=selected_num_column,
                    template = "seaborn")
        st.plotly_chart(fig,use_container_width=True, height = 200)

        
        numerical_columns.remove(selected_num_column)

