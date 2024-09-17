import streamlit as st
import plotly.express as px
import pandas as pd
import os
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="Superstore!!!", page_icon=":bar_chart:",layout="wide")

st.title(" :bar_chart: Sample SuperStore EDA")
st.markdown('<style>div.block-container{padding-top:1rem;}</style>',unsafe_allow_html=True)

fl = st.file_uploader(":file_folder: Upload a file",type=(["csv","txt","xlsx","xls"]))
if fl is not None:
    filename = fl.name
    st.write(filename)
    df = pd.read_csv(fl, encoding="ISO-8859-1")
else:
    # 이걸 해줘야 파일 업로드 안되어도 아래 상태를 오류없이 유지 할 수 있음
    os.chdir(os.getcwd())
    df = pd.read_csv("sample/Superstore.csv", encoding = "ISO-8859-1")


# 1. 분석할 기간 설정 
df["Order Date"] = pd.to_datetime(df["Order Date"])

st.write(df.head())

##################
# 2. 컬럼 선택 및 필터링
st.subheader("Select Columns to Filter")
columns = df.columns.tolist()
default_columns = ['Order Date', 'Region', 'State', 'City', 'Category', 'Sub-Category', 'Sales', 'Profit', 'Quantity']
selected_columns = st.multiselect("Choose columns to filter:", columns, default=default_columns)

if selected_columns:
    df1 = df[selected_columns]
    st.write(df1.head())
else:
    df1 = df.copy()
    st.write("No columns selected for filtering.")

###################


startDate = pd.to_datetime(df1["Order Date"]).min()
endDate = pd.to_datetime(df1["Order Date"]).max()

start_day, end_day = st.columns((2))
with start_day:
    date1 = pd.to_datetime(st.date_input("Start Date", startDate))

with end_day:
    date2 = pd.to_datetime(st.date_input("End Date", endDate))

# 설정한 기간의 데이터를 이제부터 다룬다 
df1 = df1[(df1["Order Date"] >= date1) & (df1["Order Date"] <= date2)].copy()
df1 = df1.sort_values(by="Order Date")

# 2. 사이드바에서 분석 필터를 골라서 분석을 진행한다. 
st.sidebar.header("Choose your filter: ")

# 2.1 사이드 바에 지역을 선택 
region = st.sidebar.multiselect("지역 선택", df1["Region"].unique())
if not region:
    df2 = df1.copy()
else:
    df2 = df1[df1["Region"].isin(region)]

# 2.2. 사이드 바에 주를 선택 
state = st.sidebar.multiselect("주 선택", df2['State'].unique())
if not state:
    df3 = df2.copy() 
else:
    df3 = df2[df2["State"].isin(state)]

# 2.3. 도시 선택 
city = st.sidebar.multiselect("도시 선택", df3['City'].unique())

# 모두 선택 안한경우
if not region and not state and not city:
    filtered_df = df
elif not state and not city:
    filtered_df = df[df["Region"].isin(region)]
elif not region and not city:
    filtered_df = df[df["State"].isin(state)]
elif state and city:
    filtered_df = df3[df["State"].isin(state) & df3["City"].isin(city)]
elif region and city:
    filtered_df = df3[df["Region"].isin(region) & df3["City"].isin(city)]
elif region and state:
    filtered_df = df3[df["Region"].isin(region) & df3["State"].isin(state)]
elif city:
    filtered_df = df3[df3["City"].isin(city)]
else:
    filtered_df = df3[df3["Region"].isin(region) & df3["State"].isin(state) & df3["City"].isin(city)]


################ 데이터 시각화 1.
# 시계열 분석 
st.subheader('Time Series Analysis')
# 월별 판매량을 시계열 차트를 통해 보여준다. 
filtered_df["month_year"] = filtered_df["Order Date"].dt.to_period("M")
linechart = pd.DataFrame(filtered_df.groupby(filtered_df["month_year"].dt.strftime("%Y : %b"))["Sales"].sum()).reset_index()
fig2 = px.line(linechart, x = "month_year", y="Sales", labels = {"Sales": "Amount"},height=500, width = 1000,template="gridon")
st.plotly_chart(fig2,use_container_width=True)
# 월별 판매량 tabular 데이터를 csv로 다운로드 할 수 있는 버튼을 만든다 
with st.expander("View Data of TimeSeries:"):
    st.write(linechart.T.style.background_gradient(cmap="Blues"))
    csv = linechart.to_csv(index=False).encode("utf-8")
    st.download_button('Download Data', data = csv, file_name = "TimeSeries.csv", mime ='text/csv')


# Category 열이 있음, 카테고리별 Sales를 파악해보자.
category_df = filtered_df.groupby(by = ["Category"], as_index=False)["Sales"].sum()

################ 데이터 시각화 1.
# 페이지를 2개로 나누어 
col1, col2 = st.columns(2)
# 왼쪽(첫번째 열)에는 카테고리별 판매량 
with col1:
    st.subheader("Category wise Sales")
    fig = px.bar(category_df, x = "Category", y = "Sales", 
                 text = ['${:,.2f}'.format(x) for x in category_df["Sales"]],
                 template = "seaborn")
    st.plotly_chart(fig,use_container_width=True, height = 200)
    
# 오른쪽(두번째 열)에는 지역별 판매량 
# Category별 판매량 비교 
with col2:
    st.subheader('Category wise Sales')
    fig = px.pie(filtered_df, values = "Sales", names = "Category", template = "gridon")
    fig.update_traces(text = filtered_df["Category"], textposition = "inside")
    st.plotly_chart(fig,use_container_width=True)

################ 데이터 시각화 1.
# 페이지를 2개로 나누어 
rcol1, rcol2 = st.columns(2)
Region_State_df = filtered_df.groupby(by = ["Region","State"], as_index=False)["Sales"].sum()
Region_State_df.sort_values(by=["Region", "Sales"], ascending=[True, False], inplace=True)

with rcol1:
    st.subheader("Region wise Sales")
    fig = px.pie(filtered_df, values = "Sales", names = "Region", hole = 0.5)
    fig.update_traces(text = filtered_df["Region"], textposition = "outside")
    st.plotly_chart(fig,use_container_width=True)

with rcol2:
    st.subheader("State wise Region wise Sales")
    fig = px.bar(Region_State_df, x = "Region", y = "Sales", color="State",
                 template = "seaborn")
    fig.update_layout(barmode='stack', xaxis={'categoryorder': 'total descending'})
    st.plotly_chart(fig,use_container_width=True, height = 200)


################ 데이터 시각화 4.
# Region, Category, sub-Category에 대한 TreeMap
st.subheader("Hierarchical view of Sales using TreeMap")
fig3 = px.treemap(filtered_df, path = ["Region","Category","Sub-Category"], values = "Sales",hover_data = ["Sales"],
                  color = "Sub-Category")
fig3.update_layout(width = 800, height = 650)
st.plotly_chart(fig3, use_container_width=True)

################ 데이터 시각화 5.
# 다시 페이지를 2개로 분할해서
chart1, chart2 = st.columns((2))
Segment_Category_df = filtered_df.groupby(by = ["Segment","Category"], as_index=False)["Sales"].sum()
Segment_Category_df.sort_values(by=["Category", "Sales"], ascending=[True, False], inplace=True)

# Segment별 판매량
with chart1:
    st.subheader('Segment wise Sales')
    fig = px.pie(filtered_df, values = "Sales", names = "Segment", template = "plotly_dark")
    fig.update_traces(text = filtered_df["Segment"], textposition = "inside")
    st.plotly_chart(fig,use_container_width=True)
    
# Category별 판매량 비교 
with chart2:
    st.subheader('Category wise Segment wise Sales')
    # fig = px.pie(filtered_df, values = "Sales", names = "Category", template = "gridon")
    # fig.update_traces(text = filtered_df["Category"], textposition = "inside")
    # st.plotly_chart(fig,use_container_width=True)
    
    fig = px.bar(Segment_Category_df, x = "Segment", y = "Sales", color="Category",
                 template = "seaborn")
    fig.update_layout(barmode='stack', xaxis={'categoryorder': 'total descending'})
    st.plotly_chart(fig,use_container_width=True, height = 200)
    
    
import plotly.figure_factory as ff
st.subheader(":point_right: Month wise Sub-Category Sales Summary")


with st.expander("Sub-Category Sales Summary_Table"):
    # Multiselect for Sub-Category
    sub_categories = filtered_df["Sub-Category"].unique()
    selected_sub_categories = st.multiselect("Select Sub-Categories:", sub_categories)

    if selected_sub_categories:
    # Filter DataFrame based on selected Sub-Categories
        filtered_df_sub_cat = filtered_df[filtered_df["Sub-Category"].isin(selected_sub_categories)]
    else:
        filtered_df_sub_cat = filtered_df.copy()
        
    st.markdown("Month wise sub-Category Table")
    
    # 월 이름 추출 및 순서 지정
    filtered_df_sub_cat["month"] = filtered_df_sub_cat["Order Date"].dt.month_name()
    month_order = ['January', 'February', 'March', 'April', 'May', 'June', 
                   'July', 'August', 'September', 'October', 'November', 'December']
    
    filtered_df_sub_cat['month'] = pd.Categorical(filtered_df_sub_cat['month'], categories=month_order, ordered=True)
    
    # 피벗 테이블 생성, None 값을 0으로 대체
    sub_category_Year = pd.pivot_table(data=filtered_df_sub_cat, values="Sales", index=["Sub-Category"], columns="month", fill_value=0)
    st.write(sub_category_Year.style.background_gradient(cmap="Blues"))
    
    st.markdown("Month wise Sub-Category Line Chart")
    
    # 피벗 테이블을 선 그래프용 데이터로 변환 (플랫하게 변환)
    sub_category_melted = sub_category_Year.reset_index().melt(id_vars=["Sub-Category"], value_name="Sales", var_name="month")
    
    # 선 그래프 생성
    fig = px.line(sub_category_melted, x="month", y="Sales", color="Sub-Category", markers=True, 
                  title="Monthly Sales of Selected Sub-Categories")
    
    # 월 순서 정렬 (예: January, February, ...)
    fig.update_xaxes(categoryorder='array', categoryarray=month_order)
    
    # 선 그래프 출력
    st.plotly_chart(fig, use_container_width=True)
    
# Create a scatter plot
data1 = px.scatter(filtered_df, x = "Sales", y = "Profit", size = "Quantity")
data1['layout'].update(title="Relationship between Sales and Profits using Scatter Plot.",
                       titlefont = dict(size=20),xaxis = dict(title="Sales",titlefont=dict(size=19)),
                       yaxis = dict(title = "Profit", titlefont = dict(size=19)))
st.plotly_chart(data1,use_container_width=True)



# Categorical variable visualization
st.subheader('범주형 변수 시각화')

# selected_cat_column = st.selectbox('Select a column to visualize:', filtered_df.columns)
categorical_columns = filtered_df.select_dtypes(include=['object', 'category']).columns.tolist()
selected_cat_columns = st.multiselect("Select Sub-Categories:", categorical_columns)


if selected_cat_columns:
    for selected_cat_column in selected_cat_columns:

        category_counts_df = filtered_df[selected_cat_column].value_counts().reset_index()
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


numerical_columns = filtered_df.select_dtypes(include=['number']).columns.tolist()
st.subheader('수치형 변수 시각화')

selected_num_columns = st.multiselect("Select Sub-Categories:", numerical_columns)

if selected_num_columns:
    for selected_num_column in selected_num_columns:
        
        num_category_counts_df = filtered_df[selected_num_column].value_counts().reset_index()
        num_category_counts_df.columns = [selected_num_column, 'count']
        
        st.subheader("{} 카운트".format(selected_num_column))
        fig = px.bar(num_category_counts_df, x = selected_num_column, y = "count", color=selected_num_column,
                    template = "seaborn")
        st.plotly_chart(fig,use_container_width=True, height = 200)

        
        numerical_columns.remove(selected_num_column)

# Download orginal DataSet
csv = df.to_csv(index = False).encode('utf-8')
st.download_button('Download Data', data = csv, file_name = "Data.csv",mime = "text/csv")