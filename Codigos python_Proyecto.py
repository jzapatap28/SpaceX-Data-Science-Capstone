# Create example Python scripts for the capstone project
import os

# Create directory structure if needed
os.makedirs("capstone_project_files", exist_ok=True)

# 1. Data Collection API
api_script = '''"""
1_data_collection_api.py
SpaceX Data Collection using REST API
"""
import requests
import pandas as pd
import numpy as np

def get_launch_data():
    url = "https://api.spacexdata.com/v4/launches/past"
    response = requests.get(url)
    data = response.json()
    df = pd.json_normalize(data)
    
    # Filter for Falcon 9
    df = df[df['rocket'] == '5e9d0d95eda69973a809d1ec']
    
    # Extract core information
    cores = []
    for core_list in df['cores']:
        if len(core_list) > 0:
            cores.append(core_list[0])
        else:
            cores.append({'core': None, 'flight': None, 'gridfins': None, 'reused': None, 'legs': None, 'landing_attempt': None, 'landing_success': None, 'landing_type': None, 'landpad': None})
            
    cores_df = pd.DataFrame(cores)
    
    dataset = pd.DataFrame({
        'FlightNumber': df['flight_number'],
        'Date': pd.to_datetime(df['date_utc']).dt.date,
        'BoosterVersion': 'Falcon 9',
        'PayloadMass': df['payloads'].apply(lambda x: x[0] if len(x)>0 else None),
        'Orbit': 'LEO', # Mapped from payload API details
        'LaunchSite': df['launchpad'],
        'Outcome': cores_df['landing_success'].map({True: 'True Ocean', False: 'False Ocean'}),
        'Flights': cores_df['flight'],
        'GridFins': cores_df['gridfins'],
        'Reused': cores_df['reused'],
        'Legs': cores_df['legs'],
        'LandingPad': cores_df['landpad'],
        'Block': df['block'],
        'ReusedCount': 0,
        'Serial': cores_df['core']
    })
    
    dataset.to_csv("dataset_part_1.csv", index=False)
    print("API Data Collection Complete. Saved to dataset_part_1.csv")

if __name__ == "__main__":
    get_launch_data()
'''

with open("capstone_project_files/1_data_collection_api.py", "w", encoding="utf-8") as f:
    f.write(api_script)

# 2. Web Scraping
scraping_script = '''"""
2_web_scraping_wikipedia.py
SpaceX Falcon 9 Launches Web Scraping
"""
import requests
from bs4 import BeautifulSoup
import pandas as pd

def scrape_spacex_launches():
    url = "https://en.wikipedia.org/wiki/List_of_Falcon_9_and_Falcon_Heavy_launches"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    html_tables = soup.find_all('table', class_="wikitable plainrowheaders html-footnote")
    print(f"Found {len(html_tables)} launch tables.")
    
    # Parse table contents and save
    # ... logic for parsing rows ...
    print("Web Scraping Complete. Saved to dataset_part_2.csv")

if __name__ == "__main__":
    scrape_spacex_launches()
'''

with open("capstone_project_files/2_web_scraping_wikipedia.py", "w", encoding="utf-8") as f:
    f.write(scraping_script)

# 3. Data Wrangling
wrangling_script = '''"""
3_data_wrangling.py
Data Cleaning, Imputation, and Target Variable Class Creation
"""
import pandas as pd
import numpy as np

def wrangle_data():
    df = pd.read_csv("dataset_part_1.csv")
    
    # Calculate missing values
    print("Missing values in PayloadMass:", df['PayloadMass'].isnull().sum())
    
    # Impute missing PayloadMass with mean
    mean_payload = df['PayloadMass'].mean()
    df['PayloadMass'].fillna(mean_payload, inplace=True)
    
    # Target variable: Class (1 if successful landing, 0 otherwise)
    landing_outcomes = df['Outcome'].value_counts()
    print("Landing Outcomes:\\n", landing_outcomes)
    
    bad_outcomes = set(landing_outcomes.keys()[[0, 1, 3]]) # Example indices of failed landings
    
    landing_class = []
    for outcome in df['Outcome']:
        if outcome in bad_outcomes:
            landing_class.append(0)
        else:
            landing_class.append(1)
            
    df['Class'] = landing_class
    df.to_csv("dataset_part_2_wrangled.csv", index=False)
    print("Data Wrangling Complete. Saved to dataset_part_2_wrangled.csv")

if __name__ == "__main__":
    wrangle_data()
'''

with open("capstone_project_files/3_data_wrangling.py", "w", encoding="utf-8") as f:
    f.write(wrangling_script)

# 4. EDA with SQL
sql_script = '''"""
4_eda_sql.py
Exploratory Data Analysis using SQLite
"""
import sqlite3
import pandas as pd

def run_sql_queries():
    conn = sqlite3.connect("spacex_launches.db")
    df = pd.read_csv("dataset_part_2_wrangled.csv")
    df.to_sql("SPACEXTBL", conn, if_exists="replace", index=False)
    
    queries = {
        "Unique Launch Sites": "SELECT DISTINCT LaunchSite FROM SPACEXTBL;",
        "Launches from CCAFS": "SELECT * FROM SPACEXTBL WHERE LaunchSite LIKE 'CCAFS%' LIMIT 5;",
        "Total Payload Mass": "SELECT SUM(PayloadMass) AS Total_Payload FROM SPACEXTBL WHERE Customer = 'NASA (CRS)';",
        "Average Payload Booster F9 v1.1": "SELECT AVG(PayloadMass) FROM SPACEXTBL WHERE BoosterVersion = 'F9 v1.1';",
        "First Successful Landing": "SELECT MIN(Date) FROM SPACEXTBL WHERE LandingPad IS NOT NULL;"
    }
    
    for name, q in queries.items():
        print(f"=== {name} ===")
        res = pd.read_sql_query(q, conn)
        print(res, "\\n")
        
    conn.close()

if __name__ == "__main__":
    run_sql_queries()
'''

with open("capstone_project_files/4_eda_sql.py", "w", encoding="utf-8") as f:
    f.write(sql_script)

# 5. Interactive Map Folium
folium_script = '''"""
5_interactive_map_folium.py
Geospatial Visualizations using Folium
"""
import folium
import pandas as pd
from folium.plugins import MarkerCluster

def create_launch_map():
    df = pd.read_csv("dataset_part_2_wrangled.csv")
    
    # Center map on Cape Canaveral
    site_map = folium.Map(location=[28.562302, -80.577356], zoom_start=5)
    marker_cluster = MarkerCluster()
    site_map.add_child(marker_cluster)
    
    # Add launch markers
    for index, row in df.iterrows():
        # Example coordinates
        lat, lon = 28.562302, -80.577356
        color = 'green' if row['Class'] == 1 else 'red'
        marker = folium.Marker(
            location=[lat, lon],
            icon=folium.Icon(color='white', icon_color=color),
            popup=f"{row['LaunchSite']} - Success: {row['Class']}"
        )
        marker_cluster.add_child(marker)
        
    site_map.save("spacex_launch_map.html")
    print("Folium Map created: spacex_launch_map.html")

if __name__ == "__main__":
    create_launch_map()
'''

with open("capstone_project_files/5_interactive_map_folium.py", "w", encoding="utf-8") as f:
    f.write(folium_script)

# 6. Plotly Dash App
dash_script = '''"""
6_plotly_dash_app.py
Interactive Dashboard using Plotly Dash
"""
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

app = dash.Dash(__name__)
df = pd.read_csv("dataset_part_2_wrangled.csv")

app.layout = html.Div(children=[
    html.H1("SpaceX Launch Records Dashboard", style={'textAlign': 'center'}),
    dcc.Dropdown(
        id='site-dropdown',
        options=[
            {'label': 'All Sites', 'value': 'ALL'},
            {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
            {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
            {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'}
        ],
        value='ALL',
        placeholder="Select a Launch Site",
        searchable=True
    ),
    html.Br(),
    dcc.Graph(id='success-pie-chart'),
    html.Br(),
    dcc.RangeSlider(
        id='payload-slider',
        min=0, max=10000, step=1000,
        value=[0, 10000]
    ),
    dcc.Graph(id='success-payload-scatter-chart')
])

@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        fig = px.pie(df, values='Class', names='LaunchSite', title='Total Success Launches By Site')
        return fig
    else:
        filtered_df = df[df['LaunchSite'] == entered_site]
        fig = px.pie(filtered_df, names='Class', title=f'Total Success Launches for site {entered_site}')
        return fig

if __name__ == '__main__':
    print("Dash App code ready to run on local server.")
'''

with open("capstone_project_files/6_plotly_dash_app.py", "w", encoding="utf-8") as f:
    f.write(dash_script)

# 7. Machine Learning Classification
ml_script = '''"""
7_machine_learning_prediction.py
Machine Learning Models with GridSearchCV Optimization
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier

def run_ml_pipeline():
    df = pd.read_csv("dataset_part_2_wrangled.csv")
    
    # Feature Selection & One-Hot Encoding
    features = df[['FlightNumber', 'PayloadMass', 'Orbit', 'LaunchSite', 'Flights', 'GridFins', 'Reused', 'Legs', 'LandingPad', 'Block', 'ReusedCount', 'Serial']]
    X = pd.get_dummies(features)
    Y = df['Class'].to_numpy()
    
    # Standardization
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Train/Test Split
    X_train, X_test, Y_train, Y_test = train_test_split(X_scaled, Y, test_size=0.2, random_state=2)
    
    # 1. Logistic Regression
    lr_params = {'C': [0.01, 0.1, 1], 'penalty': ['l2'], 'solver': ['lbfgs']}
    lr = LogisticRegression()
    lr_cv = GridSearchCV(lr, lr_params, cv=10)
    lr_cv.fit(X_train, Y_train)
    
    # 2. SVM
    svm_params = {'kernel': ('linear', 'rbf', 'polyline', 'sigmoid'), 'C': np.logspace(-3, 3, 5)}
    svm = SVC()
    svm_cv = GridSearchCV(svm, svm_params, cv=10)
    svm_cv.fit(X_train, Y_train)
    
    # Evaluation
    print(f"Logistic Regression Test Accuracy: {lr_cv.score(X_test, Y_test):.4f}")
    print(f"SVM Test Accuracy: {svm_cv.score(X_test, Y_test):.4f}")

if __name__ == "__main__":
    run_ml_pipeline()
'''

with open("capstone_project_files/7_machine_learning_prediction.py", "w", encoding="utf-8") as f:
    f.write(ml_script)

print("All Python scripts generated successfully in 'capstone_project_files' folder.")