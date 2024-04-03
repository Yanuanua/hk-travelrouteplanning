import streamlit as st
import folium
from streamlit_folium import st_folium
from streamlit_folium import folium_static
import pandas as pd
import openpyxl

#Method1方法
def plan_route(start_spot, total_spots, max_time, themes):
    current_spot = start_spot
    route = [current_spot]
    total_time = spots[current_spot]['time']
    visited = set([current_spot])
    visited_themes = set(spots[current_spot]['themes'])

    while len(route) < total_spots:
        remaining_spots = list(set(spots.keys()) - visited)
        if not remaining_spots:
            break
        
        if all(theme in visited_themes for theme in themes):
            next_spot = max(remaining_spots, key=lambda x: probabilities[route[-1]][x])
            next_spot_info = spots[next_spot]
            if total_time + next_spot_info['time'] <= max_time:
                route.append(next_spot)
                total_time += next_spot_info['time']
                visited_themes.update(next_spot_info['themes'])
                visited.add(next_spot)
            else:
                remaining_spots = [spot for spot in remaining_spots if spots[spot]["time"] + total_time <= max_time]
                if not remaining_spots:
                    break
                next_spot = max(remaining_spots, key=lambda x: probabilities[route[-1]][x])
                next_spot_info = spots[next_spot]
                route.append(next_spot)
                visited.add(next_spot)
                total_time += next_spot_info['time']
        else:
            for theme in themes:
                if theme not in visited_themes:
                    for spot, info in spots.items():
                        if theme in info['themes']:
                            probabilities[current_spot][spot] += 0.1
            next_spot = max(remaining_spots, key=lambda x: probabilities[route[-1]][x])
            next_spot_info = spots[next_spot]
            if total_time + next_spot_info['time'] <= max_time:
                route.append(next_spot)
                total_time += next_spot_info['time']
                visited_themes.update(next_spot_info['themes'])
                visited.add(next_spot)
            else:
                remaining_spots = [spot for spot in remaining_spots if spots[spot]["time"] + total_time <= max_time]
                if not remaining_spots:
                    break
                next_spot = max(remaining_spots, key=lambda x: probabilities[route[-1]][x])
                next_spot_info = spots[next_spot]
                route.append(next_spot)
                visited.add(next_spot)
                total_time += next_spot_info['time']
        
        current_spot = next_spot
    
    return route, total_time

#获取Method1数据
df1 = pd.read_excel("Route Probabilities.xlsx", sheet_name='Sheet1')
spots = {}
probabilities = {}
for index, row in df1.iterrows():
    themes = [theme.strip() for theme in row['themes'].split(',')]
    spot_data = {
        'latitude': row['latitude'],
        'longitude': row['longitude'],
        'time': int(row['time']),
        'cluster': str(row['cluster']),
        'themes': themes
    }
    spots[row['spot_name']] = spot_data
for index, row in df1.iterrows():
    probs = {key: row[key] for key in row.index[6:38]}  # 提取从第7列到第38列的概率数据
    probabilities[row['spot_name']] = probs

#用户界面
st.title('Plan Your HK Travel Route ^_^')
selected_option = st.selectbox('Please choose one method for travel route planning.', ['Method 1: For travelers who have time constraints and rely on historical experience.', 'Method 2: For travelers who have time to spare and love to explore new spots.'])


if selected_option == 'Method 1: For travelers who have time constraints and rely on historical experience.':
    st.subheader('Method 1')

    df2 = pd.read_excel("Spot Information.xlsx", sheet_name='Sheet1')
    Spots_Information = {}
    for index, row in df2.iterrows():
        themes = [theme.strip() for theme in row['theme'].split(',')]
        spot_data = {
            'latitude': row['latitude'],
            'longitude': row['longitude'],
            'themes': themes
        }
        Spots_Information[row['spot_name']] = spot_data

    m = folium.Map(location=[22.28056, 114.17222], zoom_start=12)
    for spot_name, info in Spots_Information.items():
        folium.Marker(
            location=[info["latitude"], info["longitude"]],
            tooltip=f"{spot_name} for {info['themes']}",
            icon=folium.Icon(icon='cloud')
        ).add_to(m)
    #points=[(22.3203648,114.169773),(22.2823565,114.1886969)]
    #folium.PolyLine(points, color="blue", weight=2.5, opacity=1).add_to(m)
    folium_static(m)


    start_spot = st.selectbox('Please choose your start spot.', list(spots.keys()))
    total_spots = st.slider('Please choose the number of spots you would like to visit.', min_value=1, max_value=len(spots))
    max_time = st.slider('Please choose the time you expect to travel.', min_value=1, max_value=4050)
    themes = st.multiselect('Please choose the theme\(s\) you are interested in \(more than one can be chosen\).', list(set(theme for spot in spots.values() for theme in spot['themes'])))

    if st.button('Generate your travel route!'):
        result = plan_route(start_spot, total_spots, max_time, themes)
        st.balloons()
        st.write(f"Route: {result[0]}")
        st.write(f"Total Time: {result[1]}")
else:
    st.subheader('Method 2')

