import streamlit as st 
from PIL import Image
import pandas as pd
import sqlite3

conn = sqlite3.connect('project')
c = conn.cursor()


st.set_page_config(
		page_title= "RouteRanger", 
		 layout="wide",  
		 #initial_sidebar_state="auto",  #Can be "auto", "expanded", "collapsed"
		 page_icon="🌲"
)

st.markdown("""
<style>
    [data-testid=stSidebar] {
        background-color: #587569;
    }
</style>
""", unsafe_allow_html=True)

st.sidebar.image("https://i.imgur.com/7VEtlCP.jpg", use_column_width=True)

st.title(":green[RouteRanger - A Trail Finder App]")

menu = ["Home", "Search", "Add Trails", "Update Trails", "Remove Trails"]
choice = st.sidebar.selectbox("Menu",menu)

if choice == "Home":
    st.subheader("About Us 🏞️")

    st.markdown('Welcome to RouteRanger - the premier community-based route finder app for outdoor enthusiasts!')
    st.markdown("""
                RouteRanger relies on the contributions of our dedicated members to build and expand our
                extensive trail database. Our community members are passionate bikers, hikers, mountaineers,
                and outdoor enthusiasts who love exploring trails across the United States.""")
    st.markdown("""Join RouteRanger today and be part of our ever-growing community of passionate outdoor explorers. 
                Contribute your favorite trails, discover new adventures, and connect with like-minded 
                individuals who share your love for the great outdoors.""")
    
    st.subheader("All Trails Overview 🏕️")
    all = 'SELECT trailName, parkName, elevation_feet, length, difficulty, routeType, reviews FROM Trails t JOIN NationalParks p ON t.parkID=p.parkID LIMIT 5'
    display = pd.read_sql_query(all, con=conn)
    st.dataframe(display, column_config={'trailName':'Trail', 'parkName':'National Park',
                                         'length': st.column_config.NumberColumn('Length',format="%.2f mi"),
                                         'elevation_feet':st.column_config.NumberColumn('Elevation',
                                                                                        format="%.2f ft"),
                                         'difficulty': st.column_config.NumberColumn('Difficulty',
                                                                                     help="1 - Easy, 2 - Moderate, 3 - Hard, 4 - Strenuous, 5 - Very challenging",
                                                                                       format="%d 🥾"),
                                         'reviews':st.column_config.NumberColumn('Reviews', format="%d 💬")},
                 hide_index=True)
    
elif choice=="Search":   
    st.subheader("Find trail🔎")
    search_choice = st.radio("Search by",("key word", "state","national park", "difficulty"))
    
    if search_choice=="key word":
        search_term = st.text_input("Enter key word")
        get_trail='SELECT trailName, elevation_feet, length, difficulty, routeType FROM Trails t JOIN NationalParks p ON t.parkID=p.parkID WHERE trailName LIKE "%{}%"'.format(search_term)
        result = pd.read_sql_query(get_trail, con=conn)
        st.write(result)
    
    elif search_choice=='state':
        state_menu = []
        for r in c.execute('SELECT DISTINCT(state) FROM Location'):
            state_menu.append(r[0])
        state_choice = st.multiselect("Select state", state_menu)
        
        # Check if state_choice is a list or a string
        if isinstance(state_choice, list):
        # Convert list to a string with comma-separated values
            states = ', '.join([f'"{state}"' for state in state_choice])
        else:
        # Wrap the single state_choice in quotes
            states = f'"{state_choice}"'
    
        get_trail=f'SELECT trailName, state, elevation_feet, length, difficulty, routeType FROM Trails t JOIN Location l ON t.trailID=l.trailID WHERE state IN ({states})'
        result = pd.read_sql_query(get_trail, con=conn)
        st.write(result)
        
    elif search_choice =="national park":
        all_parks = c.execute('SELECT DISTINCT(parkName) FROM NationalParks')
        park_menu = []
        for p in all_parks:
            park_menu.append(p[0])
        park_choice = st.multiselect("Select national park", park_menu)
        
        if isinstance(park_choice, list):
            # Convert list to a string with comma-separated values
            parks = ', '.join([f'"{park}"' for park in park_choice])
        else:
            parks = f'"park_choice"'
    
        
        get_trail=f'SELECT trailName, parkName, elevation_feet, length, difficulty, routeType FROM Trails t JOIN NationalParks p ON t.parkID=p.parkID WHERE parkName IN ({parks})'
        result = pd.read_sql_query(get_trail, con=conn)
        st.write(result)
    
    elif search_choice =="difficulty":
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(':red[Our difficulty levels:]')
            st.markdown('1 - Easy') 
            st.markdown('2 - Moderate')
            st.markdown('3 - Hard') 
            st.markdown('4 - Strenuous') 
            st.markdown('5 - Very challenging')
        
        with col2:
            levels = [1,2,3,4,5]
            level = st.selectbox("Select difficulty level", levels)
            
            get_trail='SELECT trailName, parkName, elevation_feet, length, difficulty, routeType FROM Trails t JOIN NationalParks p ON t.parkID=p.parkID WHERE difficulty="{}"'.format(level)
        for n_trails in c.execute('SELECT COUNT(*) FROM Trails WHERE difficulty="{}"'.format(level)):
            st.write(n_trails, 'total trails with difficulty level of', level)
        result = pd.read_sql_query(get_trail, con=conn)
        st.write(result)

if choice == 'Add Trails':
    st.subheader('Add a new trail')
    id = []
    for i in c.execute('SELECT trailID FROM Trails'):
        id.append(i[0])
    id.sort()
    new_trail_id = id[-1]+1
    
    new_trail_name = st.text_input("Enter trail name")
    new_elevation = st.text_input("Enter trail elevation in feet (number only)")
    new_length = st.text_input("Enter trail length in mile (number only)")
    new_difficulty = st.selectbox("Select difficulty", [1,2,3,4,5])
    
    park_menu = []
    new_parkID=''
    for p in c.execute('SELECT DISTINCT parkName FROM NationalParks'):
        park_menu.append(p[0])
    park_choice = st.selectbox("Select national park", park_menu)
    for i in c.execute('SELECT parkID FROM NationalParks WHERE parkName=?', (park_choice,)):
        new_parkID=i[0]
    
    new_route_type = st.selectbox("Select route type", ['out and back', 'loop', 'point to point'])
    
    if st.button('Add'):
        c.execute('SELECT trailName FROM Trails WHERE trailName=?', (new_trail_name,))
        result=c.fetchone()
        if result is not None:
            st.write('This trail already exists. Please use "search" to find this trail')
        else:
            insert_query='INSERT INTO Trails(trailID, trailName, length, elevation_feet, difficulty, \
            routeType, parkID) VALUES (?,?,?,?,?,?,?)'
            c.execute(insert_query,(new_trail_id, new_trail_name, new_length, new_elevation, new_difficulty, 
                                    new_route_type, new_parkID))
            conn.commit()
            st.write('Thanks! This trail is added to our database')
            new_trail = 'SELECT trailName, parkName, elevation_feet, length, difficulty, routeType FROM Trails t JOIN NationalParks p ON t.parkID=p.parkID WHERE \
                trailName="{}"'.format(new_trail_name)
            display = pd.read_sql_query(new_trail, con=conn)
            st.write(display)

if choice == "Update Trails":
    st.subheader("See something wrong?")
    
if choice == "Remove Trails":
    st.subheader("Know a trail that is no longer available?")
    