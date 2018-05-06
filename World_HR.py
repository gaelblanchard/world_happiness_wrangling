#Gael Blanchard
#Basic Data Wrangling with Python
#Data: World Happiness Report from Kaggle.com
#Required Libraries
from pyexcel.cookbook import merge_all_to_a_book
import pyexcel.ext.xlsx
import glob
import xlrd
from xlrd.sheet import ctype_text
import agate
import agatestats
import numpy
import matplotlib.pyplot as plt

#We will combine all our csvs into a workbook which we will then use for our data wrangling
merge_all_to_a_book(glob.glob("/path/to/worldhappiness/reportfolder/*.csv"),"output.xlsx")
#uses our created workbook
workbook = xlrd.open_workbook("output.xlsx")
#Test:
#print(workbook.nsheets)
#print(workbook.sheet_names())

# selects which sheet we want to use. Corresponds to 2015.csv
sheet = workbook.sheets()[0]

#Test:
#print(sheet.nrows)
#sheet.row_values(0)

#for row in range(sheet.nrows):
#	print(row, sheet.row(row))

#Retrwive titles from header of our csv file
title_rows = zip(sheet.row_values(0))

titles = [title[0] for title in title_rows]

#Test:
#print(titles)

#Gets all the data from the 2015 World Happiness Report
country_hs_rows = [sheet.row_values(row) for row in range(1,159)]

#Test:
#print(country_hs_rows)

#Assign agate types based on the type of data we have
text_type = agate.Text()
number_type = agate.Number()

example_row = sheet.row(6)
#print(example_row[2].ctype)
#print(example_row[2].value)
#print(ctype_text)

types = []
for value in example_row:
	value_type = ctype_text[value.ctype]
	if value_type == 'text':
		types.append(text_type)
	elif value_type == 'number':
		types.append(number_type)
	else:
		types.append(text_type)

#
world_happiness_table = agate.Table(country_hs_rows,titles,types)
world_happiness_table.print_table(max_columns=7)

country_happiness_scores = world_happiness_table.order_by('Country', reverse=True).limit(10)
for country in country_happiness_scores:
	print(country)

happiness_score_mean = world_happiness_table.aggregate(agate.Mean('Happiness Score'))
print(happiness_score_mean)

country_high_happiness = world_happiness_table.where(lambda r: r['Happiness Score'] > 7)
for country in country_high_happiness:
	print(country)

first_country_under_three = world_happiness_table.find(lambda r: r['Happiness Score'] < 3)
print(first_country_under_three)

#calculate the correlation between Happiness Score and Dystopia Residual
correlation = numpy.corrcoef(
		[float(value) for value in world_happiness_table.columns["Happiness Score"].values()],
		[float(compare_value) for compare_value in world_happiness_table.columns["Dystopia Residual"].values()]
	)[0,1]
print(correlation)

# Removes the outliers we have in our table using agatestats builtin function stdev_outliers() method
agatestats.patch()
std_dev_outliers_HS = world_happiness_table.stdev_outliers('Happiness Score', deviations = 3, reject = False)
#Test:
#print(len(std_dev_outliers_HS))

group_by_region = world_happiness_table.group_by('Region')

happiness_by_region = group_by_region.aggregate([('mean_happiness',agate.Mean('Happiness Score')),('mean_dystopia',agate.Mean('Dystopia Residual'))])
happiness_by_region.print_table()

region_correlation = numpy.corrcoef(
	[float(value) for value in happiness_by_region.columns["mean_happiness"].values()],
	[float(value2) for value2 in happiness_by_region.columns["mean_dystopia"].values()]
	)[0,1]
print(region_correlation)

#Graphs the correlation between happiness and dystopia when happiness is calcualted based on region
#Rather than country
plt.plot(happiness_by_region.columns["mean_happiness"],happiness_by_region.columns["mean_dystopia"])

plt.xlabel("Happiness Score(by Region)")
plt.ylabel("Dystopia Residual(by Region)")
plt.title("Correlation between Happiness and Dystopia")
plt.show()