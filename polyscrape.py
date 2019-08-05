# Webscraper to extract all professor & review data from polyratings.com

from bs4 import BeautifulSoup
from requests import get
import pandas as pd
import numpy as np
import time
from time import sleep
from random import randint
from warnings import warn

# Lists to store the professor data in
professor_names = []
professor_ratings = []
departments = []
evaluation_counts = []
rec_student_diffs = []
presents_mat_clearlys = []
class_standings = []
reasons = []
reviews = []
grades = []
dates = []

professor_pages = [str(i) for i in range(1, 4300)]

# Preparing the monitoring of the loop
start_time = time.time()
requests = 0

# For every professor's page in all pages
for professor_page in professor_pages:
	#Make a request
	response = get('http://polyratings.com/eval.php?profid=' + professor_page)
	# Pause the loop
	#sleep(randint(1, 2))
	# Monitor the requests
	requests += 1
	elapsted_time = time.time() - start_time
	# Throw a warning for non 200 response codes
	if response.status_code != 200:
		warn('Request: {}; Status code: {}'.format(requests, response.status_code))
	# Parse the content of the request with BeautifulSoup
	page_html = BeautifulSoup(response.text, 'html.parser')
	# Check to see if professor page is Valid
	if page_html.find('div', class_ = 'row eval-header') is not None:
		# Select all the reviews of the professor
		review_containers = page_html.find_all('div', class_ = 'col-xs-12 item-padding')
		# Get professor Data
		professor = page_html.find('div', class_ = 'row eval-header')
		# Professor name
		name = professor.find('h1', class_ = 'text-primary').text
		name = name.strip()
		department = ""
		# Ensure department data exists
		if len(professor.find_all('h4')) >= 2:
			department = professor.find_all('h4')[1].text
			department = department.strip()
		# Rating
		rating = str(professor.find('h2', class_ = 'text-primary').text)
		if "N/A" not in rating:
			rating = rating[:-5]
			rating = float(rating.strip())
		else:
			rating = None
		# Number of evaluations
		num_evals = professor.find_all('b')[0].text
		num_evals = num_evals.strip()
		# Handle all variations of the evaluation count
		if "evaluations" in num_evals:
			num_evals = num_evals.replace('evaluations', '')
		elif "evaluation" in num_evals:
			num_evals = num_evals.replace('evaluation', '')
		else:
			num_evals = None
		num_evals = int(num_evals)
		# 'Recognizes Student Difficulty' rating
		rec_stdnt_diff = professor.find_all('b')[1].text
		if "N/A" not in rec_stdnt_diff:
			rec_stdnt_diff = float(rec_stdnt_diff[33:])
		else:
			rec_stdnt_diff = None
		# 'Presents Material Clearly' rating
		presents_mat_clearly = professor.find_all('b')[2].text
		if "N/A" not in presents_mat_clearly:
			presents_mat_clearly = float(presents_mat_clearly[27:])
		else:
			presents_mat_clearly = None
		# Get list of review data
		review_containers = page_html.find_all('div', class_ = 'col-xs-12 item-padding')
		r_num = 0
		# For every review of all reviews of the professor
		for review in range(len(review_containers)):
			# Get individual review data
			review = review_containers[r_num]
			text = review.find('div', class_ = 'col-xs-9 col-sm-10 eval-comment').text
			text = text.strip()
			grade = review.find('div', class_ = 'col-xs-3 col-sm-2 eval-info').contents[2]
			grade = grade.strip()
			date = review.find('div', class_ = 'col-xs-3 col-sm-2 eval-info').contents[6]
			date = date[1:]
			date = date.strip()
			standing = review.find('div', class_ = 'col-xs-3 col-sm-2 eval-info').contents[0]
			standing = standing[1:]
			standing = standing.strip()
			degree_requirement = review.find('div', class_ = 'col-xs-3 col-sm-2 eval-info').contents[4]
			degree_requirement = degree_requirement[1:]
			# Append data to lists
			professor_names.append(name)
			professor_ratings.append(rating)
			departments.append(department)
			evaluation_counts.append(num_evals)
			rec_student_diffs.append(rec_stdnt_diff)
			presents_mat_clearlys.append(presents_mat_clearly)
			class_standings.append(standing)
			reasons.append(degree_requirement)
			reviews.append(text)
			grades.append(grade)
			dates.append(date)
			r_num += 1
	print("Page complete. Elapsed time:", elapsted_time)

# Maps data to pandas DataFrame
professor_data = pd.DataFrame({
	'professor_name': professor_names,
	'department': departments,
	'rating': professor_ratings,
	'num_evals': evaluation_counts,
	'recognizes_stud_diff': rec_student_diffs,
	'presents_mat_clearly': presents_mat_clearlys,
	'review': reviews,
	'grade_received': grades,
	'date': dates,
	'class_standing': class_standings,
	'reason': reasons
	})

print(professor_data.info())
# Exports data to csv
professor_data.to_csv('polyratings.csv')