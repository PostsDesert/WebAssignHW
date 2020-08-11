from selenium	import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from dateutil.parser import parse
from dateutil.tz import gettz
from datetime import timedelta, datetime
from ics import Calendar, Event
import time
import os

#Given a Webassign course page return homework
#Return list in format {'assignment':'datetime '}
def get_hw(selenium, course):
	name = selenium.find_elements_by_xpath("//*[@id='js-student-myAssignmentsWrapper']/section/ul/li/a/div[1]/span")
	print("**NAME**")
	print(name[0].text)
	due = selenium.find_elements_by_xpath("//*[@id='js-student-myAssignmentsWrapper']/section/ul/li/a/div[3]")
	link = selenium.find_elements_by_xpath("//*[@id='js-student-myAssignmentsWrapper']/section/ul/li/a")
	hw = list(zip([option.text for option in name], [option.text for option in due], [option.get_attribute('href') for option in link]))
	return hw

#Returns compiled list of homework of all classes
def all_homework(auth_url, homepage_url, user, pwd):
	try:
		options = webdriver.ChromeOptions()
		options.add_argument('window-size=1200x600')
		options.add_argument('headless')
		selenium = webdriver.Chrome(chrome_options=options)
		selenium.get(auth_url)
		selenium.implicitly_wait(5)

		#Sends username and pass
		userfield=selenium.find_element_by_id("email").send_keys(user)
		pwdfield= selenium.find_element_by_id("cengagePassword").send_keys(pwd)
		time.sleep(3)
		selenium.get(homepage_url)
	except:
		
		print('Could Not Connect')
		exit()

	#Counter index for list of classes as first two options aren't courses
	class_num = 1

	homework={}

	#Loops thru dropdown menu
	while(True):
			select = selenium.find_element_by_id('courseSelect') #Gathers array of courses
			options = select.find_elements_by_tag_name("option") #Gets lenght for break
			print("**OPTIONS**")
			print(options[class_num].text)
			course=options[class_num].text
			if len(options)>=1: 
				options[class_num].click()
				selenium.find_element_by_css_selector('#js-page-top > div > div > div:nth-child(1) > nav > div > button').click()
			else: 
				break
			homework[course]=get_hw(selenium,course) #stores assingments in form of {'class':{'hw','due'}}
			class_num += 1
			selenium.back()
			if(class_num > len(options)-1): break
	selenium.close()
	return homework


start_time = datetime.now()

#Read user and pass from file
file = open('account.key','r')
key = file.readlines()
auth_url     = key[0].replace('auth_url=','')
homepage_url = key[1].replace('homepage_url=','')
user	     = key[2].replace('user=','')
pwd	     = key[3].replace('pass=','')
tz	     = key[4].replace('timezone=','')
directory_to_write = key[5].replace('directory=','')
file.close()

homework = all_homework(auth_url, homepage_url, user, pwd) #Grabs all homework onto list

cal = Calendar()

for course, assignment in homework.items():
	print(course)
	print(assignment)
	for homework, due, link in assignment:
		time = parse(due).astimezone(gettz(tz))
		print('{} {} {} {}'.format(homework, due, time, link))
		e = Event(name=homework, begin=time-timedelta(hours=1), end=time, duration=None, description=course, created=None, last_modified=None, location=link, url=None, transparent=None, alarms=None, attendees=None, categories=None, status=None, organizer=None, geo=None, classification=None)
		cal.events.add(e)


with open(os.path.join(directory_to_write, 'WebAssign.ics'), "w") as f:
    f.writelines(cal)

end_time = datetime.now() - start_time
print(end_time)
