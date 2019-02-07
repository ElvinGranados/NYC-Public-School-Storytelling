'''For this side project, I've decided to examine NYC public high schools and
use visualization to do some storytelling about the data I have collected
during the project'''

'''First I will import the libraries needed for my script'''
import pandas as pd
import scipy.stats as stats
import numpy as np
import matplotlib.pyplot as plt
import urllib.request
import json
import seaborn as sns
import string
from mpl_toolkits.basemap import Basemap

'''The csv file I am working with was taken from NYC opendata; a website that
provides data from various agencies available to the public. This data refers
to average SAT scores for each NYC high school in 2012. Note that some schools
have selected to suppress their data for the sake of protecting their students'
identities which is why there are 's' present'''

sat_file = pd.read_csv('2012_SAT_Results.csv')

'''I've decided to separate the two groups and only work with high schools that
have provided avalable numbers'''

'''The following filter boolean returns a dataframe with only schools of interest'''

data_bool = sat_file['Num of SAT Test Takers'] != 's'
sat_data = sat_file.loc[data_bool]

'''For this next step, the dataframe data type is all in strings so in order to
resolve this, I will convert the columns that contain the scores for each subject
into integers'''

subjects = ['SAT Critical Reading Avg. Score','SAT Math Avg. Score',
'SAT Writing Avg. Score']
s1 = sat_data[subjects[0]].astype('int64')
s2 = sat_data[subjects[1]].astype('int64')
s3 = sat_data[subjects[2]].astype('int64')
sum = s1+s2+s3
'''This line creates a new column that adds up the three individual scores using
vectorization and attaches it to the existing dataframe'''

sat_data['Composite SAT Avg. Score'] = sum

'''So far so good, but not enough storytelling can be told just from a set of
scores. I've also decided to analyze the demographics of each high school in this
data. The following file contains the 2006-2012 demographic for all public schools
in NYC. We will need to filter out some data so that we are only working with
high schools in the year 2012. One very important note is that both files use
the school code 'DBN' so this can be implemented into our filtering'''

'''The following lines filter out the data by the appropriate school year'''
dem_file = pd.read_csv('Demographic.csv')
year_bool = dem_file['schoolyear'] == 20112012
filter_1 = dem_file.loc[year_bool]

'''The next lines will filter further so that only the schools in the SAT data
show up and we can ignore the others'''
hs_list = sat_data['DBN'].values
hs_bool = dem_file.DBN.isin(hs_list)
filter_2 = filter_1.loc[hs_bool]

'''These next lines will also filter out the SAT dataframe so that both dataframes
will contain the same schools since there are a few schools that reported scores
but not complete their demographics'''
h_bool = sat_data.DBN.isin(filter_2['DBN'].values)
sat_data = sat_data.loc[h_bool]
nyc_hs_sat = sat_data

'''From the demographic dataset there are some specific columns I am interested
in so I would like to only work with those columns and not concern myself with
the rest. The following lines will give me the appropriate columns and from there
I will concatenate the two files into one bigger dataset.'''

list = ['ell_num','asian_per','black_per','hispanic_per','white_per','male_per',
'female_per']
nyc_hs_dem = filter_2.loc[:,list].set_index(nyc_hs_sat.index)
f_1 = pd.concat([nyc_hs_sat,nyc_hs_dem],axis=1)

'''One more element I would like to add are the coordinates of each of the schools
in the dataset. This will allow me to use basemap which is a toolkit that creates
maps on Python and can be used for data visulization. To get the coordinates for all
schools, I used the GoogleMaps API Geocode to access the server and get my desired
information. Unfortunately due to security reasons, I will only present the code I wrote to
access the coordinates which were contained in json form and write them into a .txt file. The
commented section includes using a API key which is personal. One issue to be noted is that
due to specificity, some coordinates will be from another location in the United States or there
will be no coordinates available for a particular school.'''

f = open('strings.txt','r')
g = open('jsoncoors.txt','r')
lines = g.readlines()
lat = []
lng = []
# for line in f:
#     response = urllib.request.urlopen(line)
#     link = response.read().decode('utf-8')
#     j = json.loads(link)
#     g.write(str(j))
#     g.write('\n')
# g.close()
for line in lines:
    try:
        j = line.replace("\'","\"")
        d = eval(j)
        res = d['results']
        geo = res[0]
        coord = geo['geometry']
        points = coord['location']
        lati = points['lat']
        lngt = points['lng']
        lat.append(lati)
        lng.append(lngt)
    except:
        lat.append(0)
        lng.append(0)

'''The last few lines will append the new columns onto the dataset and finally we finish off
our dataset by saving the current progress to a new csv file that has our relevant
information so if the user wishes to share the data they can do so'''

f_1['Latitude'] = lat
f_1['Longitude'] = lng
f_1.to_csv('NYC_HS_SAT_DEM_COO.csv',index=False)

'''One issue to note is that due to the inaccuracies, the outliers and zeroes in the dataset
will need to be fixed so that can be left to the reader of this code if they are interested.
Otherwise I took the liberty to manually adjust the values given that there is an acceptable
range of coordinates that surrounded New York City; data cleaning is ubiquitous
in data analysis so it is acceptable to make the proper fixes.'''

'''Now that we our data available, it is time to make some visuals! The following code
will read the corrected csv dataset and use Basemap to create a map of NYC with the locations
of all schools plotted on a new figure. Due to the complexity of Basemap, there will be some inaccuracies such
as the Hudson River not appearing on the map but this is due to the region of interest being so tiny.
Otherwise for a Matplotlib add-on it does a great job in map visuals and geography.'''

dataset = pd.read_csv('NYC_HS_SATDEMCOORfixed.csv')
fig = plt.figure(figsize=(10,6))

'''Here we access the latitude, longitude, and total SAT scores for each school and
convert each into an array. This csv file is different from the other created file
since it contains extras columns that were not of interest such as special education
students'''

lat = dataset.loc[:,'Latitude'].values
lon = dataset.loc[:,'Longitude'].values
sat = dataset.loc[:,'Composite SAT Avg. Score'].values

'''In case of unfamiliarity, these lines of code will create a Basemap object which
will include keyword arguments to adjust the map type, resolution and lower left/
upper right coordinates to display. More information on Basemap can be found online however
it is also convenient to know the coordinates of NYC to understand why these specific
numbers are used.'''

m = Basemap(projection = 'mill',resolution='h',llcrnrlon = -74.3,llcrnrlat= 40.45,
urcrnrlon=-73.75,urcrnrlat=40.9)
m.drawcoastlines()
m.fillcontinents(color='snow',zorder=0)
m.drawmeridians(np.arange(-74.3,-73.75,0.11),labels=[0,0,0,1])
m.drawparallels(np.arange(40.45,40.9,0.09),labels=[1,0,0,0])
x,y = m(lon,lat)
m.scatter(x,y,c=sat,cmap='winter',s=5)
plt.title('NYC Avg. Sat Scores by School in Year 2012')
plt.clim(sat.min(),sat.max())
plt.colorbar()
plt.show()

'''What I've done here is drawn my latitudinal and longitudinal lines to make
the map look aesthetically appealing. From there I used the scatterplot method to plot
the coordinates of all schools and used a colormap to scale the SAT scores from highest
to lowest. I also displayed the colorbar to assist the viewer in the interpretation of
the map. As we can see most scores will range around the 1350 area however there are a few schools
scattered around the city which have a much higher performance by at least 400 points. These schools are
specialized high schools which require an exam to gain admission. These students tend to be overachievers at
a younger age and are already excelling in middle school.'''

def borough_filter(dataset,key):
    boroughs = {'BROOKLYN':'K','MANHATTAN':'M','QUEENS':'Q','BRONX':'X','STATEN ISLAND':'R'}
    code = boroughs[key]
    bool = dataset.DBN.str.contains(code) == True
    return dataset.loc[bool]

'''For the next part of my project, it may be worthy to break down the schools by borough
and figure out what is the reason for performance in schools. The above function takes advantage
that each borough uses a unique letter to identify each school so by setting the key to the borough of
interest, we are able to filter the dataset.'''

def nyc_scatter():
    num = int(input('Enter number (1-6): '))
    code = {1:'BROOKLYN',2:'MANHATTAN',3:'BRONX',4:'QUEENS',5:'STATEN ISLAND'}
    if num != 6:
        data = borough_filter(dataset,code[num])
    elif num == 6:
        data = dataset
    races = data.loc[:,['asian_per','black_per','hispanic_per','white_per','Composite SAT Avg. Score']]
    fig = plt.figure(figsize=(12,6))
    i = 1
    color = ['blue','red','green','orange']
    label = ['asian','black','hispanic','white']
    k = 0
    for c in range(0,4):
        ax = fig.add_subplot(2,2,i)
        ax.scatter(races.iloc[:,c],races.iloc[:,4],c=color[k],label=label[k])
        ax.legend(loc='best')
        i += 1
        k += 1
    plt.show()
    return

nyc_scatter()

'''The function I created takes a user input between 1-6 where each number represents
a borough; the input 6 will instead take the entire city. The output of this function
will be a scatterplot that compares demographic percentages to composite SAT scores.'''
'''From the data, there appears to be a positive correlation between Asians and Whites and their performance
whereas the opposite is observed with Blacks and Hispanics. We can find the correlation between these
variables to determine the strength of these observations.'''

factors = dataset.loc[:,['SAT Critical Reading Avg. Score','SAT Math Avg. Score','SAT Writing Avg. Score',
'Composite SAT Avg. Score','asian_per','black_per','hispanic_per','white_per','male_per',
'female_per']]

matrix_f = factors.corr()

'''A seaborn visual tool called a heatmap presents the reader with a correlation
matrix that can show the reader meaningful relationships in a way that is not bland.'''

fig = plt.figure(figsize=(12,7))
ax = sns.heatmap(matrix_f,vmin=-1.0,vmax=1.0,annot=True,square=True)
plt.title('Correlation Matrix Heatmap')
plt.savefig('Visual4.png')
plt.show()

'''The matrix does match with our observations regarding demographic percentages and performance. What
is interesting to note is a strong relationship between asians and mathematics; although not in the data,
due to their counting system, children are learning arithmetic and larger numbers at a younger age in
these countries. Overall, a higher percentage of whites at a school does indicate good results on standardized
exams which is also indicative of success in their academics.'''

'''Unfortunately, for a very diverse city, the educational system is quite divisive just from observing scores. These
lower performing schools are from lower SES neighborhoods where the majority of students are either from the South Bronx
or East Brooklyn where the income goes as low as < $10000 annually. The neighborhoods contain poor housing conditions,
drug/crime activity and an environment where its inhabitants don't feel secure and thus priorites to flourish are
not present. From prior social research, it's also been shown that white and asian households have been taught
goal orientation, to grab opportunities when present and the value of hardwork from prior generations which are factors
outside of school that already assist students towards the path to success. This is not to say that the hispanic and
black demographic is not capable of success; there are already charter schools such as the Kipp Academy and Success Academy that push
their students to appreciate the value of hardwork and strive for their future success. Strict scheduling, hours of homework, fast
paced learning starting from grade school are techniques these programs have implemented. Starting in 2016, the SAT itself
was revised to test students on more relevant material that has been taught in schools and wouldn't give students who
could afford the expensive courses such an advantage. Unfortunately, the necessary evil to compare students won't go
away anytime soon and colleges/universities need a way to measure the success of their future admittants.'''

'''What I've also decided to do is create a visual that shows median income across neighborhoods in NYC which
will further prove the unfairness that is present not just in test scores but also for the success of children that will
lead the next generation'''

'''I found the average income for the top 50 populous neighborhoods, created a csv file and used both seaborn and
basemap to create figures to further illustrate my observations.'''

n_hood = pd.read_csv('Neighborhood Coordinates.csv')
neigh = n_hood.loc[:,'Neighborhood '].values
lat = n_hood.loc[:,'Latitude'].values
lng = n_hood.loc[:,'Longitude'].values
inc = n_hood.loc[:,'Household Income (Median)'].values

fig = plt.figure(figsize=(12,6))
ax = sns.barplot(x=inc,y=neigh,palette='coolwarm')
plt.title('Median Household Income')
plt.xlabel('Income ($)')
plt.savefig('Visual3.png')
plt.show()

'''Not surprising, we are looking at neighborhoods that are in the Bronx where the median income is as low as
a sixth of the income more affluent neighborhoods are earning.'''

fig = plt.figure(figsize=(6,6))
m = Basemap(projection = 'mill',resolution='h',llcrnrlon = -74.08,llcrnrlat= 40.54,
urcrnrlon=-73.7,urcrnrlat=40.9)
m.drawcoastlines()
m.fillcontinents(color='snow',zorder=0)
m.drawmeridians(np.arange(-74.08,-73.7,0.1),labels=[0,0,0,1])
m.drawparallels(np.arange(40.54,40.9,0.06),labels=[1,0,0,0])
x,y = m(lng,lat)
m.scatter(x,y,c=inc,cmap='autumn',s=300,alpha=0.9)
plt.title('Household Income ($) vs. Neighborhood')
plt.clim(0,inc.max())
plt.colorbar()
plt.savefig('Visual2.png')
plt.show()

'''The map further illustrates the unfairness that is being exhibited in these lower SES neighborhoods.
As of 2018 some of these schools have been shut down and are no longer operating. News articles have stated that
these schools were not managed correctly, standards were subpar,and the faculty just did not care for the school. Students were
in a state of hopelessness and lacked any guidance at one of these schools and adults felt that the school should have never
been open.'''

'''This little project I do hope tells the reader a story about the divided educational system in NYC. I
personally attended one of the specialized high schools and this has made me appreciate the opportunity that
was given to me and the realization that growing up in one of the poorer neighborhoods not every child is fortunate
to be in a nurturing environment that allows for success. Although strives have been made to change this system,
we are still far away from every child having the chance to be a contributer to their society. We need to remind
ourselves that students are tractable and will be the ones to lead the future so we must do our best to help them.
I found interest in doing this assignment from reading Malcolm Gladwell's Outliers which taught me that success
can come in many forms as well as opportunities and environment can make or break individuals.'''
