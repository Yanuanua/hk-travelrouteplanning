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
import random

#Dataset
df1 = pd.read_excel("Data for Route.xlsx", sheet_name='transition')
spots = {}
tran_post = {}
tran_pre = {}
for index, row in df1.iterrows():
    themes = [theme.strip() for theme in row['themes'].split(',')]
    spot_data = {
        'latitude': row['latitude'],
        'longitude': row['longitude'],
        'time': int(row['time']),
        'cluster': str(row['cluster']),
        'spot_pre': float(row['spot_pre']),
        'spot_post': float(row['spot_post']),
        'themes': themes
    }
    spots[row['spot_name']] = spot_data
for index, row in df1.iterrows():
    probs1 = {key: row[key] for key in row.index[8:46]}
    tran_post[row['spot_name']] = probs1
for index, row in df1.iterrows():
    probs2 = {key.replace('.1', ''): row[key] for key in row.index[46:84]}
    tran_pre[row['spot_name']] = probs2
df1_1 = pd.read_excel("Data for Route.xlsx", sheet_name='transportation')
traffic_m1 = {}
for index, row in df1_1.iterrows():
    traf = {key: round(row[key]) for key in row.index[1:39]}
    traffic_m1[row['spot_name']] = traf

#Method1
def route_method1(start_spot, total_spots, max_time, themes, postpre, tratio, sratio):  
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
            next_spot = max(remaining_spots, key=lambda x: tratio*(postpre*tran_post[route[-1]][x]+(1-postpre)*tran_pre[route[-1]][x])+sratio*(postpre*spots[x]['spot_post']+(1-postpre)*spots[x]['spot_pre']))
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
                next_spot = max(remaining_spots, key=lambda x: tratio*(postpre*tran_post[route[-1]][x]+(1-postpre)*tran_pre[route[-1]][x])+sratio*(postpre*spots[x]['spot_post']+(1-postpre)*spots[x]['spot_pre']))
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
                            tran_post[current_spot][spot]*=1.8
                            tran_pre[current_spot][spot]*=1.8
                            spots[spot]['spot_post']*=1.8
                            spots[spot]['spot_pre']*=1.8
            next_spot = max(remaining_spots, key=lambda x: tratio*(postpre*tran_post[route[-1]][x]+(1-postpre)*tran_pre[route[-1]][x])+sratio*(postpre*spots[x]['spot_post']+(1-postpre)*spots[x]['spot_pre']))
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
                next_spot = max(remaining_spots, key=lambda x: tratio*(postpre*tran_post[route[-1]][x]+(1-postpre)*tran_pre[route[-1]][x])+sratio*(postpre*spots[x]['spot_post']+(1-postpre)*spots[x]['spot_pre']))
                next_spot_info = spots[next_spot]
                route.append(next_spot)
                visited_clusters.add(next_spot_info["cluster"])
                total_time += next_spot_info['time']
                total_time += traffic_m1[current_spot][next_spot]
        
        current_spot = next_spot
    
    return route, total_time

#Method2
def route_method2(start_point, spots_num, themes, themes_num, postpre):
    filtered_data = []
    all_spots = set()
    for i in range(len(themes), 0, -1):
        filtered = df1[df1['themes'].astype(str).apply(lambda x: sum(theme in x for theme in themes) >= i)]
        filtered = filtered[~filtered['spot_name'].isin(all_spots)]
        all_spots.update(filtered['spot_name'])
        filtered_data.append(filtered)
        
    combined_df = pd.concat(filtered_data)
    combined_df['themes_count'] = combined_df['themes'].apply(lambda x: sum(theme in x for theme in themes))
    combined_df['spot_post'] = combined_df['spot_post']*postpre
    combined_df['spot_pre'] = combined_df['spot_pre'] *(1-postpre)
    combined_df['combined_pro'] = combined_df['spot_post'] + combined_df['spot_pre']
    sorted_df = combined_df.sort_values(by=['themes_count', 'combined_pro'], ascending=[False, False])
    top_spots = sorted_df['spot_name'].head(themes_num).tolist()
    rows_count = len(top_spots)
    
    if spots_num > themes_num:
        combined_df = combined_df[~combined_df['spot_name'].isin(top_spots)]
        #filtered_df = df1[~df1['spot_name'].isin(top_spots)]
        #sorted_df = filtered_df.sort_values(by='spot_pro', ascending=False)
        sorted_df = combined_df.sort_values(by='combined_pro', ascending=False)
        top_spots1 = sorted_df['spot_name'].head(spots_num - rows_count).tolist()
    else:
        top_spots1 = []
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
                duration_in_traffic = directions_result[0]['legs'][0]['duration']['value'] / 60
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

    return min_path, total_time, start_point, coordinate_start

#Method3
def route_method3(start_point, spots_num, themes, themes_num, spots=spots): #必须输入start point 酒店/关口
    filtered_data = []
    all_spots = set()
    for i in range(len(themes), 0, -1):
        filtered = df1[df1['themes'].astype(str).apply(lambda x: sum(theme in x for theme in themes) >= i)]
        filtered = filtered[~filtered['spot_name'].isin(all_spots)]
        all_spots.update(filtered['spot_name'])
        filtered_data.append(filtered)
    combined_df = pd.concat(filtered_data)
    
    combined_df['themes_count'] = combined_df['themes'].apply(lambda x: sum(theme in x for theme in themes))
    sorted_df = combined_df.sort_values(by=['themes_count'], ascending=False)
    top_spots = sorted_df['spot_name'].head(themes_num).tolist()
    random.shuffle(top_spots)
    if spots_num > themes_num:
        remaining_spots = df1[~df1['spot_name'].isin(top_spots)]['spot_name'].tolist()
        random.shuffle(remaining_spots)
        selected_remaining_spots = remaining_spots[:spots_num - themes_num]
    else:
        selected_remaining_spots = []
    visited_spots = top_spots + selected_remaining_spots
    route = [start_point] + visited_spots
    total_stay_time = df1[df1['spot_name'].isin(route)]['time'].sum()
    
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
    
    matrix = [[0 for _ in range(spots_num + 1)] for _ in range(spots_num + 1)]
    for i in range(spots_num + 1):
        for j in range(spots_num + 1):
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
    total_duration = 0
    for i in range(len(min_path) - 1):
        origin_spot = min_path[i]
        destination_spot = min_path[i + 1]
        origin_index = route.index(origin_spot)
        destination_index = route.index(destination_spot)
        duration_in_traffic = matrix[origin_index][destination_index]
        total_duration += duration_in_traffic
    total_time = round(total_stay_time+total_duration)

    return min_path, total_time, start_point, coordinate_start

#用户界面
st.title('Plan Your HK Travel Route ^_^')
st.write('Hello dear tourists, welcome to our Hong Kong travel route recommendation system.')
st.write('We now support 3 route recommendation methods.')
st.markdown("<h1 style='text-align: left; color: green; font-size: 20px;'>Method 1 (if transition probability ≠ 0)</h1>", unsafe_allow_html=True)
st.write('Suitable for tourists who follow popular attractions but have limited time, are in the attractions, or have certain intentions \(the larger the number, the more dependent it is on the transition probability, and the smaller the number, the more dependent it is on the spot probability\).')
st.markdown("<h1 style='text-align: left; color: green; font-size: 20px;'>Method 2 (if transition probability = 0 and spot probability ≠ 0)</h1>", unsafe_allow_html=True)
st.write('Suitable for tourists who follow popular attractions and have ample time.')
st.markdown("<h1 style='text-align: left; color: green; font-size: 20px;'>Method 3 (if transition probability = 0 and spot probability = 0)</h1>", unsafe_allow_html=True)
st.write('Suitable for tourists who are willing to explore different attractions and have ample time.')
options = [None, 0.00, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 1.00]
Spots_Information = {}
for index, row in df1.iterrows():
    themes = [theme.strip() for theme in row['themes'].split(',')]
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
selected_tratio = st.slider('Please choose the weight of the transition probability.', min_value=0, max_value=100)
selected_sratio = st.slider('Please choose the weight of the spot probability.', min_value=0, max_value=100)
if selected_tratio != 0:
    st.subheader('Method 1: Transition Probability, Time Constraint, and Theme Priority Method')
    postpre = st.slider('Please choose the ratio of post-pandemic data and pre-pandemic data.', min_value=1, max_value=9)
    start_spot = st.selectbox('Please choose your start spot.', [None] + list(spots.keys()))
    total_spots = st.slider('Please choose the number of spots you would like to visit.', min_value=1, max_value=len(spots))
    time_hours = st.slider('Please choose the time you expect to travel (hours)', min_value=0, max_value=24)
    time_minutes = st.slider('Please choose the time you expect to travel (minutes)', min_value=0, max_value=59)
    max_time = time_hours * 60 + time_minutes
    themes = st.multiselect('Please choose the theme\(s\) you are interested in \(more than one can be chosen\).', list(set(theme for spot in spots.values() for theme in spot['themes'])))
    tratio = selected_tratio
    sratio = selected_sratio
    if st.button('Generate your travel route!'):
        result = route_method1(start_spot, total_spots, max_time, themes, postpre=postpre,tratio=tratio, sratio=sratio)
        st.balloons()
        st.write(f"Route: {' → '.join(result[0])}")
        hours = result[1] // 60
        minutes = result[1] % 60
        st.write(f"Total Time: {hours} hours {minutes} minutes")
        st.write('\U00002600 Thank you for using our recommendation system and have a nice trip! \U00002600')
        m_1 = folium.Map(location=[22.28056, 114.17222], zoom_start=12)
        points = []
        i = 1
        for spot in result[0]:
            folium.Marker(
                location=[Spots_Information[spot]['latitude'], Spots_Information[spot]['longitude']],
                tooltip=f"{spot} for {', '.join(Spots_Information[spot]['themes'])}",
                icon=folium.Icon(icon='fa-' + str(i), prefix='fa')
            ).add_to(m_1)
            i = i + 1
        folium_static(m_1)
elif selected_sratio != 0:
    st.subheader('Method 2: TSP Spot Probability and Theme Priority Method')
    postpre = st.slider('Please choose the ratio of post-pandemic data and pre-pandemic data.', min_value=1, max_value=9)
    start_point = st.text_input("Please enter your current residence as your starting and return point (It is recommended to enter the hotel where you live in Hong Kong or the customs port to Hong Kong).")
    spots_num = st.slider('Please choose the number of spots you would like to visit.', min_value=1, max_value=len(spots))
    themes = st.multiselect('Please choose the theme\(s\) you are interested in \(more than one can be chosen\).', list(set(theme for spot in spots.values() for theme in spot['themes'])))
    themes_num = st.slider('Please select how many times you would like the selected theme\(s\) to appear on the route.', min_value=0, max_value=spots_num)
    if st.button('Generate your travel route!'):
        if not start_point:
            st.warning("Please enter your current residence as your starting and return point.")
        if not themes:
            st.warning("Please choose the theme\(s\) you are interested in.")
        else:
            start_point = f"Hong Kong {start_point}"
            result = route_method2(start_point, spots_num, themes, themes_num, postpre=postpre)
            st.balloons()
            st.write(f"Route: {' → '.join(result[0])}")
            hours = result[1] // 60
            minutes = result[1] % 60
            st.write(f"Total Time: {hours} hours {minutes} minutes")
            st.write('\U00002600 Thank you for using our recommendation system and have a nice trip! \U00002600')
            m_1 = folium.Map(location=[22.28056, 114.17222], zoom_start=12)
            folium.Marker(
                location= list(result[3][1]),
                tooltip=f"Your Starting and Return Point: {result[2]}",
                icon=folium.Icon(icon='cloud')
                ).add_to(m_1)
            i = 1
            for spot in result[0][1:-2]:
                folium.Marker(
                    location=[Spots_Information[spot]['latitude'], Spots_Information[spot]['longitude']],
                    tooltip=f"{spot} for {', '.join(Spots_Information[spot]['themes'])}",
                    icon=folium.Icon(icon='fa-' + str(i), prefix='fa')
                ).add_to(m_1)
                i = i + 1
            folium_static(m_1)
else:
    st.subheader('Method 3: TSP Random and Theme Priority Method')
    spots = spots
    start_point = st.text_input("Please enter your current residence as your starting and return point (It is recommended to enter the hotel where you live in Hong Kong or the customs port to Hong Kong).")
    spots_num = st.slider('Please choose the number of spots you would like to visit.', min_value=1, max_value=len(spots))
    themes = st.multiselect('Please choose the theme\(s\) you are interested in \(more than one can be chosen\).', list(set(theme for spot in spots.values() for theme in spot['themes'])))
    themes_num = st.slider('Please select how many times you would like the selected theme\(s\) to appear on the route.', min_value=0, max_value=spots_num)
    if st.button('Generate your travel route!'):
        if not start_point:
            st.warning("Please enter your current residence as your starting and return point.")
        if not themes:
            st.warning("Please choose the theme\(s\) you are interested in.")
        else:
            start_point = f"Hong Kong {start_point}"
            result = route_method3(start_point, spots_num, themes, themes_num, spots=spots)
            st.balloons()
            st.write(f"Route: {' → '.join(result[0])}")
            hours = result[1] // 60
            minutes = result[1] % 60
            st.write(f"Total Time: {hours} hours {minutes} minutes")
            st.write('\U00002600 Thank you for using our recommendation system and have a nice trip! \U00002600')
            m_1 = folium.Map(location=[22.28056, 114.17222], zoom_start=12)
            folium.Marker(
                location= list(result[3][1]),
                tooltip=f"Your Starting and Return Point: {result[2]}",
                icon=folium.Icon(icon='cloud')
                ).add_to(m_1)
            i = 1
            for spot in result[0][1:-2]:
                folium.Marker(
                    location=[Spots_Information[spot]['latitude'], Spots_Information[spot]['longitude']],
                    tooltip=f"{spot} for {', '.join(Spots_Information[spot]['themes'])}",
                    icon=folium.Icon(icon='fa-' + str(i), prefix='fa')
                ).add_to(m_1)
                i = i + 1
            folium_static(m_1)
    
