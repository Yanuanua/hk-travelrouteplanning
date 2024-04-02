import streamlit as st

def plan_route(start_spot, total_spots, max_time, themes):
    spots = {
        'aa': {'time': 2, 'themes': ['自然', '休闲']},
        'bb': {'time': 1, 'themes': ['人文', '城市']},
        'cc': {'time': 3, 'themes': ['购物', '休闲']},
        'dd': {'time': 2, 'themes': ['美食', '自然']},
        'ee': {'time': 1, 'themes': ['宗教', '自然']},
        'ff': {'time': 2, 'themes': ['游乐园']},
        'gg': {'time': 2, 'themes': ['体育', '休闲']},
        'hh': {'time': 3, 'themes': ['自然']},
        'ii': {'time': 2, 'themes': ['人文', '城市']},
        'jj': {'time': 1, 'themes': ['购物', '人文']},
        'kk': {'time': 2, 'themes': ['美食', '休闲']},
        'll': {'time': 1, 'themes': ['宗教']},
        'mm': {'time': 2, 'themes': ['游乐园', '城市']},
        'nn': {'time': 3, 'themes': ['体育', '购物']}
    }

    probabilities = {
        'aa': {'bb': 0.35, 'cc': 0.2, 'dd': 0.15, 'ee': 0.45, 'ff': 0.25, 'gg': 0.3, 'hh': 0.12, 'ii': 0.35, 'jj': 0.18, 'kk': 0.42, 'll': 0.1, 'mm': 0.33, 'nn': 0.22},
        'bb': {'aa': 0.25, 'cc': 0.3, 'dd': 0.1, 'ee': 0.5, 'ff': 0.2, 'gg': 0.35, 'hh': 0.1, 'ii': 0.4, 'jj': 0.22, 'kk': 0.48, 'll': 0.1, 'mm': 0.35, 'nn': 0.18},
        'cc': {'aa': 0.2, 'bb': 0.25, 'dd': 0.12, 'ee': 0.42, 'ff': 0.2, 'gg': 0.3, 'hh': 0.1, 'ii': 0.38, 'jj': 0.2, 'kk': 0.45, 'll': 0.1, 'mm': 0.3, 'nn': 0.25},
        'dd': {'aa': 0.22, 'bb': 0.2, 'cc': 0.1, 'ee': 0.48, 'ff': 0.18, 'gg': 0.32, 'hh': 0.1, 'ii': 0.42, 'jj': 0.2, 'kk': 0.4, 'll': 0.1, 'mm': 0.3, 'nn': 0.25},
        'ee': {'aa': 0.18, 'bb': 0.28, 'cc': 0.15, 'dd': 0.5, 'ff': 0.2, 'gg': 0.35, 'hh': 0.1, 'ii': 0.4, 'jj': 0.18, 'kk': 0.45, 'll': 0.1, 'mm': 0.32, 'nn': 0.22},
        'ff': {'aa': 0.2, 'bb': 0.25, 'cc': 0.1, 'dd': 0.52, 'ee': 0.22, 'gg': 0.3, 'hh': 0.1, 'ii': 0.4, 'jj': 0.2, 'kk': 0.45, 'll': 0.1, 'mm': 0.3, 'nn': 0.25},
        'gg': {'aa': 0.2, 'bb': 0.23, 'cc': 0.1, 'dd': 0.5, 'ee': 0.25, 'ff': 0.3, 'hh': 0.1, 'ii': 0.38, 'jj': 0.2, 'kk': 0.42, 'll': 0.1, 'mm': 0.32, 'nn': 0.23},
        'hh': {'aa': 0.2, 'bb': 0.22, 'cc': 0.1, 'dd': 0.48, 'ee': 0.2, 'ff': 0.3, 'gg': 0.1, 'ii': 0.42, 'jj': 0.2, 'kk': 0.45, 'll': 0.1, 'mm': 0.3, 'nn': 0.25},
        'ii': {'aa': 0.2, 'bb': 0.23, 'cc': 0.1, 'dd': 0.5, 'ee': 0.25, 'ff': 0.3, 'gg': 0.1, 'hh': 0.4, 'jj': 0.2, 'kk': 0.45, 'll': 0.1, 'mm': 0.32, 'nn': 0.23},
        'jj': {'aa': 0.2, 'bb': 0.25, 'cc': 0.1, 'dd': 0.48, 'ee': 0.22, 'ff': 0.3, 'gg': 0.3, 'hh': 0.38, 'ii': 0.2, 'kk': 0.45, 'll': 0.1, 'mm': 0.3, 'nn': 0.25},
        'kk': {'aa': 0.2, 'bb': 0.22, 'cc': 0.1, 'dd': 0.5, 'ee': 0.25, 'ff': 0.3, 'gg': 0.1, 'hh': 0.42, 'ii': 0.2, 'jj': 0.45, 'll': 0.1, 'mm': 0.32, 'nn': 0.23},
        'll': {'aa': 0.2, 'bb': 0.23, 'cc': 0.1, 'dd': 0.5, 'ee': 0.25, 'ff': 0.3, 'gg': 0.1, 'hh': 0.4, 'ii': 0.2, 'jj': 0.45, 'kk': 0.1, 'mm': 0.32, 'nn': 0.22},
        'mm': {'aa': 0.2, 'bb': 0.25, 'cc': 0.1, 'dd': 0.48, 'ee': 0.22, 'ff': 0.3, 'gg': 0.1, 'hh': 0.42, 'ii': 0.2, 'jj': 0.45, 'kk': 0.1, 'll': 0.3, 'nn': 0.23},
        'nn': {'aa': 0.2, 'bb': 0.23, 'cc': 0.1, 'dd': 0.5, 'ee': 0.25, 'ff': 0.3, 'gg': 0.1, 'hh': 0.4, 'ii': 0.2, 'jj': 0.45, 'kk': 0.1, 'll': 0.32, 'mm': 0.22}
    }
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

spots = {
    'aa': {'time': 2, 'themes': ['自然', '休闲']},
    'bb': {'time': 1, 'themes': ['人文', '城市']},
    'cc': {'time': 3, 'themes': ['购物', '休闲']},
    'dd': {'time': 2, 'themes': ['美食', '自然']},
    'ee': {'time': 1, 'themes': ['宗教', '自然']},
    'ff': {'time': 2, 'themes': ['游乐园']},
    'gg': {'time': 2, 'themes': ['体育', '休闲']},
    'hh': {'time': 3, 'themes': ['自然']},
    'ii': {'time': 2, 'themes': ['人文', '城市']},
    'jj': {'time': 1, 'themes': ['购物', '人文']},
    'kk': {'time': 2, 'themes': ['美食', '休闲']},
    'll': {'time': 1, 'themes': ['宗教']},
    'mm': {'time': 2, 'themes': ['游乐园', '城市']},
    'nn': {'time': 3, 'themes': ['体育', '购物']}
}


st.title('Plan Your HK Travel Route ^_^')
#st.page_link("your_app.py", label="Home", icon="🏠")
#st.page_link("pages/page_1.py", label="Page 1", icon="1️⃣")
#st.page_link("pages/page_2.py", label="Page 2", icon="2️⃣", disabled=True)
selected_option = st.selectbox('Please choose one method for travel route planning.', ['Method 1: For travelers who have time constraints and rely on historical experience.', 'Method 2: For travelers who have time to spare and love to explore new spots.'])
if selected_option == 'Method 1: For travelers who have time constraints and rely on historical experience.':
    st.subheader('Method 1')
    start_spot = st.selectbox('Please choose your start spot.', list(spots.keys()))
    total_spots = st.slider('Please choose the number of spots you would like to visit.', min_value=1, max_value=len(spots))
    max_time = st.slider('Please choose the time you expect to travel.', min_value=1, max_value=30)
    themes = st.multiselect('Please choose the theme\(s\) you are interested in \(more than one can be chosen\).', list(set(theme for spot in spots.values() for theme in spot['themes'])))

    if st.button('Generate your travel route!'):
        result = plan_route(start_spot, total_spots, max_time, themes)
        st.write(f"Route: {result[0]}")
        st.write(f"Total Time: {result[1]}")
else:
    st.subheader('Method 2')
