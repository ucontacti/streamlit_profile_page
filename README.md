# Streamlit Gallery for various project
This repo includes a colelction of different topics that I thought are cool and fast to implement. I hope you can find these dashboards useful. 
Web app is available in this [link](https://data-chamber.de/).
## Running locally
<p>You need to place your Tweepy tokens in "config/tweepy_token.py"</p>
<p>Also you need to download and store US Accident database into  "data/US_Accidents_Dec21_updated.csv"</p>

* Using Docker:
    ```
    docker build -t streamlit_dashboard . 
    docker docker run -p 8501:8501 streamlit_dashboard
    ```

* Using Python(Make sure you are using python 3.9 or above):
    ```
    pip install -r requirements.txt
    streamlit run 1_🏠_Homepage.py 
    ```


## Twitter hot topics SentimenT Analysis
![](/demo/sentiment.PNG)

### US Incident 2016-2021 demo
![](/demo/demo_us_incident.gif)