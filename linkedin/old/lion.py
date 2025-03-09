## LIONS - LinkedIn Opportunity Networking Search
# “You are more than what you have become.” – Mufasa

# Version 0.3

# Copyright (C) 2022 Timothy Clarke https://www.linkedin.com/in/tjclarke/

# When you pull the data from LinkedIn pull you "Connections" data and you "messages" data (.csv files)
# Information about how to get your Connections data from LinkedIn is here: https://lnkd.in/gdpudPAV
# It is easy to figure out how to also pull the "messages" data.  You just need to select that data also.

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program. If not, see https://www.gnu.org/licenses/.

import datetime
import os
import time

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import math

workpath = os.getcwd()
connectionsfile = workpath + "/Connections.csv"
messagesfilepath = workpath + "/messages.csv"

connections = pd.read_csv(connectionsfile, skiprows=3)

#messages = pd.read_csv(messagesfilepath)

## Let's explore the data a bit before we get started

connections.describe()

connections.head(3)

connections.dtypes

# Note to self... we will need to fix "Connected On" to a datetime 

### First let's recreate the examples in the LinkedIn document (Thanks Mr Briit --Total Data Science (https://www.linkedin.com/in/mrbriit/)

connections = connections.sort_values(by="Connected On")

plt.figure(figsize=(20, 6))
ax = sns.barplot(
    data=connections.groupby(by="Connected On").count().reset_index(),
    x="Connected On",
    y="First Name",
)
ax.set(xticklabels=[])
plt.show()

## Positions: Which Positions do my connections hold?

Positions = (
    connections["Position"]
    .value_counts()[
        connections["Position"].value_counts() / len(connections) * 100 > 0.20
    ]
    .to_frame()
    .reset_index()
)
Positions.rename(columns={"index": "position", "Position": "count"}, inplace=True)
Positions

plt.figure(figsize=(15, 10))
bar = sns.barplot(x="position", y="count", data=Positions)
plt.xticks(rotation=-90)
plt.show()

## wordcloud can be a little tricky to install. If you only need it for plotting a basic wordcloud, <br>
## then pip install wordcloud or conda install -c conda-forge wordcloud would be sufficient. However, <br>
## the latest version with the ability to mask the cloud into any shape of your choice requires a different <br>
## method of installation as below:

## git clone https://github.com/amueller/word_cloud.git
## cd word_cloud
## pip install .

import sys

# !{sys.executable} -m pip install wordcloud

from wordcloud import WordCloud


def CreateWordCloud(text):
    wordcloud = WordCloud(
        width=1000,
        height=900,
        background_color="black",
        min_font_size=10,
        colormap="Set2",
    ).generate(text)

    plt.figure(figsize=(15, 15))
    plt.grid(visible=None)
    plt.axis("off")
    plt.imshow(wordcloud, interpolation="bilinear")

connections.fillna("Unknown", inplace=True)

string = ""
for index, row in connections.iterrows():
    string += row["Position"] + " "

CreateWordCloud(string)

## Unfortunately "Company" is hand coded by each user and could be anything.  We need to figure out how to clean that up to make it more useful.

connections["cleaned"] = connections[
    "Company"
].str.strip()  # cleans up all of the early and late white spaces
connections["cleaned"] = connections[
    "cleaned"
].str.title()  # set all the rANdom CASE decsions by People to a CONSISTENLY be the "The Title Case"
connections["comp"] = connections[
    "cleaned"
]  # creates a new column which will be modified below.

# The CondenseDict could need to be modified (personalized) in the future.

## The condensing dictionary below will likely need to be personalized to some extent.

## The format is:<br> 
## key = What string will be searched for in the company name column<br>
## value = What string will replace the entire string in the company name column if the key is found<br>

## For example using my this CondenseDict below all of the following "Amazon Web Services", "Amazon Robotics", "AWS Inc.", "At AWS", "I LOVE MACAWS" would all condense to "Amazon" (clearly it is not a perfect solution, but I am open to suggestions)

out = "No Company"

CondenseDict = {
    "..": "Unknown",
    "Hire Right Away": out,
    "Job Hunt": out,
    "Unknown": out,
    "@Home": out,
    "Retired": out,
    "Freelance": out,
    "Independent Consultant": out,
    "Independent Contractor": out,
    "Self Employed": out,
    "SelfEmployed": out,
    "Self-Employed": out,
    "Actively Looking": out,
    "Manyhobbies": out,
    "None": out,
    "Clarke": out,  # some of the author's family members
    "Adobe": "Adobe",
    "Affine": "Affine",
    "Amazon": "Amazon",
    "AWS": "Amazon",
    "Hca": "HCA Healthcare",
    "Deloitte": "Deloitte",
    "Fico": "FICO",
    "Gap": "GAP",
    "Teradata": "Teradata",
    "Pepsi": "PepsiCo",
    "Sap": "SAP",
    "Tata": "Tata",
    "Target": "Target",
    "Ibm": "IBM",
    "Gilead": "Gilead Sciences",
    "Servicenow": "ServiceNow",
    "University Of California, San Diego": "UCSD",
    "Uc San Diego": "UCSD",
    "Ucsd": "UCSD",
}

# This little piece of code loops through the "Condense Dictionary" and searched the "Co_name" column for the Dic:key in every element of the
# column... if it finds it in the string, it replaced it with the Dic:value.  The has the effect of condensing "Amazon", "Amazon Robotics" and "AWS" to "Amazon" (for example)

for key in CondenseDict:
    for index, row in connections.iterrows():
        if key in str(row["comp"]):
            connections.loc[index, "comp"] = CondenseDict[key]


# uncomment below and run if you want to check out how effect of this chunk of code on your data.

pd.set_option('display.max_rows', None)  # or 1000
connections[["Company", "cleaned", "comp"]]

# Clean up the date information and set to a datatime format
connections["c_date"] = pd.to_datetime(connections["Connected On"], format="%d %b %Y")
connections["c_year"] = pd.DatetimeIndex(connections["c_date"]).year
connections["c_month_year"] = (
    pd.DatetimeIndex(connections["c_date"]).to_period("M").to_timestamp()
)

# Review your annual connection history

connections["now"] = datetime.datetime.now()


def month_diff(x, y):
    end = x.dt.to_period("M").view(dtype="int64")
    start = y.dt.to_period("M").view(dtype="int64")
    return end - start + 1


connections["months_connected"] = month_diff(connections.now, connections.c_month_year)

yearly_connect = connections.groupby(by=["c_year"])["Last Name"].count().reset_index()
yearly_connect = yearly_connect.rename(
    columns={"c_year": "year", "Last Name": "New Contacts"}
)
yearly_connect["Total Contacts"] = yearly_connect["New Contacts"].cumsum()
yearly_connect.set_index("year", inplace=True)
yearly_connect = yearly_connect[["Total Contacts", "New Contacts"]]
yearly_connect

plt.figure(figsize=(12, 8))
sns.set_style("whitegrid")
sns.set_context("talk")
p = sns.lineplot(data=yearly_connect, dashes=False)
p.set_title("LinkedIn Contacts (per Year)", fontsize=25)
p.set_ylabel("Contacts", fontsize=20)
p.set_xlabel("Year", fontsize=20)
plt.grid(visible=True)
plt.axis("on")
plt.show()

## A more granular look at connection history

monthly_connect = (
    connections.groupby(by=["c_month_year"])["Last Name"].count().reset_index()
)
monthly_connect = monthly_connect.rename(
    columns={"c_month_year": "mon_y", "Last Name": "New Contacts"}
)

datetime_index = pd.DatetimeIndex(monthly_connect["mon_y"].values)
monthly_connect.set_index(datetime_index, inplace=True)
monthly_connect.drop("mon_y", axis=1, inplace=True)
monthly_connect.sort_index(inplace=True)
monthly_connect = monthly_connect.asfreq("MS")

monthly_connect.fillna(0, inplace=True)
monthly_connect["Total Contacts"] = monthly_connect["New Contacts"].cumsum()

monthly_connect = monthly_connect[["Total Contacts", "New Contacts"]]

plt.figure(figsize=(20, 6))
sns.set_style("whitegrid")
sns.set_context("talk")
p = sns.lineplot(data=monthly_connect, dashes=False)
p.set_title("LinkedIn Contacts (per Month, Log Scale)", fontsize=25)
p.set_yscale("log")
p.set_ylabel("Contacts", fontsize=20)
p.set_xlabel("Year", fontsize=20)

# Optimal Search Chart

### Use the three variables below to customize your chart

## If there are companies on this list that you don't want to work for, add them to your "DoNotShow" list, for example, the company you just left

MinDepth = 15  # depth is average years * number of contacts.  If you know 4 people at Google for 3 years it is a depth of 12
MinContacts = 2  # Suggest a minium of 2 when doing job search, it is hard to get in touch with people sometimes...
DoNotShow = [
    out,
    "Teradata",
#    "Wells Fargo",
#    "UCSD",
#    "Intersystems",
#    "Cerulium Corporation",
#    "Amazon",
#    "GAP",
]  # Add companies that you are not consdiering.  Keep "out" = "No Company".
rotdeg = 40 # Rotation degree of the names in the chart

column_filter = "|".join(DoNotShow)
company_connect = connections.groupby(by=["comp"])["Last Name"].count().reset_index()
company_connect = company_connect.rename(columns={"Last Name": "Contacts"})
company_connect = company_connect[
    np.logical_not(company_connect["comp"].str.contains(column_filter))
]

company_avg = connections.groupby(by=["comp"])["months_connected"].mean().reset_index()
company_connect["ave_years"] = company_avg["months_connected"] / 12
company_connect["depth"] = company_connect["ave_years"] * company_connect["Contacts"]
company_connect = company_connect[
    (company_connect.depth >= MinDepth) & (company_connect.Contacts >= MinContacts)
]
company_connect = company_connect.reset_index(drop=True)

## You need to delete or rename the existing file if you want it to refresh

company_connect.to_csv("data/all_companies.csv", header=True)

plt.figure(figsize=(10, 10))
sns.set_style("darkgrid")
sns.set_context("talk", font_scale=0.9)

x = company_connect["ave_years"]
y = company_connect["Contacts"]
c = company_connect["comp"]

plt.figure(figsize=(15, 10))
p = sns.scatterplot(x="ave_years", y="Contacts", data=company_connect)


lx = np.arange(MinDepth) + 1
ly = MinDepth / lx
ly2 = MinDepth * 2 / lx
ly4 = MinDepth * 4 / lx

# These lines show "zones of similar prospects"
ax = sns.lineplot(x=lx, y=ly, linestyle="dashed", alpha=0.3)
ax2 = sns.lineplot(x=lx, y=ly2, linestyle="dashed", alpha=0.3)
ax4 = sns.lineplot(x=lx, y=ly4, linestyle="dashed", alpha=0.3)

# Annotate label points
for i, c in enumerate(c):
    plt.annotate(c, (x[i] + 0.05, y[i] + 0.05), rotation=rotdeg)
p.set_ylabel("LinkedIn Connections", fontsize=20)
p.set_xlabel("Average Years Connected", fontsize=20)
p.set_title("My Optimal Job Search", y=1.05, fontsize=20)

# These most likely need to be adjusted.

max_y = math.ceil(company_connect.Contacts.max())+1
max_x = math.ceil(company_connect.ave_years.max())+1

p.set_ylim(0, max_y)
p.set_xlim(0, max_x)
plt.show()

## Who should you reach out to?

connections["full_name"] = connections["First Name"] + " " +connections["Last Name"]

who_to_contact = pd.merge(company_connect, connections[['comp','full_name','Connected On','months_connected']],
                          how='inner', on='comp').sort_values(by='months_connected', ascending=False)

HowManyToSee = 50

who_to_contact[
    ["comp", "depth", 'full_name', "Connected On", "months_connected"]
].head(HowManyToSee)


# How many of those people at the your target companies do you have LinkedIn message conversations with?

#messages.dtypes

#convos = messages[["FROM","TO","SENDER PROFILE URL","DATE"]]
#convos = convos[convos.TO=='Timothy Clarke'].dropna().reset_index(drop=True)
#convos

# Who has been talking to you over the years? This indicates strength of connection. Eventually I need to do something with this.

#convo_from = convos.groupby('FROM')['TO'].count().reset_index()
#convo_from.sort_values('TO', ascending=False).head(50)
#.sort_values('TO', ascending=False)