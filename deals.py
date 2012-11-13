import re
import urllib2
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Unicode
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

engine = create_engine('sqlite:///sd.sqlite', echo=False)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

class Deal(Base):
	__tablename__ = 'deals'
	
	id = Column(Integer, primary_key=True)
	title = Column(String)
	thread_id = Column(String)
	create_date = Column(DateTime)
	
	def __init__(self, thread_id, title, create_date):
		self.thread_id = thread_id
		self.title = title
		self.create_date = create_date
	
	def __repr__(self):
		return "<Deal: %s / %s" % (self.title, str(self.create_date))

Base.metadata.create_all(engine) 

def parse_date(date):
	date = re.sub("(?si)<.*?>", "", date)
	date = re.sub("(?si)[\r\n]", "", date)
	date = re.sub(r"(?i)\s+", " ", date)
	
	if re.search("Today", date):
		today = datetime.today().strftime("%m-%d-%Y")
		date = re.sub("Today", today, date)
	if re.search("Yesterday", date):
		yesterday = (datetime.today() - timedelta(1)).strftime("%m-%d-%Y")
		date = re.sub("Yesterday", yesterday, date)
	
	date = date.strip()
	date_format = "%m-%d-%Y %I:%M %p"
	return datetime.strptime(date, date_format)

if __name__ == "__main__":
	deals = []
	response = urllib2.urlopen('http://slickdeals.net/forums/forumdisplay.php?f=9')
	html = response.read()
	for match_deal in re.finditer(r'(?si)<tr id="sdpostrow_\d+">.*?</tr>', html):
		deal_html = match_deal.group()
		match = re.search(r'<a href="[^<]+id="thread_title_(\d+)">(.*?)</a>', deal_html, re.DOTALL | re.IGNORECASE)
		thread_id = match.group(1)
		thread_title = match.group(2)
		
		thread_title = re.sub("[^ -~]", "", thread_title)
	
		match = re.search(r"<!-- Post Date -->\s*<td[^<]+>\s+<div[^<]+>(.*?)</span>", deal_html, re.DOTALL | re.IGNORECASE)
		thread_date = parse_date(match.group(1))
		
		d = Deal(thread_id, thread_title, thread_date)
		session.add(d)
		print d.thread_id

	session.commit()
		