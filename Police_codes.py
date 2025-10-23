import streamlit as st
import pandas as pd
import pymysql
def create_connection():
    try:
        connection =pymysql.connect(
            host="localhost",
            user="root",
            password="Ashwitha",  #sql login password
            database="secure_check_logs",
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection 
    except Exception as e:
        st.error(f"Database Connection error:{e}")
        return None
# fetch data from database
def fetch_data(query):
    connection=create_connection()
    if connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                result=cursor.fetchall()
                df=pd.DataFrame(result)
                return df
        finally:
            connection.close()
    else:
        return pd.DataFrame()
    
#streamlit code
st.set_page_config(page_title="Securecheck Police Files",layout="wide") 
st.title("🔒Securecheck- Police Check digital ledger")
st.markdown("⏱️Real-time monitoring and insights for law enforcement")
st.header("👮‍♂️Police logs overview")
query= "select * from traffic_stops"
data= fetch_data(query)
st.dataframe(data,use_container_width=True)


#metrics
st.header("✅ Key metrics")
col1,col2,col3,col4,col5=st.columns(5)

with col1:
    total_stops=data.shape[0]
    st.metric("Total police stops",total_stops)
with col2:
    arrests=data[data['stop_outcome'].str.contains("Arrest",case=False,na=False)].shape[0]
    st.metric("Total arrests",arrests)   
with col3:
    warnings=data[data['stop_outcome'].str.contains("warning",case=False,na=False)].shape[0]
    st.metric("Total warnings",warnings)
with col4:
    drugs_related= data[data['drugs_related_stop']==1].shape[0]
    st.metric("Drug related stops",drugs_related)
with col5:
    search_conducted=data[data['search_conducted']==1].shape[0]
    st.metric("Total search conducted",search_conducted)           

#Selectbox queries:
st.header("💡Advanced Insights")
selected_query=st.selectbox("▶️Select a query to run",[
    "What are the top 10 vehicle_Number involved in drug-related stops?",
    "Which vehicles were most frequently searched?",
    "Which driver age group had the highest arrest rate?",
    "What is the gender distribution of drivers stopped in each country?",
    "Which race and gender combination has the highest search rate?",
    "What time of day sees the most traffic stops?",
    "What is the average stop duration for different violations?",
    "Are stops during the night more likely to lead to arrests?",
    "Which violations are most associated with searches or arrests?",
    "Which violations are most common among younger drivers (<25)?",
    "Is there a violation that rarely results in search or arrest?",
    "Which countries report the highest rate of drug-related stops?",
    "What is the arrest rate by country and violation?",
    "Which country has the most stops with search conducted?",
    "Yearly Breakdown of Stops and Arrests by Country",
    "Driver Violation Trends Based on Age and Race",
    "Time Period Analysis of Number of Stops by Year,Month, Hour of the Day",
    "Violations with High Search and Arrest Rates",
    "Driver Demographics by Country (Age, Gender, and Race)",
    "Top 5 Violations with Highest Arrest Rates"
])
#Adding queries for above questions
query_map= {
    "What are the top 10 vehicle_Number involved in drug-related stops?":"SELECT vehicle_number,COUNT(*) AS count from traffic_stops where drugs_related_stop=True GROUP BY vehicle_number ORDER BY count DESC LIMIT 10",
    "Which vehicles were most frequently searched?":"select vehicle_number,COUNT(*) AS count from traffic_stops where search_conducted=True GROUP BY vehicle_number ORDER BY count DESC limit 10",
    "Which driver age group had the highest arrest rate?":"SELECT CASE when driver_age <25 then '<25' when driver_age between 25 and 40 then '25-40' when driver_age between 41 and 60 then '41-60' else '>40' end AS total_range ,count(*) AS total_stops,sum(case when is_arrested=1 then 1 else 0 end)AS total_arrests,round(sum(case when is_arrested=1 then 1 else 0 end)/count(*)*100,2)AS percent_rate from traffic_stops group by driver_age order by percent_rate desc limit 3",
    "What is the gender distribution of drivers stopped in each country?":"select country_name,driver_gender,COUNT(*) AS count FROM traffic_stops GROUP BY country_name, driver_gender ORDER BY country_name, COUNT(*) DESC",
    "Which race and gender combination has the highest search rate?":"SELECT driver_race,driver_gender,COUNT(*) AS search_count FROM traffic_stops WHERE search_conducted=True GROUP BY driver_race, driver_gender ORDER BY search_count DESC LIMIT 1",
    "What time of day sees the most traffic stops?":" SELECT HOUR(timestamp) AS hour_of_day, COUNT(*) AS total_stops FROM traffic_stops GROUP BY hour_of_day ORDER BY total_stops DESC LIMIT 1",
    "What is the average stop duration for different violations?":"SELECT violation,avg(stop_duration)AS average_stop_duration from traffic_stops group by violation order by average_stop_duration desc",
    "Are stops during the night more likely to lead to arrests?":"SELECT CASE WHEN HOUR(timestamp) BETWEEN 20 AND 23 OR HOUR(timestamp) BETWEEN 0 AND 5 THEN 'Night' ELSE 'Day' END AS time_of_day,COUNT(*) AS count,SUM(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END) AS total_arrests,ROUND(SUM(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS arrest_rate_percent FROM traffic_stops GROUP BY time_of_day ORDER BY arrest_rate_percent DESC",
    "Which violations are most associated with searches or arrests?":"SELECT violation,sum(case when search_conducted=True then 1 else 0 end) AS searches,round(sum(case when search_conducted=True then 1 else 0 end)/count(*)*100,2)AS percent_rate FROM traffic_stops group by violation order by percent_rate desc",
    "Which violations are most common among younger drivers (<25)?":"SELECT violation,count(*)AS count FROM traffic_stops where driver_age<25 group by violation order by count desc",
    "Is there a violation that rarely results in search or arrest?":"SELECT violation,COUNT(*)AS total_stops,sum(case when search_conducted=True then 1 else 0 end)AS total_searches,sum(case when is_arrested=True then 1 else 0 end)AS total_arrests FROM traffic_stops group by violation order by total_searches,total_arrests ASC",
    "Which countries report the highest rate of drug-related stops?":"SELECT country_name,count(*)AS count FROM traffic_stops where drugs_related_stop=True group by country_name order by count DESC limit 2",
    "What is the arrest rate by country and violation?":"SELECT country_name,violation,count(*)AS arrest_count,round(sum(case when is_arrested=True then 1 else 0 end)/count(*)*100,2)AS arrest_rate from traffic_stops group by country_name,violation order by arrest_rate desc",
    "Which country has the most stops with search conducted?":"SELECT country_name,count(*)AS count from traffic_stops where search_conducted=True group by country_name order by count desc limit 1",
    "Yearly Breakdown of Stops and Arrests by Country":"WITH yearly_stats AS (SELECT country_name,YEAR(timestamp) AS stop_year,COUNT(*) AS total_stops,SUM(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END) AS total_arrests FROM traffic_stops GROUP BY country_name, YEAR(timestamp)) SELECT country_name,stop_year,total_stops,total_arrests,ROUND(total_arrests / total_stops * 100, 2) AS arrest_rate,SUM(total_stops) OVER (PARTITION BY country_name ORDER BY stop_year) AS cumulative_stops,SUM(total_arrests) OVER (PARTITION BY country_name ORDER BY stop_year) AS cumulative_arrests,ROUND(SUM(total_arrests) OVER (PARTITION BY country_name ORDER BY stop_year) /SUM(total_stops) OVER (PARTITION BY country_name ORDER BY stop_year) * 100,2) AS cumulative_arrest_rate FROM yearly_stats ORDER BY country_name, stop_year",
    "Driver Violation Trends Based on Age and Race":"SELECT v.driver_race,v.age_group,v.violation,v.violation_count,ROUND(v.violation_count * 100.0 / t.total_by_race_age,2) AS violation_percentage FROM(SELECT driver_race,CASE WHEN driver_age < 20 THEN 'Under 20' WHEN driver_age BETWEEN 20 AND 29 THEN '20-29' WHEN driver_age BETWEEN 30 AND 39 THEN '30-39' WHEN driver_age BETWEEN 40 AND 49 THEN '40-49' WHEN driver_age BETWEEN 50 AND 59 THEN '50-59' ELSE '60+' END AS age_group,violation,COUNT(*) AS violation_count FROM traffic_stops GROUP BY driver_race, age_group, violation) AS v JOIN(SELECT driver_race,CASE WHEN driver_age < 20 THEN 'Under 20' WHEN driver_age BETWEEN 20 AND 29 THEN '20-29' WHEN driver_age BETWEEN 30 AND 39 THEN '30-39' WHEN driver_age BETWEEN 40 AND 49 THEN '40-49' WHEN driver_age BETWEEN 50 AND 59 THEN '50-59' ELSE '60+' END AS age_group, COUNT(*) AS total_by_race_age FROM traffic_stops GROUP BY driver_race, age_group) AS t ON v.driver_race = t.driver_race AND v.age_group = t.age_group ORDER BY v.driver_race, v.age_group, v.violation_count DESC",
    "Time Period Analysis of Number of Stops by Year,Month, Hour of the Day":"SELECT year(timestamp) AS year,month(timestamp)AS month,hour(timestamp) AS hour_of_day,count(*) AS total_stops FROM traffic_stops group by  year(timestamp),month(timestamp),hour(timestamp) order by year(timestamp),month(timestamp),hour(timestamp) ASC",
    "Violations with High Search and Arrest Rates":"SELECT violation,count(*) AS count,sum(case when search_conducted=True then 1 else 0 end)AS Total_searched,sum(case when is_arrested=True then 1 else 0 end)AS total_arrests,round(sum(case when search_conducted=True then 1 else 0 end)/count(*)*100,2) AS percent_rate_searched,round(sum(case when is_arrested =True then 1 else 0 end)/count(*)*100,2)AS percent_rate_arrests from traffic_stops group by violation order by (percent_rate_searched + percent_rate_arrests) desc",
    "Driver Demographics by Country (Age, Gender, and Race)":"SELECT country_name,driver_age,driver_gender,driver_race, count(*) AS driver_count from traffic_stops group by country_name,driver_age,driver_gender,driver_race order by driver_count desc",
    "Top 5 Violations with Highest Arrest Rates":"SELECT violation,count(*) AS count,sum(case when is_arrested=True then 1 else 0 end) AS total_arrest,round(sum(case when is_arrested=True then 1 else 0 end)/count(*)*100,2) AS percent_rate from traffic_stops group by violation order by percent_rate desc"
    } 
if st.button("🗄️Run Query"):
    result=fetch_data(query_map[selected_query])
    if not result.empty:
        st.write(result)
    else:
        st.warning("No results found for the resulted query.") 

st.markdown("---")
st.markdown("🛡️Reliable Insights, Smarter Policing. — SecureCheck")
st.header("🔍 Smarter Searches, Natural Results — SecureCheck")


st.markdown("Fill in the details below to get a prediction of the stop outcome based on existing data.")


st.header("📝 Add New Police Log & Predict Outcome and Violation")   
# Input form for all fields   
with st.form("new_log_form"):
    timestamp_date = st.date_input("timestamp")
    timestamp_time = st.time_input("timestamp")
    county_name = st.text_input("County Name")
    driver_gender = st.selectbox("Driver Gender", ["male", "female"])
    driver_age = st.number_input("Driver Age", min_value=16, max_value=100, value=27)
    driver_race = st.text_input("Driver Race")
    search_conducted = st.selectbox("Was a Search Conducted?", ["0", "1"])
    search_type = st.text_input("Search Type")
    drugs_related_stop = st.selectbox("Was it Drug Related?", ["0", "1"])
    stop_duration = st.selectbox("Stop Duration", data['stop_duration'].dropna().unique())
    vehicle_number = st.text_input("Vehicle Number")
    #timestamp = pd.Timestamp.now()

    submitted = st.form_submit_button("Predict Stop Outcome & Violation")    
    if submitted:
        # Filter data for prediction
        filtered_data = data[
            (data['driver_gender'] == driver_gender) &
            (data['driver_age'] == driver_age) &
            (data['search_conducted'] == int(search_conducted)) &
            (data['stop_duration'] == stop_duration) &
            (data['drugs_related_stop'] == int(drugs_related_stop))
        ]

        # Predict stop_outcome
        if not filtered_data.empty:
            predicted_outcome = filtered_data['stop_outcome'].mode()[0]
            predicted_violation = filtered_data['violation'].mode()[0]
        else:
            predicted_outcome = "warning"  # Default fallback
            predicted_violation = "speeding"  # Default fallback 

        # Natural language summary
        search_text = "A search was conducted" if int(search_conducted) else "No search was conducted"
        drug_text = "was drug-related" if int(drugs_related_stop) else "was not drug-related"

        st.markdown(f"""
        🚔 **Prediction Summary**

        - **Predicted Violation:** {predicted_violation}
        - **Predicted Stop Outcome:** {predicted_outcome}

        🗒️ A {driver_age}-year-old {driver_gender} driver in {county_name} was stopped at {timestamp_time} on {timestamp_date}.  
        {search_text}, and the stop {drug_text}.  
        Stop duration: **{stop_duration}**.
        Vehicle Number: **{vehicle_number}**.
        """)    