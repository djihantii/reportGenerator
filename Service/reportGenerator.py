import psycopg2
import sys
import pprint
import os
import numpy as np
import matplotlib.pyplot as plt
import plotly.plotly as py
from collections import Counter
import unicodedata
import logging
from lpod.document import *
from lpod.element import *
from lpod.style import *
from lpod.table import *
from lpod.frame import *
from lpod.draw_page import *
import yaml
from datetime import date , datetime
from dateutil.relativedelta import relativedelta
import pylab
import matplotlib
import matplotlib.dates



#####to move to config file#####
month_dict = {
	1 : "Janvier",
	2 : "Fevrier",
	3 : "Mars",
	4 : "Avril",
	5 : "Mai",
	6 : "Juin",
	7 : "Juillet",
	8 : "Aout",
	9 : "Septembre",
	10 : "Octobre",
	11 : "Novembre",
	12 : "Decembre"
	
}
##########

class Organizer():
	def __init__(self , preferences):
		pass
	pass
##########

class Organizer():
	def __init__(self , orderList):
		pass

class Category():
	def __init__(self , markdownFile , clientId , contractList , period , conn , data_conf):
		self.markdownFile = markdownFile
		self.clientId = clientId
		self.contractList = contractList
		self.period = period
		self.conn = conn
		self.data_conf = data_conf
class Category_Client(Category):
	def __init__(self , markdownFile , clientId , contractList , period , conn , data_conf):
		Category.__init__(self , markdownFile , clientId , contractList , period , conn , data_conf)

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
	def __init__(self , markdownFile , clientId , contractList , period , conn , data_conf):
		Category.__init__(self , markdownFile , clientId , contractList , period , conn , data_conf)

	def initValues(self):
		self.queries=InitQueriesFlow(self.clientId , self.contractList , self.period)
		self.queries.setQueries()
		self.cursor=TaskExecutor(self.queries.listQueries  , self.conn)
		self.cursor.executeTasks()
		self.cursor.fetchValues()
		self.values = self.cursor.fetchedValues

	def getSum(self , contrat , indice):
		result = 0
		for i in range(0 , len(contrat)):
			result = result + int(contrat[i][indice])
		# print result
		return result
	#Count the sum of distinct issues type per contract for each month
	def setValues(self):
		self.totalValues = []
		for i in range(0 , self.period):
			self.totalValues.append([])
			for j in range(0 , len(self.values[i][0])-1):
				self.totalValues[i].append([])
				# print self.getSum(self.values[i] , j)
				self.totalValues[i][j]= self.getSum(self.values[i] , j)

	def recoverMonths(self):
		listMonths = []
		for i in range(0 , len(self.values)):
			for j in range(0 , len(self.values[i])-1):
				listMonths.append(month_dict[int(self.values[i][j][4])])

		return listMonths

	def drawTable(self):
		self.table = ExterneTablesGenerator("tableFlow"  ,["information", "support" , "autre" , "total"],  self.recoverMonths() , self.totalValues ,"tmplt.odp" , "testTable")	
		self.table.recoverTemplate()
		self.table.createPage()
		self.table.create_table()
		# print len(self.table.titlesRow)
		# print len(self.table.titlesColumn)
		self.table.fill_cells()
		self.table.merge()
		self.table.savePresentation()


class Category_Division(Category):
	def __init__(self , markdownFile , clientId , contractList , period , conn , data_conf):
		Category.__init__(self , markdownFile , clientId , contractList , period , conn , data_conf)

	def initValues(self):
		self.queries=InitQueriesDivision(self.clientId , self.contractList , self.period)
		self.queries.setQueries()
		self.cursor=TaskExecutor(self.queries.listQueries  , self.conn)
		self.cursor.executeTasks()
		self.cursor.fetchValues()
		self.values = self.cursor.fetchedValues

	def getSum(self , contrat , indice):
		result = 0
		for i in range(0 , len(contrat)):
			result = result + int(contrat[i][indice])
		# print result
		return result
	#Count the sum of distinct issues type per contract for each month
	def setValues(self):
		self.totalSeverities = [0 , 0, 0, 0 ]
		self.totalValues = []
		for i in range(0 , self.period):
			self.totalValues.append([])
			for j in range(0 , len(self.values[i][0])-1):
				self.totalValues[i].append([])
				# print self.getSum(self.values[i] , j)
				self.totalValues[i][j]= self.getSum(self.values[i] , j)

		for i in range(0 , len(self.totalValues)):
			for j in range(0 , len(self.totalValues[i])-1):
				self.totalSeverities[j]=self.totalSeverities[j]+self.totalValues[i][j]
	def recoverMonths(self):
		listMonths = []
		for i in range(0 , len(self.values)):
			for j in range(0 , len(self.values[i])-2):
				listMonths.append(month_dict[int(self.values[i][j][5])])

		return listMonths

	def drawTable(self):
		self.table = ExterneTablesGenerator("table Division"  ,["Mineure", "Majeure" , "Bloquante" , "autre","total"],  self.recoverMonths() , self.totalValues ,"../templates/tmplt.odp" , "testTable" , self.data_conf)	
		self.table.recoverTemplate()
		self.table.createPage()
		self.table.create_table()
		# print len(self.table.titlesRow)
		# print len(self.table.titlesColumn)
		self.table.fill_cells()
		self.table.merge()
		self.table.savePresentation()

	def drawHistogram(self):
		histogram = HistogramGenerator("Repartition" , self.totalSeverities , ["Mineure" , "Majeure" , "Bloquante " , "Autres"])
		histogram.setTitles()
		histogram.create_histogram()
		histogram.saveFigure()



class Category_Resolution(Category):
	def __init__(self , markdownFile , clientId , contractList , period , conn , data_conf):
		Category.__init__(self , markdownFile , clientId , contractList , period , conn , data_conf)

	def setValues(self):
		self.negativeQueries=InitQueriesNegativeResolution(self.clientId , self.contractList , self.period)
		self.negativeQueries.setQueries()
		self.cursor=TaskExecutor(self.negativeQueries.listQueries  , self.conn)
		self.cursor.executeTasks()
		self.cursor.fetchValues()
		self.negativeValues = self.cursor.fetchedValues

		self.positiveQueries=InitQueriesPositiveResolution(self.clientId , self.contractList , self.period)
		self.positiveQueries.setQueries()
		self.cursor=TaskExecutor(self.positiveQueries.listQueries  , self.conn)
		self.cursor.executeTasks()
		self.cursor.fetchValues()
		self.positiveValues = self.cursor.fetchedValues
 	
 	def setPercentageResolutions(self):
 		self.percentages = [0 , 0 , 0 ,0]
 		for i in range(0 , len(self.percentages)):
 			self.percentages[i]=self.totalPositiveValues[i]*100/(self.totalPositiveValues[i]+self.totalNegativeValues[i])

 	def setSumtickets(self):
 		self.totalPositiveValues = [0 , 0 , 0 , 0]
 		self.totalNegativeValues = [0 , 0 , 0 , 0]
 		self.totalValues = [0 , 0 , 0 , 0]
 		for i in range(0, self.period):
 			for j in range(0 , len(self.contractList)):
 				for k in range(0 , len(self.totalPositiveValues)):
 					self.totalPositiveValues[k]=self.totalPositiveValues[k]+int(self.negativeValues[i][j][k])
 					self.totalNegativeValues[k]=self.totalNegativeValues[k]+int(self.positiveValues[i][j][k])
 					self.totalValues[k] = self.totalValues[k]+int(self.negativeValues[i][j][k])+int(self.positiveValues[i][j][k])
 	def drawTable(self):
 		self.valuesTable =[[] , []]
 		for i in range(0 , 4):
 			self.valuesTable[0].append(str(self.totalValues[i]))

 		for i in range(0 , 4):
 			self.valuesTable[1].append(str(self.percentages[i])+"%")
 		
 		
 		self.table = ExterneTablesGenerator("Resolutions"  ,["Information" , "Anomalie Mineure" , "Anomalie Majeure" , "Anomalie Bloquante"],  ["Nombre de tickets" , "Delai respectes"] , self.valuesTable ,"../templates/tmplt.odp" , "tableResolution" , self.data_conf)	
		self.table.recoverTemplate()
		self.table.createPage()
		self.table.create_table()
		
		self.table.fill_cells()
		self.table.merge()
		self.table.savePresentation()

	def drawPieCharts(self):
		anomalieTotalValue =[0 , 0]
		for i in range(1 , 4):
		  	anomalieTotalValue[0] = anomalieTotalValue[0]+self.totalPositiveValues[i]
		  	anomalieTotalValue[1] = anomalieTotalValue[1]+self.totalNegativeValues[i]  
		

		pieInformation = PieChartsGenerator("Informations" , ["Delai respecte" , "Delai non respecte"] , [int(self.totalPositiveValues[0]) ,int(self.totalNegativeValues[0]) ])
		pieInformation.createPieCharte()
		pieInformation.savePieChart()

		pieAnomalie = PieChartsGenerator("Anomalie" , ["Delai respecte" , "Delai non respecte"] , anomalieTotalValue)
		pieAnomalie.createPieCharte()
		pieAnomalie.savePieChart()

class Category_Synthesis(Category):
	def __init__(self , markdownFile , clientId , contractList , period , conn , data_conf):
		Category.__init__(self , markdownFile , clientId , contractList , period , conn , data_conf)	

	def setValues(self):
		self.queries = InitQueriesSynthesis(self.clientId , self.contractList , self.period)
		self.queries.setInformation_Queries()
		self.queries.set_Anom_Min_Queries()
		self.queries.setAnom_Maj_Queries()
		self.queries.setBlock_Queries()
		self.queries.setOther_Queries()

		self.cursor=TaskExecutor(self.queries.queriesInformation  , self.conn)
		self.cursor.executeTasks()
		self.cursor.fetchValues()
		self.informationValues = self.cursor.fetchedValues


		self.cursor=TaskExecutor(self.queries.queriesAnoMin  , self.conn)
		self.cursor.executeTasks()
		self.cursor.fetchValues()
		self.anomMinValues = self.cursor.fetchedValues

		self.cursor=TaskExecutor(self.queries.queriesAnoMaj  , self.conn)
		self.cursor.executeTasks()
		self.cursor.fetchValues()
		self.anomMajValues = self.cursor.fetchedValues

		self.cursor=TaskExecutor(self.queries.queriesBlock  , self.conn)
		self.cursor.executeTasks()
		self.cursor.fetchValues()
		self.anomBloqValues = self.cursor.fetchedValues

		self.cursor=TaskExecutor(self.queries.queriesOthers  , self.conn)
		self.cursor.executeTasks()
		self.cursor.fetchValues()
		self.otherValues = self.cursor.fetchedValues


	def setSumMonths(self , vectorType):
		result = [0 , 0 , 0 , 0]
		for i in range(0 , len(vectorType)):
			for j in range(0 , len(vectorType[i])):
				for k in range(0 , len(vectorType[i][j])):
					result[k] = result[k]+vectorType[i][j][k]
		return result

	def setVectors(self):
		self.informationVector = self.setSumMonths(self.informationValues)
		self.anomMinVector = self.setSumMonths(self.anomMinValues)
		self.anomMajVector = self.setSumMonths(self.anomMajValues)
		self.anomBloqVector = self.setSumMonths(self.anomBloqValues)
		self.otherVector = self.setSumMonths(self.otherValues) 
		
		# print self.informationValues
		# print "informVector"
		# print self.informationVector
		# print "anomMinVector"
		# print self.anomMinVector

	def transformVectors(self):
		statusVector = [[] , [] , [] , []]
		
		for i in range(0 , len(statusVector)):
			statusVector[i].append(str(self.informationVector[i]))
			statusVector[i].append(str(self.anomMinVector[i]))
			statusVector[i].append(str(self.anomMajVector[i]))
			statusVector[i].append(str(self.anomBloqVector[i]))
			statusVector[i].append(str(self.otherVector[i]))
			statusVector[i].append(str(self.informationVector[i]+self.anomMinVector[i]+self.anomMajVector[i]+self.anomBloqVector[i]+self.otherVector[i]))
			# print np.sum(statusVector)
		return statusVector	

	def drawTable(self):
		self.table = ExterneTablesGenerator("Syntheses"  ,["Information" , "Anomalie Mineure" , "Anomalie Majeure" , "Anomalie Bloquante" , "Autre" , "Total"],  ["Encours de trait" , "En attente d'elem" , "Clotures" , "total"] , self.transformVectors() ,"../templates/tmplt.odp" , "tableSynthesis" , self.data_conf)	
		self.table.recoverTemplate()
		self.table.createPage()
		self.table.create_table()
		
		self.table.fill_cells()
		self.table.merge()
		self.table.savePresentation()
 



class Category_Evolution(Category):
	def __init__(self , markdownFile , clientId , contractList , period , conn , data_conf):
		Category.__init__(self , markdownFile , clientId , contractList , period , conn , data_conf)

	def setPage(self):
		periodReporting = (date.today() +relativedelta(months =-self.period))

		
		self.markdownFile.new_slide("Reporting - De "+self.data_conf['month_dict'][(periodReporting.month)]+" a "+self.data_conf['month_dict'][(date.today().month)])


	def setValues(self):
		#recover information issues from QueriesInformation
		#recover Anomaly issues from QueriesDivision
		flow = InitQueriesFlow(self.clientId , self.contractList , self.period )
		flow.setQueries()

		anomaly = InitQueriesDivision(self.clientId , self.contractList , self.period)
		anomaly.setQueries()


		cursorFlow = TaskExecutor(flow.listQueries , self.conn)
		cursorFlow.executeTasks()
		cursorFlow.fetchValues()
		self.valuesFlow = cursorFlow.fetchedValues

		cursorAnomaly = TaskExecutor(anomaly.listQueries , self.conn)
		cursorAnomaly.executeTasks()
		cursorAnomaly.fetchValues()
		self.valuesAnomaly = cursorAnomaly.fetchedValues


	def setVectors(self):

		#vector containing sum of information issues for each month
		self.informVector = []
		for i in range(0 , self.period):
			self.informVector.append(0)
			for j in range(0 , len(self.contractList)):
				self.informVector[i] = self.informVector[i] + self.valuesFlow[i][j][0]

		#vector containing sum of anomalies issues for each month
		self.anomalyVector = []
		for i in range(0 , self.period):
			self.anomalyVector.append(0)
			for j in range(0 , len(self.contractList)):
				for k in range(0 , 2):
					self.anomalyVector[i]=self.anomalyVector[i]+self.valuesAnomaly[i][j][k]

		print (self.informVector)
		print (self.anomalyVector)
	
	def drawDoubleLineChart(self):
		graphic = LineChartGenerator("title" , "xLabel" , "yLabel" , self.period)
		graphic.saveLineChart(graphic.createDoubleLineChartDates(self.informVector , self.anomalyVector) , "titleFig")		



class Category_Demands(Category):
	def __init__(self , markdownFile , clientId , contractList , period , conn , data_conf):
		Category.__init__(self , markdownFile , clientId , contractList , period , conn , data_conf)


class Category_Clos_Open(Category):
	def __init__(self , markdownFile , clientId , contractList , period , conn , data_conf):
		Category.__init__(self , markdownFile , clientId , contractList , period , conn , data_conf)



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
				self.listQueries[i][j].append(self.static_query+str(i)+" and contract_id = "+str(self.contractList[j])+"  ;")
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
				self.listQueries[i][j].append(self.static_query+str(i)+" and contract_id = "+str(self.contractList[j])+" and issue_severity !='Bloquante' and issue_severity !='3 anomalie bloquante' and issue_severity not like '%Majeure%' and issue_severity not like '%Mineure%' ;")
				self.listQueries[i][j].append(self.static_query+str(i)+" and contract_id = "+str(self.contractList[j])+" and (issue_severity ='Bloquante' or issue_severity='3 anomalie bloquante' or issue_severity like '%Majeure%' or issue_severity like '%Mineure%') ;")
				self.listQueries[i][j].append("select extract(month from (select current_date - interval '"+str(i)+" month')) ;")	


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
			self.listQueries.append([])
			for j in range(0 , len(self.contractList)):
				self.listQueries[i].append([])
				self.listQueries[i][j].append("select count(st.issue_type) "+self.static_query+str(i)+" and st.issue_type like '%information' and st.contract_id = "+str(self.contractList[j])+" ;")
				self.listQueries[i][j].append("select count(st.issue_severity) "+self.static_query+str(i)+" and st.issue_severity like '%Mineure' and st.contract_id = "+str(self.contractList[j])+" ;")
				self.listQueries[i][j].append("select count(st.issue_severity) "+self.static_query+str(i)+" and st.issue_severity like '%Majeure' and st.contract_id = "+str(self.contractList[j])+" ;")
				self.listQueries[i][j].append("select count(st.issue_severity) "+self.static_query+str(i)+" and (st.issue_severity ='Bloquante' or st.issue_severity='3 anomalie bloquante')  and contract_id = "+str(self.contractList[j])+" ;")


class InitQueriesSynthesis(InitQueries):
	def __init__(self , clientId , contractList , period):
		InitQueries.__init__(self  , clientId , contractList)
		self.period= int(period)
		self.static_query = " from statistic_ticket st inner join contract ct on ct.id = st.contract_id where (select extract (year from (select age(current_date , ct.creation_date)))) = 0 and (select extract (month from (select age( current_date , ct.creation_date)))) = "


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
			self.queriesOthers.append([])
			for j in range(0 , len(self.contractList)):
				self.queriesOthers[i].append([])
				self.queriesOthers[i][j].append(self.static_other_query+str(i)+" and fix_in_progress = 't' and contract_id = "+str(self.contractList[j])+self.static_condition)
				self.queriesOthers[i][j].append(self.static_other_query+str(i)+" and waiting_for_customer = 't' and contract_id = "+str(self.contractList[j])+self.static_condition)
				self.queriesOthers[i][j].append(self.static_other_query+str(i)+" and close_date is not null and contract_id = "+str(self.contractList[j])+self.static_condition)
				self.queriesOthers[i][j].append(self.static_other_query+str(i)+" and (fix_in_progress = 't' or waiting_for_customer = 't' or close_date is not null) and contract_id = "+str(self.contractList[j])+self.static_condition)



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
						# print self.fetchedValues[i][j][k]
					except TypeError:
						self.fetchedValues[i][j].append( "Champ mal rempli")
						# print self.fetchedValues[i][j][k]
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
	def __init__(self ,title , values , titles ):
		self.title = title
		self.values = values
		self.ticket_dict = {}
		self.titles = titles


	def setTitles(self):
		for i in range(0 , len(self.titles)):
			self.ticket_dict[self.titles[i]]=self.values[i]
		# self.ticket_dict["Information"] = self.values[0]
		# self.ticket_dict["Mineure"]=self.values[1]
		# self.ticket_dict["Majeure"]=self.values[2]
		# self.ticket_dict["Bloquante"]=self.values[3]
		# self.ticket_dict["Autre"]=self.values[4]
		print self.ticket_dict

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
	def __init__(self  , title , titlesRow , titlesColumn , values , path , id , data_conf):
		self.title = title
		self.values = values
		self.titlesRow = titlesRow
		self.titlesColumn = titlesColumn
		self.values = values
		self.id = str(id)
		self.path = path
		self.data_conf = data_conf
	def recoverTemplate(self):	
		try:
			
			self.doc = odf_get_document(str(self.data_conf['conversion']['template']))
			self.context = self.doc.get_body()
			
			print "longuerue "+ str(len(self.context.get_children()))
			
		except:
			logging.error("can't recover or open the template "+str(self.path))

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
		self.context.insert(self.page  , 1)
		self.context.insert(self.page  , 0)

	def savePresentation(self):
		
		self.doc.save(target=str(self.id)+"report.odp" , pretty="true")
		self.data_conf['conversion']['template']=str(self.id)+"report.odp"



class LineChartGenerator():
	def __init__(self , title ,xLabel , yLabel , period):
		self.title = title
		self.xLabel = xLabel
		self.yLabel = yLabel
		
		self.period = period

	def createLineChart(self):
		plt.plot(self.values[0] , self.values[1])
		plt.title(self.title)
		plt.xlabel(self.xLabel)
		plt.ylabel(self.yLabel)


	def createLineChartDates(self , values):
		self.values = values
		dates = []
		for i in range(-self.period , 0):
			dates.append(date.today() +relativedelta(months =+i))
		print dates
		print len(self.values)
		print len(dates)

		fig = pylab.figure()
		ax = fig.gca()
		ax.plot_date(dates , self.values , 'b.-')

		ax.xaxis.set_major_locator(
	    matplotlib.dates.MonthLocator(bymonth=(1 , 2 , 3 , 4 , 5 , 6 , 7 ,8,9 , 10 , 11,12))
		)
		ax.xaxis.set_major_formatter(
    	matplotlib.dates.DateFormatter('%d-%b')
		)
		
		return fig

	def createDoubleLineChartDates(self ,values, values2):
		print "period is"+str(self.period)
		self.values2 = values2
		self.values = values
		dates = []
		for i in range(-self.period , 0):
			dates.append(date.today() +relativedelta(months =+i))
		print dates
		print len(self.values)
		print len(dates)

		fig = pylab.figure()
		ax = fig.gca()
		ax.plot_date(dates , self.values , 'r.-')
		ax.plot_date(dates , self.values2 , 'g.-')

		ax.xaxis.set_major_locator(
	    matplotlib.dates.MonthLocator(bymonth=(1 , 2 , 3 , 4 , 5 , 6 , 7 ,8,9 , 10 , 11,12))
		)
		ax.xaxis.set_major_formatter(
    	matplotlib.dates.DateFormatter('%d-%b')
		)
		
		return fig

	def saveLineChart(self , fig , title):
		fig.savefig(title+".svg")
		fig.show()
		

class markdownGenerator():
	def __init__(self , file):
		try:
			self.file = open(str(file)+".md" , "w")	
			self.title = str(file)+".md"	
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
	def __init__(self , dict_values):
		self.user = dict_values['user']
		self.password = dict_values['password']
		self.database = dict_values['database']
		self.host = dict_values['host']

	def connection(self):
		try:
			conn_string = " host=" + self.host+ " dbname="+self.database+" user="+self.user+" password="+self.password+" "
			logging.info("Connecting to database succeeded")
			self.conn = psycopg2.connect(conn_string)
		except (Exception, psycopg2.DatabaseError) as error:
			logging.debug('Connection to database failed !')

class Converter():
	def __init__(self , markdownFile , template , title , data_conf):
		self.markdownFile = markdownFile
		self.template = template
		# self.arguments = arguments
		self.data_conf = data_conf
		self.title = title
		self.converter = data_conf['conversion']['converter']
	def convert(self):
		self.markdownFile.file.close()
		# print self.converter+" "+self.markdownFile.title+" "+self.template+" "+self.title+".odp"
		
		os.system("odpdown "+self.markdownFile.title+" "+self.data_conf['conversion']['template']+" "+self.title+".odp")
		self.data_conf['conversion']['template']=str(self.title+".odp")
	


def testExternal():
	test = ExterneTablesGenerator("test" , ["a" , "b"] , ["c" , "d"] , [["1" , "2"] , ["3" , "4"]] , "tmplt.odp" , "oiazy")	
	test.recoverTemplate()
	test.createPage()
	test.create_table()
	test.fill_cells()
	test.merge()
	test.savePresentation()	

def testTotalSum(contrat , indice):
	result = 0
	for i in range(0 , len(contrat)):
		result = result + contrat[i][indice]
	return result


if __name__ == "__main__":

	file = markdownGenerator("filetest")
	
	# for arg in sys.argv:
	# 	print arg 

	# # test = Category_Flow(file , "1836" , ["12485"  , "12491"] , 1 , conn.conn)
	# # test.initValues()

	# # test.setValues()
	# # print test.values
	# # # testArray = [  [[1 , 1 , 1],[2 , 2 , 2],[3 , 3 , 3]] ,[[4 , 4 , 4],[5 , 5 , 5],[6 , 6 , 6]],[[7 , 7 , 7],[8 , 8 , 8],[9 , 9, 9]],[[10 , 10 , 10],[11 , 11 , 11],[12 , 12 , 12]] ]
	# # # print test.totalValues
	# # print test.recoverMonths()
	# # test.drawTable()
	# # # print test.queries.listQueries[0][0][3]



	with open("../reportConfig/report.conf" , "rwsubl") as stream:
		data_loaded = yaml.load(stream)
		data = yaml.dump(data_loaded)

	logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s' , datefmt='%m-%d %H:%M', filename='reporting.log', filemode='w')
	conn = ConnectionDB(data_loaded['connection'])
	conn.connection()

	# # test = Category_Division(file , "1836" , ["12485"  , "12491"] , 1 , conn.conn , data_loaded)
	# # test.initValues()
	# # test.setValues()
	# # test.drawTable()

	# # print data_loaded['conversion']


	# data_loaded['conversion']['template'] = 'testing2.odp'
	# test = Category_Client(file , "1836" , ["12485" , "2104" , "77666" , "12491"] , 3 , conn.conn , data_loaded)
	# test.initValues()
	# test.fillSlide()
	# convert = Converter(file , "../templates/tmplt.odp" , "testing3" , data_loaded)
	# convert.convert()	

	# # print data_loaded['conversion']
	# # convert = Converter(file , "../templates/tmplt.odp" , "testing2" , data_loaded)
	# # convert.convert()
	# # print data_loaded['conversion']

	# # test = Category_Resolution(file , "1836" , ["12485"  , "12491"] , 1 , conn.conn , data_loaded)
	# # test.setValues()
	# # test.setSumtickets()
	# # test.setPercentageResolutions()
	# # test.drawTable()

	# print data_loaded['conversion']



	# test = Category_Synthesis(file , "1836" , ["12485" ] , 1 , conn.conn , data_loaded)
	
	# test.setValues()
	# test.setVectors()
	# test.transformVectors()
	# test.drawTable()


	# test = LineChartGenerator("title" , "xlabel" , "ylabel" , [[1  , 4 , 8], [1  , 4 , 8]])
	# test.createLineChart()
	# test.saveLineChart()



	# test = LineChartGenerator("title" , "xlabel" , "ylabe" , [2 , 5 , 0 , 4] , 4)
	# test.saveLineChart(test.createLineChartDates() , "chekla")


	test = Category_Evolution(file , "1836" , ["12485" ] , 5 , conn.conn , data_loaded)
	# test.setValues()
	# test.setVectors()
	# test.drawDoubleLineChart()


	test.setPage()










