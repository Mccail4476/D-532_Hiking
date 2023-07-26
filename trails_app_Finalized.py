import streamlit as st 
import pandas as pd
import sqlite3

conn = sqlite3.connect('project')
c = conn.cursor()

### Creating database

## Parks Table & dataset ##

#Read master dataset
df = pd.read_csv('trails-data.csv')
#Create parks DataFrame
parks = df[['national_park']]
#Drop duplicates
parks = parks.drop_duplicates()
#Create a column that ranges from 1 to the maximum row
parks['park_id'] = range(1, len(parks)+1)
#Rename columns
parks = parks.rename(columns={'national_park':'parkName', 'park_id':'parkID'})
try:
    c.execute('DROP TABLE NationalParks;')
except:
    print("Nothing Happened")
c.execute('CREATE TABLE NationalParks (\
    parkName VARCHAR(100),\
    parkID INT PRIMARY KEY NOT NULL);')
parks.to_sql('NationalParks', conn, if_exists='append', index=False)

## Trails table & dataset
trails = df[['trail_id', 'name', 'national_park', 'length', 'elevation_gain',
       'difficulty_rating', 'route_type', 'num_reviews']]
trails = trails.rename(columns={'trail_id':'trailID', 'name':'trailName', 'national_park':'parkName', 'elevation_gain':'elevation_feet', 'difficulty_rating':'difficulty', 'route_type':'routeType', 'num_reviews':'reviews'})
trails = pd.merge(trails, parks, on='parkName')
trails.drop('parkName', axis=1, inplace=True)
trails['length'] = trails['length']*0.000621371
trails['trailID'].duplicated().any()
try:
    c.execute('DROP TABLE Trails;')
except:
    print("Nothing Happened")
c.execute('CREATE TABLE Trails (\
    trailID INT PRIMARY KEY NOT NULL,\
    trailName VARCHAR(50) NOT NULL,\
    elevation_feet DECIMAL(10,4),\
    length DECIMAL(10,4),\
    difficulty INT,\
    routeType VARCHAR(20),\
    reviews INT,\
    parkID INT);')
trails.to_sql('Trails', conn, if_exists='append', index=False)

## Features Table & dataset ##

features = df[['trail_id', 'features']]
def format_text(text):
    text = text[1:-1].split(', ')
    new_string = [t.replace("'","") for t in text]
    return new_string
features['feature_list'] = features['features'].apply(format_text)
features.drop('features', axis=1, inplace=True)
new_rows = []
for _, row in features.iterrows():
    feature_list = row['feature_list']
    for feature in feature_list:
        new_rows.append([row['trail_id'], feature])

new_feature = pd.DataFrame(new_rows, columns=['trail_id', 'feature'])
new_feature.head()
new_feature.rename(columns={'trail_id':'trailID'}, inplace=True)
try:
    c.execute('DROP TABLE Features;')
except:
    print("Nothing Happened")
c.execute('CREATE TABLE Features (\
    trailID INT, \
    feature VARCHAR(200),\
    FOREIGN KEY (trailID) REFERENCES Trails (trailID) ON DELETE CASCADE);')
new_feature.to_sql('Features', conn, if_exists='append', index=False)

## Activities dataset ##
activities = df[['trail_id', 'activities']]
activities['activity_list'] = activities['activities'].apply(format_text)
activities.drop('activities', axis=1, inplace=True)
new_rows = []
for _, row in activities.iterrows():
    activity_list = row['activity_list']
    for activity in activity_list:
        new_rows.append([row['trail_id'], activity])

new_activities = pd.DataFrame(new_rows, columns=['trail_id', 'activity'])
new_activities.head()
new_activities.rename(columns={'trail_id':'trailID'}, inplace=True)
try:
    c.execute('DROP TABLE Activities;')
except:
    print("Nothing Happened")
c.execute('CREATE TABLE Activities (\
    trailID INT, \
    activity VARCHAR(200),\
    FOREIGN KEY (trailID) REFERENCES Trails (trailID) ON DELETE CASCADE);')
new_activities.to_sql('Activities', conn, if_exists='append', index=False)


## Location dataset ##

loc = df[['trail_id', 'city_name', 'state_name', '_geoloc']].rename(columns={'trail_id':'trailID', 'city_name':'area_name','state_name':'state', '_geoloc':'geolocation'})
try:
    c.execute('DROP TABLE Location;')
except:
    print("Nothing Happened")
c.execute('CREATE TABLE Location (\
    trailID INT, \
    area_name VARCHAR(100),\
    state varchar(50),\
    geolocation varchar(100),\
    FOREIGN KEY (trailID) REFERENCES Trails (trailID) ON DELETE CASCADE);')
loc.to_sql('Location', conn, if_exists='append', index=False)

## Users Table
try:
    c.execute('DROP TABLE Users;')
except:
    print("Nothing Happened")
c.execute('CREATE TABLE Users (userID INTEGER PRIMARY KEY AUTOINCREMENT,\
    username VARCHAR(100),\
    uPassword VARCHAR(100));')


## TrailsUpdates Table ##

try:
    c.execute('DROP TABLE TrailsUpdates;')
except:
    print("Nothing Happened")
c.execute('CREATE TABLE TrailsUpdates (\
    updateID INTEGER PRIMARY KEY AUTOINCREMENT,\
    trailID INT,\
    userID INT,\
    content TEXT,\
    FOREIGN KEY (trailID) REFERENCES Trails (trailID),\
    FOREIGN KEY (userID) REFERENCES Users (userID));')

###


## Web application starts here

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

menu = ["Home", "Search", "Add Trails", "Trails Maintenance"]
choice = st.sidebar.selectbox("MENU", menu)

if choice == "Home":
    st.subheader("About Us 🏞️")

    st.markdown('Welcome to RouteRanger - the premier community-based trail finder app for outdoor enthusiasts!')
    st.markdown("""
                RouteRanger relies on the contributions of our dedicated members to build and expand our
                extensive trail database. Our community members are passionate bikers, hikers, mountaineers,
                and outdoor enthusiasts who love exploring trails across the United States.""")
    st.markdown("""Join RouteRanger today and be part of our ever-growing community of passionate outdoor explorers. 
                Contribute your favorite trails, discover new adventures, and connect with like-minded 
                individuals who share your love for the great outdoors.""")
    
    st.subheader("All Trails Overview 🏕️")
    all = 'SELECT trailName, parkName, elevation_feet, length, difficulty, routeType, reviews FROM Trails t JOIN NationalParks p ON t.parkID=p.parkID LIMIT 10'
    display = pd.read_sql_query(all, con=conn)
    st.dataframe(display, column_config={'trailName':'Trail', 'parkName':'National Park',
                                         'length': st.column_config.NumberColumn('Length',format="%.2f mi"),
                                         'elevation_feet':st.column_config.NumberColumn('Elevation',
                                                                                        format="%d ft"),
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
        get_trail='SELECT trailName, parkName, elevation_feet, length, difficulty, routeType FROM Trails t JOIN NationalParks p ON t.parkID=p.parkID WHERE trailName LIKE "%{}%"'.format(search_term)
        result = pd.read_sql_query(get_trail, con=conn)
        st.dataframe(result, column_config={'trailName':'Trail', 'parkName':'National Park',
                                            'length': st.column_config.NumberColumn('Length',format="%.1f mi"),
                                         'elevation_feet':st.column_config.NumberColumn('Elevation',
                                                                                        format="%d ft"),
                                         'difficulty': st.column_config.NumberColumn('Difficulty',
                                                                                     help="1 - Easy, 2 - Moderate, 3 - Hard, 4 - Strenuous, 5 - Very challenging",
                                                                                       format="%d 🥾")})
    
    elif search_choice=='state':
        all_states = c.execute('SELECT DISTINCT(state) FROM Location')
        state_menu = []
        for r in all_states:
            r=str(r).replace(',','').replace('(', '').replace(')', '').replace("'", "")
            state_menu.append(r)
        state_choice = st.multiselect("Select state", state_menu)
        
        # Check if state_choice is a list or a string
        if isinstance(state_choice, list):
        # Convert list to a string with comma-separated values
            states = ', '.join([f'"{state}"' for state in state_choice])
        else:
        # Wrap the single state_choice in quotes
            states = f'"{state_choice}"'
    
        get_trail=f'SELECT trailName, area_name, state, elevation_feet, length, difficulty, routeType FROM Trails t JOIN Location l ON t.trailID=l.trailID WHERE state IN ({states})'
        result = pd.read_sql_query(get_trail, con=conn)
        st.dataframe(result, column_config={'trailName':'Trail', 'area_name':'Area', 'state':'State',
                                         'length': st.column_config.NumberColumn('Length',format="%.1f mi"),
                                         'elevation_feet':st.column_config.NumberColumn('Elevation',
                                                                                        format="%d ft"),
                                         'difficulty': st.column_config.NumberColumn('Difficulty',
                                                                                     help="1 - Easy, 2 - Moderate, 3 - Hard, 4 - Strenuous, 5 - Very challenging",
                                                                                       format="%d 🥾")})
        
    elif search_choice =="national park":
        all_parks = c.execute('SELECT DISTINCT(parkName) FROM NationalParks')
        park_menu = []
        for r in all_parks:
            r=str(r).replace(',','').replace('(', '').replace(')', '').replace("'", "")
            park_menu.append(r)
        park_choice = st.multiselect("Select national park", park_menu)
        
        if isinstance(park_choice, list):
            # Convert list to a string with comma-separated values
            parks = ', '.join([f'"{park}"' for park in park_choice])
        else:
            parks = f'"park_choice"'
    
        get_trail=f'SELECT trailName, parkName, elevation_feet, length, difficulty, routeType FROM Trails t JOIN NationalParks p ON t.parkID=p.parkID WHERE parkName IN ({parks})'
        result = pd.read_sql_query(get_trail, con=conn)
        st.dataframe(result, column_config={'trailName':'Trail', 'parkName':'National Park',
                                         'length': st.column_config.NumberColumn('Length',format="%.1f mi"),
                                         'elevation_feet':st.column_config.NumberColumn('Elevation',
                                                                                        format="%d ft"),
                                         'difficulty': st.column_config.NumberColumn('Difficulty',
                                                                                     help="1 - Easy, 2 - Moderate, 3 - Hard, 4 - Strenuous, 5 - Very challenging",
                                                                                       format="%d 🥾")})
    
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
            st.write(n_trails[0], 'total trails with difficulty level of', level)
        result = pd.read_sql_query(get_trail, con=conn)
        st.dataframe(result, column_config={'trailName':'Trail', 'parkName':'National Park',
                                         'length': st.column_config.NumberColumn('Length',format="%.1f mi"),
                                         'elevation_feet':st.column_config.NumberColumn('Elevation',
                                                                                        format="%d ft"),
                                         'difficulty': st.column_config.NumberColumn('Difficulty',
                                                                                     help="1 - Easy, 2 - Moderate, 3 - Hard, 4 - Strenuous, 5 - Very challenging",
                                                                                       format="%d 🥾")})


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
    new_difficulty = st.selectbox("Select difficulty (1 to 5, where 5 is the most difficult)", [1,2,3,4,5])
    
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
            st.success('Thanks! This trail is added to our database', icon="✅")
            new_trail = 'SELECT trailName, parkName, elevation_feet, length, difficulty, routeType FROM Trails t JOIN NationalParks p ON t.parkID=p.parkID WHERE \
                trailName="{}"'.format(new_trail_name)
            display = pd.read_sql_query(new_trail, con=conn)
            st.write(display)


if choice == "Trails Maintenance":
    st.subheader("Need to update a trail or know a trail that is no longer available?")
    st.write("Hey, just go ahead and make some tweaks directly in the table below.")
    st.warning("Double-check the facts and make sure everything's entered correctly because our entire community relies on this database :)", icon="⚠️")
    st.info('Pro Tip: Click anywhere in the table and press Ctrl-F to search for the trail that needs to be updated or deleted', icon="⭐")
    # df = pd.read_csv('trails.csv')
    query = 'SELECT * FROM Trails'
    df = pd.read_sql_query(query, con=conn)
    
    edited_df = st.data_editor(df, key='data_editor', disabled=['trailID', 'parkID', 'reviews'], hide_index=True)
    
    del_trailID = st.text_input('Copy and Paste trail ID that needs to be remove:')
    del_trailID = del_trailID.replace(',', '').replace('"', '')

    if st.button('Delete'):
        try:
            del_trailID = int(del_trailID)
            c.execute('DELETE FROM Trails WHERE trailID=?', (del_trailID,))
            conn.commit()
            if c.rowcount > 0:
                st.write('Thanks! The trail with ID', del_trailID, 'has been removed from our database.')
            else:
                st.write('No rows found with the provided trail ID:', del_trailID)
        except ValueError:
            st.error('Please enter a valid trail ID', icon="🚨")
    
    changes = st.session_state["data_editor"]
    st.write("Here's what you've changed:")
    st.caption('_Once you make the changes, we will review them and update our database_')
    st.write(changes)
## Changes made by users are saved as a JSON object into varibale 'changes' and will be reviewed by admin team 
#  before making permanent changes into database, to avoid misuse of language. 
    
    
