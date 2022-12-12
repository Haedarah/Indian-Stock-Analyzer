import numpy as np
import pandas as pd
import streamlit as st
import yfinance as yf
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import math 


months={
1:"January",
2:"February",
3:"March",
4:"April",
5:"May",
6:"June",
7:"July",
8:"August",
9:"September",
10:"October",
11:"November",
0:"December",
}


st.set_page_config(
	page_icon="chart_with_upwards_trend",
    page_title="Indian Stocks Analyzer",
    layout="wide",
)

header=st.container()
parameters=st.container()
st.write("""---""")
UpperBlock=st.container()
st.write("""---""")
MiddleBlock=st.container()
st.write("""---""")
LowerBlock=st.container()
st.write("""---""")


with header:
	col1,col2=st.columns([1,4],gap="large")

	with col1:
		st.image("Objects/logo.png",use_column_width=True)

	with col2:
		st.title("Indian Stock Market Analyzer")
		st.write("A tool which spots seasonality in Indian stocks performances.")
		st.write("---")



indian_tickers=pd.read_csv("Data/Indian_tickers_YFinance_Correct_NoIndex.csv")
names=indian_tickers[['Name','Exchange','Ticker']]



with parameters:
	col1,col2,col3=st.columns([1,1,1],gap="large")

	with col1:
		exchange=st.selectbox("Select the stock exchange you want to use:",["National Stock Exchange","Bombay Stock Exchange"])
		
		if exchange=="Bombay Stock Exchange" :
			names=names[names['Exchange']=="BSE"]
		else:
			names=names[names['Exchange']=="NSI"]

		st.write("**Number of available stocks:**",str(len(names)))

	names=names[['Name','Ticker']]
	names=names.sort_values(by=["Name"])
	names=names.reset_index(drop=True)

	with col2:
		stock=st.selectbox("Stock:",names)



with UpperBlock:
	st.subheader("Visualization")
	
	ticker=names[names['Name']==stock]['Ticker']
	ticker=str(ticker)
	ticker=ticker.split()
	data=yf.download(tickers=ticker[1],start="2013-01-01",end=datetime.now())
	data=data[["Close"]]
	data=data.reset_index()

	col1,col2,col3=st.columns([1,1,1],gap="small")
	with col1:
		st.write("**Name:** ")
		st.write("**Yahoo Finance Ticker:** ")
		st.write("**Number of Data Points Since 2013-01-01:** ")
	with col2:
		st.write(stock)
		st.write(ticker[1])
		st.write(str(len(data)))

	plotting1=go.Figure()
	plotting1.add_trace(go.Scatter(x=data['Date'],y=data['Close'],mode='lines',
		line=dict(color="blue",width=3),name="Historical Data"))
	plotting1.update_layout(title=stock+"'s Performance Since 2013",xaxis_title="Date", yaxis_title="Close/₹",height=600,font=dict(color="Brown"))

	st.plotly_chart(plotting1,use_container_width=True)



with MiddleBlock:
	month=((datetime.now().month)+1)%12
	st.subheader("Projection of ["+stock+"]'s performance during next month ("+months[month]+"), depending on the last 10 "+months[month]+"s")

	data=data.reset_index()
	new_data=data[data['Close']=="Raso"]
	
	for i in data.index:
		if data['Date'][i].month==month:
			newRow=pd.DataFrame({'Date':data['Date'][i], 'Close':data['Close'][i]},index=[i])
			new_data=pd.concat([new_data,newRow],ignore_index=True)

	new_data=new_data.drop(labels='index', axis=1)
	new_data["upper_trend"]=new_data["Close"]
	j=0
	curr_year=2013
	virtical=[]
	year=[2013]

	for i in new_data.index:
		if new_data['Date'][i].year==curr_year:
			new_data['upper_trend'][i]=j
			j=j+1
		else:
			new_data['upper_trend'][i]=0
			j=1
			curr_year=curr_year+1
			virtical.append(i)
			year.append(curr_year)
	virtical.append(len(new_data)-1)

	
	new_data=new_data.reset_index()

	plotting2=go.Figure()
	plotting2.add_vline(x=0,line_color="black",line_width=1,annotation_text=str(2013))
	plotting2.add_trace(go.Scatter(x=new_data["index"][:virtical[0]],y=new_data["Close"][:virtical[0]],mode='lines',line=dict(color="blue",width=4),name=months[month]))	
	for i in range(1,10):
		plotting2.add_vline(x=virtical[i-1],line_color="black",line_width=1,annotation_text=str(2013+i))
		plotting2.add_trace(go.Scatter(x=new_data["index"][virtical[i-1]:virtical[i]],y=new_data["Close"][virtical[i-1]:virtical[i]],mode='lines',line=dict(color="blue",width=4),name=months[month]))
	plotting2.update_layout(title=stock+" - "+months[month]+"s Performance Since 2013",xaxis_title="idx", yaxis_title="Close/₹",height=600,font=dict(color="Brown"),showlegend=False)
	st.plotly_chart(plotting2,use_container_width=True)

	mean_corr=0
	j=0
	flag=0

	for i in virtical:
		current=(new_data['Close'][j:i].corr(new_data['upper_trend'][j:i]))
		if math.isnan(current):
			flag=1
		else:
			mean_corr=mean_corr+current
		j=i


	mean_corr=mean_corr/10
	mean_corr=mean_corr*100
	mean_corr=round(mean_corr,2)

	st.write("---")
	if mean_corr>=0:
		st.markdown("<h2>According to past "+months[month]+"s performance, this stock has a "+str(mean_corr)+"%"+" chance of having an <span style='color:Green;'>upper trend</span> this "+months[month]+".",unsafe_allow_html=True)
	else:
		st.markdown("<h2>According to past "+months[month]+"s performance, this stock has a "+str((-1)*mean_corr)+"%"+" chance of having a <span style='color:Red;'>lower trend</span> this "+months[month]+".",unsafe_allow_html=True)

	if flag==1:
		st.write("*The Projection of this stock has been done using less data, or the stock itself has at least one "+months[month]+"/s where it didn't move at all.")
		st.write("As a result, the accuracy of the projection is most likely less than other stock's projections.")



with LowerBlock:
	st.subheader("The "+months[month]+"'s top performers according to the last 10 "+months[month]+"s")
	
	performance=pd.read_csv("Data/Next_January_Projection.csv")
	performance=performance.dropna()
	st.write("Only ("+str(len(performance))+") stocks have useful data in the last 10 years. From that, The most likely stocks to perform well in the next "+months[month]+" are: ")
	performance=performance.sort_values(by=['corr'],ascending=False,ignore_index=True)
	
	for i in range(5):
		
		st.write(str(i+1)+". "+performance['Name'][i])
		# st.write()
		top=yf.download(tickers=performance['Ticker'][i],start="2013-01-01",end=datetime.now())
		top=top[['Close']]
		top=top.reset_index()
		top['JAN']=top['Close']
		
		for i in top.index:
			if top['Date'][i].month==month:
				top['JAN'][i]="JAN"

		plotting3=go.Figure()
		plotting3.add_trace(go.Scatter(x=top['Date'],y=top['Close'],mode='lines',line=dict(color="blue",width=3),name="Historical Data"))
		plotting3.add_trace(go.Scatter(x=top[top['JAN']=="JAN"]['Date'],y=top[top['JAN']=="JAN"]['Close'],mode='markers',marker=dict(color="red",size=7),name="January"))
		plotting3.update_layout(xaxis_title="Date", yaxis_title="Close/₹",height=600,font=dict(color="Brown"))

		st.plotly_chart(plotting3,use_container_width=True)

	st.write("Details of the top 5 performing stocks:")
	st.table(performance.head(5))
	st.write("*The 'corr' column, refers to the correlation percentage between the stock, and an upper trend.")