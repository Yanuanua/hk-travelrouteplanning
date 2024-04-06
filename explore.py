import streamlit as st
import folium
from streamlit_folium import st_folium
from streamlit_folium import folium_static
import pandas as pd
import openpyxl
import pandas as pd
from geopy.geocoders import GoogleV3
import googlemaps
from datetime import datetime
from sys import maxsize  
from itertools import permutations

#数据集
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
        'spot_pro': float(row['spot_pro']),
        'themes': themes
    }
    spots[row['spot_name']] = spot_data
for index, row in df1.iterrows():
    probs = {key: row[key] for key in row.index[7:39]}
    probabilities[row['spot_name']] = probs
df1_1 = pd.read_excel("Traffic_Method1.xlsx", sheet_name='Sheet1')
traffic_m1 = {}
for index, row in df1_1.iterrows():
    traf = {key: round(row[key]) for key in row.index[1:33]}
    traffic_m1[row['spot_name']] = traf
df_2 = pd.read_excel('Spot Information_2.xlsx')

#转移概率地标概率都不为0
def route_method1(start_spot, total_spots, max_time, themes, ratio): #0<=ratio<=1 转移概率的ratio     
    if start_spot == None:
        current_spot = random.choice(list(spots.keys()))
    else:
        current_spot = start_spot
    route = [current_spot]
    total_time = spots[current_spot]['time']
    visited_clusters = set([spots[current_spot]["cluster"]])
    visited_themes = set(spots[current_spot]['themes'])

    while len(route) < total_spots:
        remaining_spots = [spot for spot in list(set(spots.keys())) if spots[spot]["cluster"] not in visited_clusters]
        if not remaining_spots:
            break
        
        if all(theme in visited_themes for theme in themes):
            next_spot = max(remaining_spots, key=lambda x: ratio*probabilities[route[-1]][x] + (1-ratio)*spots[x]['spot_pro'])
            next_spot_info = spots[next_spot]
            if total_time + next_spot_info['time'] + traffic_m1[current_spot][next_spot] <= max_time:
                route.append(next_spot)
                total_time += next_spot_info['time']
                total_time += traffic_m1[current_spot][next_spot]
                visited_themes.update(next_spot_info['themes'])
                visited_clusters.add(next_spot_info["cluster"])
            else:
                remaining_spots = [spot for spot in remaining_spots if spots[spot]["time"] + total_time + 30 <= max_time]
                if not remaining_spots:
                    break
                next_spot = max(remaining_spots, key=lambda x: ratio*probabilities[route[-1]][x] + (1-ratio)*spots[x]['spot_pro'])
                next_spot_info = spots[next_spot]
                route.append(next_spot)
                visited_clusters.add(next_spot_info["cluster"])
                total_time += next_spot_info['time']
                total_time += traffic_m1[current_spot][next_spot]
        else:
            for theme in themes:
                if theme not in visited_themes:
                    for spot, info in spots.items():
                        if theme in info['themes']:
                            probabilities[current_spot][spot] *= 1.4
            next_spot = max(remaining_spots, key=lambda x: ratio*probabilities[route[-1]][x] + (1-ratio)*spots[x]['spot_pro'])
            next_spot_info = spots[next_spot]
            if total_time + next_spot_info['time'] + traffic_m1[current_spot][next_spot] <= max_time:
                route.append(next_spot)
                total_time += next_spot_info['time']
                total_time += traffic_m1[current_spot][next_spot]
                visited_themes.update(next_spot_info['themes'])
                visited_clusters.add(next_spot_info["cluster"])
            else:
                remaining_spots = [spot for spot in remaining_spots if spots[spot]["time"] + total_time + 30 <= max_time]
                if not remaining_spots:
                    break
                next_spot = max(remaining_spots, key=lambda x: ratio*probabilities[route[-1]][x] + (1-ratio)*spots[x]['spot_pro'])
                next_spot_info = spots[next_spot]
                route.append(next_spot)
                visited_clusters.add(next_spot_info["cluster"])
                total_time += next_spot_info['time']
                total_time += traffic_m1[current_spot][next_spot]
        
        current_spot = next_spot
    
    return route, total_time

#转移概率为0
def route_method2(start_point, spots_num, themes, themes_num):
    filtered_data = []
    all_spots = set()
    for i in range(len(themes), 0, -1):
        filtered = df1[df1['themes'].astype(str).apply(lambda x: sum(theme in x for theme in themes) >= i)]
        filtered = filtered[~filtered['spot_name'].isin(all_spots)]
        all_spots.update(filtered['spot_name'])
        filtered_data.append(filtered)
    combined_df = pd.concat(filtered_data)

    combined_df['themes_count'] = combined_df['themes'].apply(lambda x: sum(theme in x for theme in themes))
    sorted_df = combined_df.sort_values(by=['themes_count', 'spot_pro'], ascending=[False, False])
    top_spots = sorted_df['spot_name'].head(themes_num).tolist()
    rows_count = len(top_spots)

    if spots_num > themes_num:
        filtered_df = df1[~df1['spot_name'].isin(top_spots)]
        sorted_df = filtered_df.sort_values(by='spot_pro', ascending=False)
        top_spots1 = sorted_df['spot_name'].head(spots_num - rows_count).tolist()
    visited_spots = top_spots + top_spots1
    route = [start_point] + visited_spots
    total_stay_time = df1[df1['spot_name'].isin(route)]['time'].sum()
        
    geolocator = GoogleV3(api_key='AIzaSyD7dw8EQZ0YN-Znw4ccEB4K4uakw0Cj2DM')
    gmaps = googlemaps.Client(key='AIzaSyD7dw8EQZ0YN-Znw4ccEB4K4uakw0Cj2DM')
    coordinate_start = geolocator.geocode(start_point)
    locations = [(coordinate_start.latitude, coordinate_start.longitude)]
    coordinates = {row['spot_name']: (row['latitude'], row['longitude']) for index, row in df1.iterrows() if row['spot_name'] in visited_spots}
    coordinates_info = [coordinates[key] for key in visited_spots]
    locations.extend(coordinates_info)

    matrix = [[0 for _ in range(spots_num + 1)] for _ in range(spots_num + 1)]
    for i in range(spots_num + 1):
        for j in range(spots_num + 1):
            if i != j:
                origin = locations[i]
                destination = locations[j]
                directions_result = gmaps.directions(origin, destination, mode="transit", departure_time=datetime.now())
                duration_in_traffic = directions_result[0]['legs'][0]['duration']['value'] / 60  # 转换为分钟
                matrix[i][j] = duration_in_traffic
    
    graph = matrix 
    vertex = {}
    for index, value in enumerate(route):
        vertex[index] = value
    min_path_weight = maxsize
    next_permutation=permutations(list(vertex.keys())[1:])
    min_path_order = None
    for i in next_permutation:
        current_pathweight = 0 
        k = 0 
        for j in i:  
            current_pathweight += matrix[k][j]  
            k = j  
        current_pathweight += matrix[k][0]  

        if current_pathweight < min_path_weight:
            min_path_weight = current_pathweight
            min_path_order = [0] + list(i) + [0]
    
    min_path = []
    for order in min_path_order:
        min_path.append(vertex[order])
    total_duration = 0
    for i in range(len(min_path) - 1):
        origin_spot = min_path[i]
        destination_spot = min_path[i + 1]
        origin_index = route.index(origin_spot)
        destination_index = route.index(destination_spot)
        duration_in_traffic = matrix[origin_index][destination_index]
        total_duration += duration_in_traffic
    total_time = round(total_stay_time+total_duration)

    return min_path, total_time, coordinate_start

#不依赖转移概率和地表概率
def route_method3(start_point, themes, total_spots, spots=spots): #必须输入start point 酒店/关口
    current_spot = start_point
    route = [current_spot]
    selectspots = []
    for spot in list(set(spots.keys())):
        for theme in spots[spot]['themes']:
            if theme in themes:
                selectspots.append(spot)
    print(selectspots)
    next_spot = random.choice(selectspots)
    current_spot = next_spot
    total_time = spots[current_spot]['time']
    visited_spots = [current_spot]
    visited_themes = set(spots[current_spot]['themes'])
    route.append(current_spot)

    while len(route)-1 < total_spots:
        remaining_spots = [spot for spot in list(set(spots.keys())) if spot not in visited_spots]
        if not remaining_spots:
            break
        
        if all(theme in visited_themes for theme in themes):
            next_spot = random.choice(remaining_spots)
            next_spot_info = spots[next_spot]
            route.append(next_spot)
            total_time += next_spot_info['time']
            total_time += traffic_m1[current_spot][next_spot]
            visited_spots.append(next_spot)
            visited_themes.update(next_spot_info['themes'])
        else:
            for theme in themes:
                if theme not in visited_themes:
                    for spot in list(set(spots.keys())):
                        if spot not in visited_spots:
                            for theme in spots[spot]['themes']:
                                if theme in themes:
                                    selectspots = []
                                    selectspots.append(spot)
                                    print(selectspots)
            next_spot = random.choice(selectspots)
            print(next_spot)
            next_spot_info = spots[next_spot]
            route.append(next_spot)
            total_time += next_spot_info['time']
            total_time += traffic_m1[current_spot][next_spot]
            visited_spots.append(next_spot)
            visited_themes.update(next_spot_info['themes'])
        
        current_spot = next_spot
    print(route)

    geolocator = GoogleV3(api_key='AIzaSyD7dw8EQZ0YN-Znw4ccEB4K4uakw0Cj2DM')
    gmaps = googlemaps.Client(key='AIzaSyD7dw8EQZ0YN-Znw4ccEB4K4uakw0Cj2DM')
    coordinate_start = geolocator.geocode(start_point)
    locations = [(coordinate_start.latitude, coordinate_start.longitude)]
    print(visited_spots)
    coordinates = {row['spot_name']: (row['latitude'], row['longitude']) for index, row in df1.iterrows() if row['spot_name'] in visited_spots}
    coordinates_info = [coordinates[key] for key in visited_spots]
    locations.extend(coordinates_info)
    print(coordinates)
    print(coordinates_info)
    
    matrix = [[0 for _ in range(total_spots + 1)] for _ in range(total_spots + 1)]
    for i in range(total_spots + 1):
        for j in range(total_spots + 1):
            if i != j:
                origin = locations[i]
                destination = locations[j]
                directions_result = gmaps.directions(origin, destination, mode="transit", departure_time=datetime.now())
                duration_in_traffic_seconds = directions_result[0]['legs'][0]['duration']['value']
                duration_in_traffic_minutes = duration_in_traffic_seconds / 60
                matrix[i][j] = duration_in_traffic_minutes
    graph = matrix
    vertex = {}
    for index, value in enumerate(route):
        vertex[index] = value
    print(vertex)
    min_path_weight = maxsize
    next_permutation=permutations(list(vertex.keys())[1:])
    min_path_order = None
    
    for i in next_permutation: 
        current_pathweight = 0
        k = 0
        for j in i:  
            current_pathweight += graph[k][j]  
            k = j  
        current_pathweight += graph[k][0]  

        if current_pathweight < min_path_weight:
            min_path_weight = current_pathweight
            min_path_order = [0] + list(i) + [0]
    min_path = []
    for order in min_path_order:
        min_path.append(vertex[order])
    print(min_path_order)
    total_time += matrix[0][min_path_order[1]] + matrix[min_path_order[-2]][0]
    total_time = round(total_time)
    
    return min_path, total_time

#用户界面
st.title('Plan Your HK Travel Route ^_^')
selected_ratio = st.slider('Please choose the ratio of transition probability to topic probability.', min_value=0.00, max_value=1.00, format="%.2f")
df_map = pd.read_excel("Spot Information.xlsx", sheet_name='Sheet1')
Spots_Information = {}
for index, row in df_map.iterrows():
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
        tooltip=f"{spot_name} for {', '.join(info['themes'])}",
        icon=folium.Icon(icon='cloud')
    ).add_to(m)
folium_static(m)
if selected_ratio > 0:
    st.subheader('Method 1')
    ratio = selected_ratio
    start_spot = st.selectbox('Please choose your start spot.', [None] + list(spots.keys()))
    total_spots = st.slider('Please choose the number of spots you would like to visit.', min_value=1, max_value=len(spots))
    max_time = st.slider('Please choose the time you expect to travel.', min_value=1, max_value=6050)
    themes = st.multiselect('Please choose the theme\(s\) you are interested in \(more than one can be chosen\).', list(set(theme for spot in spots.values() for theme in spot['themes'])))
    if st.button('Generate your travel route!'):
        result = route_method1(start_spot, total_spots, max_time, themes, ratio=selected_ratio)
        st.balloons()
        st.write(f"Route: {' → '.join(result[0])}")
        st.write(f"Total Time: {result[1]}")
        m_1 = folium.Map(location=[22.28056, 114.17222], zoom_start=12)
        points = []
        for spot in result[0]:
            folium.Marker(
                location=[Spots_Information[spot]['latitude'], Spots_Information[spot]['longitude']],
                tooltip=f"{spot} for {', '.join(Spots_Information[spot]['themes'])}",
                icon=folium.Icon(icon='cloud')
            ).add_to(m_1)
            points.append((Spots_Information[spot]['latitude'], Spots_Information[spot]['longitude']))
        folium_static(m_1)
elif selected_ratio == 0:
    st.subheader('Method 2')
    start_point = st.text_input("Please enter your current residence as your starting point and return point (It is recommended to enter the hotel where you live in Hong Kong or the customs port to Hong Kong).")
    spots_num = st.slider('Please choose the number of spots you would like to visit.', min_value=1, max_value=len(spots))
    themes = st.multiselect('Please choose the theme\(s\) you are interested in \(more than one can be chosen\).', list(set(theme for spot in spots.values() for theme in spot['themes'])))
    themes_num = st.slider('Please select how many times you would like the selected theme\(s\) to appear on the route.', min_value=1, max_value=spots_num+1)
    if st.button('Generate your travel route!'):
        result = route_method2(start_point, spots_num, themes, themes_num)
        st.balloons()
        st.write(f"Route: {' → '.join(result[0])}")
        st.write(f"Total Time: {result[1]}")
        m_1 = folium.Map(location=[22.28056, 114.17222], zoom_start=12)
        points = [coordinate_start]
        for spot in result[0]:
            folium.Marker(
                location=[Spots_Information[spot]['latitude'], Spots_Information[spot]['longitude']],
                tooltip=f"{spot} for {', '.join(Spots_Information[spot]['themes'])}",
                icon=folium.Icon(icon='cloud')
            ).add_to(m_1)
            points.append((Spots_Information[spot]['latitude'], Spots_Information[spot]['longitude']))
        folium_static(m_1)

