import psycopg2
import sys
import pprint
import os
import numpy as np
import matplotlib.pyplot as plt
import plotly.plotly as py
from collections import Counter
import unicodedata
# from tableRenderer import *
import logging
from lpod.document import *
from lpod.element import *
from lpod.style import *
from lpod.table import *
from lpod.frame import *
from lpod.draw_page import *


class Organizer():
	def __init__(self , orderList):
		pass
	pass

class Category():
	def __init__(self , markdownFile , clientId , contractList , period , conn):
		self.markdownFile = markdownFile
		self.clientId = clientId
		self.contractList = contractList
		self.period = period
		self.conn = conn

class Category_Client(Category):
	def __init__(self , markdownFile , clientId , contractList , period , conn):
		Category.__init__(self , markdownFile , clientId , contractList , period , conn)

	def initValues(self):
		self.queries=InitQueriesContract(self.clientId , self.contractList)
		self.queries.setQueries()
		self.cursor=TaskExecutor(self.queries.listQueries  , self.conn)
		self.cursor.executeTasks()
		self.cursor.fetchValues()
		self.values = self.cursor.fetchedValues


	def fillSlide(self):
		self.markdownFile.new_slide("**Le client :**"+str(self.values[0][0][0]))
		# print self.values
		self.markdownFile.writeText("* **Nom du client :** "+str(self.values[0][0][0]))
		self.markdownFile.writeText("* **Client depuis :** "+str(self.values[0][1][0]))

		for i in range(0 , len(self.contractList)):
			self.markdownFile.new_slide("**Contrat :**"+ str(self.values[1][i][0]))
			self.markdownFile.writeText("* **Nom du Contrat :** "+str(self.values[1][i][0]))
			self.markdownFile.writeText("* **Description du contrat :** "+str(self.values[1][i][1]))
			self.markdownFile.writeText("* **Debut du contrat :** "+str(self.values[1][i][2]))
			self.markdownFile.writeText("* **Fin de contrat :** "+str(self.values[1][i][3]))
			self.markdownFile.writeText("* **Logiciel :** "+str(self.values[1][i][4]))
			self.markdownFile.writeText("* **Version :** "+str(self.values[1][i][5]))			

class Category_Flow(Category):
	def __init__(self , markdownFile , clientId , contractList , period):
		Category.__init__(markdownFile , clientId , contractList , period)

class Category_Division(Category):
	def __init__(self , markdownFile , clientId , contractList , period):
		Category.__init__(markdownFile , clientId , contractList , period)

class Category_Resolution(Category):
	def __init__(self , markdownFile , clientId , contractList , period):
		Category.__init__(markdownFile , clientId , contractList , period)


class Category_Evolution(Category):
	def __init__(self , markdownFile , clientId , contractList , period):
		Category.__init__(markdownFile , clientId , contractList , period)


class Category_Demands(Category):
	def __init__(self , markdownFile , clientId , contractList , period):
		Category.__init__(markdownFile , clientId , contractList , period)


class Category_Synthesis(Category):
	def __init__(self , markdownFile , clientId , contractList , period):
		Category.__init__(markdownFile , clientId , contractList , period)	

class Category_Evolution(Category):
	def __init__(self , markdownFile , clientId , contractList , period):
		Category.__init__(markdownFile , clientId , contractList , period)

class Category_Clos_Open(Category):
	def __init__(self , markdownFile , clientId , contractList , period):
		Category.__init__(markdownFile , clientId , contractList , period)



class InitQueries():
	def __init__(self , clientId , contractList):
		self.listQueries = []
		self.clientId = clientId
		self.contractList = contractList

class InitQueriesContract(InitQueries):
	def __init__(self , clientId , contractList):
		InitQueries.__init__(self  , clientId , contractList)
		

		self.customer = []
		self.contract = []
		self.listQueries.append(self.customer)
		self.listQueries.append(self.contract)

	def setQueries(self):
		self.customer_name = ["SELECT name  FROM customer WHERE id = "+str(self.clientId)+" ;"]
		self.customer_since = ["SELECT creation_date::timestamp::date FROM customer WHERE id = "+str(self.clientId)+" ;"]
		self.customer.append(self.customer_name)
		self.customer.append(self.customer_since)
		for i in range(0 , len(self.contractList)):
			self.contract.append([])
			self.contract[i].append("SELECT name FROM contract WHERE id = "+str(self.contractList[i])+" ;")
			self.contract[i].append("SELECT description FROM contract WHERE id = "+str(self.contractList[i])+" ;")
			self.contract[i].append("SELECT start_date::timestamp::date FROM contract WHERE id = "+str(self.contractList[i])+" ;")
			self.contract[i].append("SELECT end_date::timestamp::date FROM contract WHERE id = "+str(self.contractList[i])+" ;")
			self.contract[i].append("SELECT sf.name FROM software sf INNER JOIN contract_software_version csv ON csv.software_id = sf.id where csv.contract_id = "+str(self.contractList[i])+" limit 22;")
			self.contract[i].append("SELECT sv.name from software_version sv inner join contract_software_version csv on csv.software_id = sv.software_id and csv.contract_id = "+str(self.contractList[i])+" limit 22;")
		

class InitQueriesFlow(InitQueries):
	def __init__(self , clientId , contractList , period):
		InitQueries.__init__(self  , clientId , contractList)
		self.period = int(period)
		self.static_query="select count(issue_type) from statistic_ticket where (select extract (year from (select age(current_date , creation_date)))) = 0 and (select extract (month from (select age( current_date , creation_date)))) ="
	def setQueries(self):
		for i in range(0 , self.period):
			self.listQueries.append([])
			for j in range(0 , len(self.contractList)):
				self.listQueries[i].append([])
				self.listQueries[i][j].append(self.static_query+str(i)+" and contract_id = "+str(self.contractList[j])+" and issue_type like '%information%' ;")				
				self.listQueries[i][j].append(self.static_query+str(i)+" and contract_id = "+str(self.contractList[j])+" and (issue_type like '%anomalie%' or issue_type like '%Anomalie%') ;")
				self.listQueries[i][j].append(self.static_query+str(i)+" and contract_id = "+str(self.contractList[j])+" and issue_type not like '%anomalie%' and issue_type not like '%Anomalie%' and issue_type not like '%information%' ;")
				self.listQueries[i][j].append("select extract(month from (select current_date - interval '"+str(i)+" month')) ;")	


class InitQueriesDivision(InitQueries):
	def __init__(self , clientId , contractList , period):
		InitQueries.__init__(self  , clientId , contractList)
		self.period = period
		self.static_query = "select count(issue_severity) from statistic_ticket where (select extract (year from (select age(current_date , creation_date)))) = 0 and (select extract (month from (select age( current_date , creation_date)))) = "

	def setQueries(self):
		for i in range(0 , self.period):
			self.listQueries.append([])
			for j in range(0 , len(self.contractList)):
				self.listQueries[i].append([])
				self.listQueries[i][j].append(self.static_query+str(i)+" and contract_id = "+str(self.contractList[j])+" and issue_severity like '%Mineure%' ;")
				self.listQueries[i][j].append(self.static_query+str(i)+" and contract_id = "+str(self.contractList[j])+" and issue_severity like '%Majeure%' ;")
				self.listQueries[i][j].append(self.static_query+str(i)+" and contract_id = "+str(self.contractList[j])+" and (issue_severity ='Bloquante' or issue_severity='3 anomalie bloquante') ;")


class InitQueriesNegativeResolution(InitQueries):
	def __init__(self , clientId , contractList , period):
		InitQueries.__init__(self  , clientId , contractList)
		self.period = int(period)
		self.static_query = " from statistic_ticket st inner join contract ct on ct.id = st.contract_id where st.close_date is not null and (st.fix_sla_target < st.fix_duration) and (select extract (year from (select age(current_date , ct.creation_date)))) = 0 and (select extract (month from (select age( current_date , ct.creation_date)))) = "
	
	def setQueries(self):
		for i in range(0 , self.period):
			self.listQueries.append([])
			for j in range(0 , len(self.contractList)):
				self.listQueries[i].append([])
				self.listQueries[i][j].append("select count(st.issue_type) "+self.static_query+str(i)+" and st.issue_type like '%information' and contract_id = "+str(self.contractList[j])+" ;")
				self.listQueries[i][j].append("select count(st.issue_severity) "+self.static_query+str(i)+" and st.issue_severity like '%Mineure' and contract_id = "+str(self.contractList[j])+" ;")
				self.listQueries[i][j].append("select count(st.issue_severity) "+self.static_query+str(i)+" and st.issue_severity like '%Majeure' and contract_id = "+str(self.contractList[j])+" ;")
				self.listQueries[i][j].append("select count(st.issue_severity) "+self.static_query+str(i)+" and (issue_severity ='Bloquante' or issue_severity='3 anomalie bloquante')  and contract_id = "+str(self.contractList[j])+" ;")


class InitQueriesPositiveResolution(InitQueries):
	def __init__(self , clientId , contractList , period):
		InitQueries.__init__(self  , clientId , contractList)
		self.period = int(period)
		self.static_query = " from statistic_ticket st inner join contract ct on ct.id = st.contract_id where st.close_date is not null and (st.fix_sla_target >= st.fix_duration) and (select extract (year from (select age(current_date , ct.creation_date)))) = 0 and (select extract (month from (select age( current_date , ct.creation_date)))) = "
	
	def setQueries(self):
		for i in range(0 , self.period):
			self.listQueries[i].append([])
			for j in range(0 , len(self.contractList)):
				self.listQueries[i][j].append("select count(st.issue_type) "+self.static_query+str(i)+" and st.issue_type like '%information' and st.contract_id = "+str(self.contractList[j])+" ;")
				self.listQueries[i][j].append("select count(st.issue_severity) "+self.static_query+str(i)+" and st.issue_severity like '%Mineure' and st.contract_id = "+str(self.contractList[j])+" ;")
				self.listQueries[i][j].append("select count(st.issue_severity) "+self.static_query+str(i)+" and st.issue_severity like '%Majeure' and st.contract_id = "+str(self.contractList[j])+" ;")
				self.listQueries[i][j].append("select count(st.issue_severity) "+self.static_query+str(i)+" and (st.issue_severity ='Bloquante' or st.issue_severity='3 anomalie bloquante')  "+str(self.contractList[j])+" ;")


class InitQueriesSynthesis(InitQueries):
	def __init__(self , clientId , contractList , period):
		InitQueries.__init__(self  , clientId , contractList)
		self.period= int(period)
		self.static_query = " from statistic_ticket st inner join contract ct on ct.id = st.contract_id where st.close_date is not null and (st.fix_sla_target < st.fix_duration) and (select extract (year from (select age(current_date , ct.creation_date)))) = 0 and (select extract (month from (select age( current_date , ct.creation_date)))) = "


	def setInformation_Queries(self):		
		self.queriesInformation = []
		for i in range(0, self.period):
			self.queriesInformation.append([])
			for j in range(0 , len(self.contractList)):
				self.queriesInformation[i].append([])
				self.queriesInformation[i][j].append("select count(st.issue_type) "+self.static_query+str(i)+" and st.issue_type like '%information' and st.fix_in_progress = 't' and st.contract_id = "+str(self.contractList[j])+" ;")
				self.queriesInformation[i][j].append("select count(st.issue_type) "+self.static_query+str(i)+" and st.issue_type like '%information' and st.waiting_for_customer = 't' and st.contract_id = "+str(self.contractList[j])+" ;")
				self.queriesInformation[i][j].append("select count(st.issue_type) "+self.static_query+str(i)+" and st.issue_type like '%information' and  st.close_date is not null and st.contract_id = "+str(self.contractList[j])+" ;")
				self.queriesInformation[i][j].append("select count(st.issue_type) "+self.static_query+str(i)+" and st.issue_type like '%information' and (st.fix_in_progress = 't' or st.waiting_for_customer = 't' or st.close_date is not null) and st.contract_id = "+str(self.contractList[j])+" ;")
		

	def set_Anom_Min_Queries(self):
		self.queriesAnoMin = []
		for i in range(0, self.period):
			self.queriesAnoMin.append([])
			for j in range(0 , len(self.contractList)):
				self.queriesAnoMin[i].append([])
				self.queriesAnoMin[i][j].append("select count(st.issue_severity) "+self.static_query+str(i)+" and st.issue_severity like '%Mineure' and st.fix_in_progress = 't' and st.contract_id = "+str(self.contractList[j])+" ;")
				self.queriesAnoMin[i][j].append("select count(st.issue_severity) "+self.static_query+str(i)+" and st.issue_severity like '%Mineure' and st.waiting_for_customer = 't' and st.contract_id = "+str(self.contractList[j])+" ;")
				self.queriesAnoMin[i][j].append("select count(st.issue_severity) "+self.static_query+str(i)+" and st.issue_severity like '%Mineure' and  st.close_date is not null and st.contract_id = "+str(self.contractList[j])+" ;")
				self.queriesAnoMin[i][j].append("select count(st.issue_severity) "+self.static_query+str(i)+" and st.issue_severity like '%Mineure' and (st.fix_in_progress = 't' or st.waiting_for_customer = 't' or st.close_date is not null) and st.contract_id = "+str(self.contractList[j])+" ;")
	def setAnom_Maj_Queries(self):
		self.queriesAnoMaj = []
		for i in range(0, self.period):
			self.queriesAnoMaj.append([])
			for j in range(0 , len(self.contractList)):
				self.queriesAnoMaj[i].append([])
				self.queriesAnoMaj[i][j].append("select count(st.issue_severity) "+self.static_query+str(i)+" and st.issue_severity like '%Majeure' and st.fix_in_progress = 't' and st.contract_id = "+str(self.contractList[j])+" ;")
				self.queriesAnoMaj[i][j].append("select count(st.issue_severity) "+self.static_query+str(i)+" and st.issue_severity like '%Majeure' and st.waiting_for_customer = 't' and st.contract_id = "+str(self.contractList[j])+" ;")
				self.queriesAnoMaj[i][j].append("select count(st.issue_severity) "+self.static_query+str(i)+" and st.issue_severity like '%Majeure' and  st.close_date is not null and st.contract_id = "+str(self.contractList[j])+" ;")
				self.queriesAnoMaj[i][j].append("select count(st.issue_severity) "+self.static_query+str(i)+" and st.issue_severity like '%Majeure' and (st.fix_in_progress = 't' or st.waiting_for_customer = 't' or st.close_date is not null) and st.contract_id = "+str(self.contractList[j])+" ;")
	
	def setBlock_Queries(self):
		self.queriesBlock = []
		for i in range(0, self.period):
			self.queriesBlock.append([])
			for j in range(0 , len(self.contractList)):
				self.queriesBlock[i].append([])
				self.queriesBlock[i][j].append("select count(st.issue_severity) "+self.static_query+str(i)+" and (st.issue_severity ='Bloquante' or st.issue_severity='3 anomalie bloquante') and st.fix_in_progress = 't' and st.contract_id = "+str(self.contractList[j])+" ;")
				self.queriesBlock[i][j].append("select count(st.issue_severity) "+self.static_query+str(i)+" and (st.issue_severity ='Bloquante' or st.issue_severity='3 anomalie bloquante') and st.waiting_for_customer = 't' and st.contract_id = "+str(self.contractList[j])+" ;")
				self.queriesBlock[i][j].append("select count(st.issue_severity) "+self.static_query+str(i)+" and (st.issue_severity ='Bloquante' or st.issue_severity='3 anomalie bloquante') and  st.close_date is not null and st.contract_id = "+str(self.contractList[j])+" ;")
				self.queriesBlock[i][j].append("select count(st.issue_severity) "+self.static_query+str(i)+" and (st.issue_severity ='Bloquante' or st.issue_severity='3 anomalie bloquante') and (st.fix_in_progress = 't' or st.waiting_for_customer = 't' or st.close_date is not null) and st.contract_id = "+str(self.contractList[j])+" ;")

	def setOther_Queries(self):
		self.queriesOthers = []
		self.static_other_query = "select count(issue_type) from statistic_ticket where (select extract (year from (select age(current_date , creation_date)))) = 0 and (select extract (month from (select age( current_date , creation_date)))) ="
		self.static_condition ="  and issue_type not like '%anomalie%' and issue_type not like '%Anomalie%' and issue_type not like '%information%' ;"
		for i in range(0, self.period):
			self.queriesBlock.append([])
			for j in range(0 , len(self.contractList)):
				self.queriesBlock[i].append([])
				self.queriesOthers[i][j].append(self.static_other_query+str(i)+" and st.fix_in_progress = 't' and st.contract_id = "+str(self.contractList[j])+self.static_condition)
				self.queriesOthers[i][j].append(self.static_other_query+str(i)+" and st.waiting_for_customer = 't' and st.contract_id = "+str(self.contractList[j])+self.static_condition)
				self.queriesOthers[i][j].append(self.static_other_query+str(i)+" and st.close_date is not null and st.contract_id = "+str(self.contractList[j])+self.static_condition)
				self.queriesOthers[i][j].append(self.static_other_query+str(i)+" and (st.fix_in_progress = 't' or st.waiting_for_customer = 't' or st.close_date is not null) and st.contract_id = "+str(self.contractList[j])+self.static_condition)




class TaskExecutor():
	def __init__(self , queries , conn ):
		self.nbrTypes = len(queries)
		self.queries = queries
		self.conn = conn
		self.resultTable = []
		self.conn = conn

	def testing(self):
		self.t = self.conn.cursor()
		print self.queries[0][0][0]
		# self.t.execute(self.queries[0][0][0])


	def executeTasks(self):
		for i in range(0 , len(self.queries)):
			self.resultTable.append([])
			for j in range(0, len(self.queries[i])):
				self.resultTable[i].append([])
				for k in range(0 , len(self.queries[i][j])):
					# print self.queries[i][j][k]
					self.resultTable[i][j].append(self.conn.cursor())
					self.resultTable[i][j][k].execute(self.queries[i][j][k])


	def fetchValues(self):
		self.fetchedValues = []
		for i in range(0 , len(self.resultTable)):
			self.fetchedValues.append([])
			for j in range(0 , len(self.resultTable[i])):
				self.fetchedValues[i].append([])
				for k in range(0 , len(self.resultTable[i][j])):
					# print "jexecute le fetchvalues"
					try:

						self.fetchedValues[i][j].append(self.resultTable[i][j][k].fetchone()[0])
						print self.fetchedValues[i][j][k]
					except TypeError:
						self.fetchedValues[i][j].append( "Champ mal rempli")
						print self.fetchedValues[i][j][k]
						logging.error("Query "+self.queries[i][j][k]+" failed !")

class PieChartsGenerator():
	def __init__(self ,title ,titles,  values ):
		self.titles = titles
		self.values = values
		self.title = title

	def setValues(self):
		pass

	def createPieCharte(self):
		explode=(0 , 0)
		figure , ax = plt.subplots()
		ax.pie(self.values , explode=explode , labels = self.titles , autopct = '%1.1f%%', shadow=True , startangle=90)
		ax.axis('equal')		

	def savePieChart(self):
		plt.savefig(str(self.title)+"resolution.svg")



class HistogramGenerator():
	def __init__(self ,title , values ):
		self.title = title
		self.values = values
		self.ticket_dict = {}
		
	def setTitles(self):
		self.ticket_dict["Information"] = self.values[0]
		self.ticket_dict["Mineure"]=self.values[1]
		self.ticket_dict["Majeure"]=self.values[2]
		self.ticket_dict["Bloquante"]=self.values[3]
		self.ticket_dict["Autre"]=self.values[4]

	def create_histogram(self):
		figure = plt.figure()
		ax = figure.add_subplot(111)

		frequencies = self.ticket_dict.values()
		names = self.ticket_dict.keys()

		x_coordinates = np.arange(len(self.ticket_dict))
		ax.bar(x_coordinates , frequencies , align='center')

		ax.xaxis.set_major_locator(plt.FixedLocator(x_coordinates))
		ax.xaxis.set_major_formatter(plt.FixedFormatter(names))

	def saveFigure(self):
		plt.savefig("flow"+str(self.title)+".svg")



class ExterneTablesGenerator():
	def __init__(self  , title , titlesRow , titlesColumn , values , path , id):
		self.title = title
		self.values = values
		self.titlesRow = titlesRow
		self.titlesColumn = titlesColumn
		self.values = values
		self.id = str(id)
		self.path = path
	def recoverTemplate(self):	
		try:
			self.doc = odf_get_document(str(self.path))
			self.context = self.doc.get_body()
		except:
			logging.error("can't recover or open template "+str(self.path))

	def createPage(self):
		self.page = odf_create_draw_page(page_id = "p"+self.id , name="page"+str(id))
	def create_table(self):
		self.tab = odf_create_table("table"+str(id) , width=len(self.titlesColumn)+1 , height = len(self.titlesRow)+1)
	
	
	def set_val(self , i , j , value):
		self.tab.set_value((i , j) , str(value))

	def fill_cells(self):
		#fill row titles
		for i in range(1 , len(self.titlesColumn)+1):
			self.set_val(i , 0 , self.titlesColumn[i-1])
		#fill column titles
		for j in range(1 , len(self.titlesRow)+1):
			self.set_val(0 , j , self.titlesRow[j-1])
		#fill values
		for i in range(1 , len(self.titlesColumn)+1):
			for j in range(1 , len(self.titlesRow)+1):
				self.set_val(i , j , self.values[i-1][j-1])
	
	def merge(self):
		self.frame = odf_create_frame(name = u"frame"+str(id) , size=('22cm' , '7.2cm') , position = ('2.3cm' , '4.5cm'))
		self.frame.append(self.tab)
		self.page.append(self.frame)
		self.context.insert(self.page , 1)
	
	def savePresentation(self):
		self.doc.save(target=str(self.id)+"report.odp" , pretty="false")

class LineChartGenerator():
	def __init__(self , title ,xLabel , yLabel, values):
		self.title = title
		self.xLabel = xLabel
		self.yLabel = yLabel
		self.values = values

	def createLineChart(self):
		plt.plot(self.values[0] , self.values[1])
		plt.title(self.title)
		plt.xlabel(self.xLabel)
		plt.ylabel(self.yLabel)
	def saveLineChart(self):
		plt.savefig(title+".svg")

class markdownGenerator():
	def __init__(self , file):
		try:
			self.file = open(str(file)+".md" , "w")		
		except:
			logging.error("Can't open file "+str(file)+".md")
	
	def new_slide(self , title):
		self.file.write("## "+title)
		self.end_line()
	def end_line(self):
		self.file.write("\n \n")
	
	def img_insert(self ,name, link , title):
		self.new_slide(title)
		self.file.write("!["+name+"]("+link+")")
		self.end_line()
	
	def writeText(self , text):
		self.file.write(text)
		self.end_line()

class ConnectionDB():
	def __init__(self , user , password , database , host):
		self.user = user
		self.password = password
		self.database = database
		self.host = host

	def connection(self):
		try:
			conn_string = " host=" + self.host+ " dbname="+self.database+" user="+self.user+" password="+self.password+" "
			logging.info("Connecting to database succeeded")
			self.conn = psycopg2.connect(conn_string)
		except (Exception, psycopg2.DatabaseError) as error:
			logging.debug('Connection to database failed !')


def testExternal():
	test = ExterneTablesGenerator("test" , ["a" , "b"] , ["c" , "d"] , [["1" , "2"] , ["3" , "4"]] , "tmplt.odp" , "oiazy")	
	test.recoverTemplate()
	test.createPage()
	test.create_table()
	test.fill_cells()
	test.merge()
	test.savePresentation()	


if __name__ == "__main__":
	logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s' , datefmt='%m-%d %H:%M', filename='reporting.log', filemode='w')
	conn = ConnectionDB("tosca2dev", "tosca2dev" , "tosca2dev" , "tosca2.linagora.dc1")
	conn.connection()

	file = markdownGenerator("filetest")
	

	test = Category_Client(file , "1836" , ["12485" , "2104" , "77666" , "12491"] , 3 , conn.conn)
	test.initValues()
	test.fillSlide()
































