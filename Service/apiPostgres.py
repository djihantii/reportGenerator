import psycopg2
import sys
import pprint
import os
import numpy as np
import matplotlib.pyplot as plt
import plotly.plotly as py
from collections import Counter
import unicodedata
from tableRenderer import *
import logging

client_id = str(sys.argv[1])
contract_id = str(sys.argv[2])
month_rep = int(sys.argv[3])

#Ouverture du fichier markdown qui contiendra les informations
output_md = open(""+contract_id+".md" , "w")

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

#Categories' title
categories = ["**Contrat**" , "**Reporting**" , "**Cloture**" ]

comite = ["**Linagora**"]
	# contrat = ["**Nom**"  , "**description**" , "**Debut du contrat**" , "**Fin du contrat**"]







def connexion_db():
	try:
		conn_string = " host='tosca2.linagora.dc1' dbname='tosca2dev' user='tosca2dev' password='tosca2dev' "
		logging.info("Connecting to database \n ->%s" %(conn_string))
		conn = psycopg2.connect(conn_string)
		return conn
	except (Exception, psycopg2.DatabaseError) as error:
		logging.debug('Connection failed !')

#Preparing queries
def queries_contract_list():
	
	query_contract = []
	query_contract_VLA = []
	query_contract_client=[]
	query_contract.append(query_contract_client)
	query_contract.append(query_contract_VLA)

	customer_name = "SELECT name  FROM customer WHERE id = "+client_id+" ;"
	customer_since= "SELECT creation_date::timestamp::date FROM customer WHERE id = "+client_id+" ;"
	contract_name = "SELECT name FROM contract WHERE id = "+contract_id+" ;"
	contract_description = "SELECT description FROM contract WHERE id = "+contract_id+" ;"
	contract_start_date = "SELECT start_date::timestamp::date FROM contract WHERE id = "+contract_id+" ;"
	contract_end_date = "SELECT end_date::timestamp::date FROM contract WHERE id = "+contract_id+" ;"
	
	VLA_software_name = "SELECT sf.name FROM software sf INNER JOIN contract_software_version csv ON csv.software_id = sf.id where csv.contract_id = "+contract_id+" limit 22;"
	VLA_software_version = "SELECT sv.name from software_version sv inner join contract_software_version csv on csv.software_id = sv.software_id and csv.contract_id = "+contract_id+" limit 22;"


	query_contract_client.append(customer_name)
	query_contract_client.append(customer_since)
	query_contract_client.append(contract_name)
	query_contract_client.append(contract_description)
	query_contract_client.append(contract_start_date)
	query_contract_client.append(contract_end_date)
	

	query_contract_VLA.append(VLA_software_name)
	query_contract_VLA.append(VLA_software_version)
	
	return query_contract

def queries_reporting_flow(months):
	query_reporting = []
	query_information = []
	query_anomalie = []
	query_autre = []
	query_date = []
	query_reporting.append(query_information)
	query_reporting.append(query_anomalie)
	query_reporting.append(query_autre)
	query_reporting.append(query_date)
	static_query = "select count(issue_type) from statistic_ticket where contract_id="+contract_id+" and (select extract (year from (select age(current_date , creation_date)))) = 0 and (select extract (month from (select age( current_date , creation_date)))) ="
	
	i=0
	while i<months:
		query_information.append(""+static_query+str(i)+" and issue_type like '%information%' ;")
		query_anomalie.append(""+static_query+str(i)+" and (issue_type like '%anomalie%' or issue_type like '%Anomalie%') ;")
		query_autre.append(""+static_query+str(i)+" and issue_type not like '%anomalie%' and issue_type not like '%Anomalie%' and issue_type not like '%information%' ;")
		query_date.append("select extract(month from (select current_date - interval '"+str(i)+" month')) ;")
		i=i+1

	return query_reporting

def queries_reporting_severities(months):
	query_severity=[[] , [] , [] , []]
	static_query="select count(issue_severity) from statistic_ticket where contract_id="+contract_id+" and (select extract (year from (select age(current_date , creation_date)))) = 0 and (select extract (month from (select age( current_date , creation_date)))) ="
 
 	i=0
 	while i<months:
 		query_severity[0].append(""+static_query+str(i)+"and issue_severity like '%Mineure%' ;")
 		query_severity[1].append(""+static_query+str(i)+"and issue_severity like '%Majeure%' ;")
 		query_severity[2].append(""+static_query+str(i)+"and (issue_severity ='Bloquante' or issue_severity='3 anomalie bloquante') ;")
 		i=i+1

 	return query_severity

def queries_resolution_time(months):
	
	query_resolution = [[] , [], [] , []]
	static_query = " from statistic_ticket st inner join contract ct on ct.id = st.contract_id where st.contract_id = "+contract_id+" and (SELECT extract (year from (select age(current_date , st.creation_date)))) = 0 and (select extract (month from (select age (current_date , st.creation_date)))) <= "+str(months)
	positive = "and st.close_date is not null and (st.fix_sla_target >= st.fix_duration) ;"
	negative = "and st.close_date is not null and (st.fix_sla_target < st.fix_duration) ;"
	query_resolution[0].append("select count(st.issue_type) "+static_query+" and st.issue_type like '%information%' "+positive)
	query_resolution[0].append("select count(st.issue_type) "+static_query+" and st.issue_type like '%information%' "+negative)

	query_resolution[1].append("select count(st.issue_severity) "+static_query+" and st.issue_severity like '%Mineure%' "+positive)
	query_resolution[1].append("select count(st.issue_severity) "+static_query+" and st.issue_severity like '%Mineure%' "+negative)
	
	query_resolution[2].append("select count(st.issue_severity) "+static_query+" and st.issue_severity like '%Majeure%' "+positive)
	query_resolution[2].append("select count(st.issue_severity) "+static_query+" and st.issue_severity like '%Majeure%' "+negative)

	query_resolution[3].append("select count(st.issue_severity) "+static_query+" and (issue_severity ='Bloquante' or issue_severity='3 anomalie bloquante') "+positive)
	query_resolution[3].append("select count(st.issue_severity) "+static_query+" and (issue_severity ='Bloquante' or issue_severity='3 anomalie bloquante') "+negative)



	return query_resolution

def queries_closure_list():
	query_closure = []
	


def category_contract_customer(conn):
		
	query_contract = queries_contract_list()
	
	cursor = []
	cursor_client_contract=[]
	cursor_VLA_contract = []
	x=0
	while x<len(query_contract[0]):
		cursor_client_contract.append(conn.cursor())
		cursor_client_contract[x].execute(query_contract[0][x])
		x=x+1
	x=0
	while x<len(query_contract[1]):
		cursor_VLA_contract.append(conn.cursor())
		cursor_VLA_contract[x].execute(query_contract[1][x])
		x=x+1

	cursor.append(cursor_client_contract)
	cursor.append(cursor_VLA_contract)
	return cursor


def category_flow_tickets(conn , months):
	query_reporting = queries_reporting_flow(months)
	counter=0
	cursor = []
	cursor_anomalie = []
	cursor_information = []
	cursor_autre = []
	cursor_month = []

	while counter<months:
		cursor_information.append(conn.cursor())
		cursor_information[counter].execute(query_reporting[0][counter])
		
		cursor_anomalie.append(conn.cursor())
		cursor_anomalie[counter].execute(query_reporting[1][counter])
		
		cursor_autre.append(conn.cursor())
		cursor_autre[counter].execute(query_reporting[2][counter])
		
		cursor_month.append(conn.cursor())
		cursor_month[counter].execute(query_reporting[3][counter])
		
		counter=counter+1
	

	cursor.append(cursor_information)
	cursor.append(cursor_anomalie)
	cursor.append(cursor_autre)
	cursor.append(cursor_month)	
	return cursor


def category_severities_tickets(conn , months):
	query_severity = queries_reporting_severities(months)
	counter=0
	cursor = [[] , [] , []]

	while counter<months:
		cursor[0].append(conn.cursor())
		cursor[0][counter].execute(query_severity[0][counter])
		
	
		cursor[1].append(conn.cursor())
		cursor[1][counter].execute(query_severity[1][counter])

		cursor[2].append(conn.cursor())
		cursor[2][counter].execute(query_severity[2][counter])
	
		counter=counter+1
	
	return cursor	


def category_resolution_time(conn , months):
	cursor = [ [] , [] , [] , [] ] 
	query_list = queries_resolution_time(months)
	i=j=0
	for i in range(0,4):
		for j in range(0,2):
			cursor[i].append(conn.cursor())
			cursor[i][j].execute(query_list[i][j])
			j=j+1
		i=i+1
	return cursor

def category_closure():
	queries.append(query_closure)
	pass

def end_line():
	output_md.write("\n \n")

def tield():
	output_md.write("~~~")

def img_insert(name , link , title):
	new_slide(title)
	output_md.write("!["+name+"]("+link+")")
	end_line()
def new_slide(title):
	output_md.write("## "+title)
	end_line()


def slide_contract_creator( cursors , title):
	customer_contract = [ "**Nom du client**" , "**Client depuis**", "**Nom du contrat**"  , "**description du contrat**" , "**Debut du contrat**" , "**Fin du contrat**"]
	new_slide(title)
	x=0
	while x < len(customer_contract):
		#print str( cursors[x].fetchone() )
		output_md.write("* "+customer_contract[x]+" : "+str(( cursors[x].fetchone() )[0]) )
		end_line()
		x=x+1

def slide_VLA_creator(title , cursors):
	new_slide(title)
	
	software = cursors[0].fetchone()
	version = cursors[1].fetchone()
	i=1
	while software is not None:
		if (i % 10) == 0:
			new_slide(title)
		output_md.write("**Software** : "+software[0]+"\t **version** : "+version[0])
		end_line()
		software = cursors[0].fetchone()
		version = cursors[1].fetchone()		
		i=i+1


def recovering_flow_results(cursor , months):
	counter=0
	values = [ [] , [] , [] , [] , [] ]
	while counter<months:

		date= month_dict[cursor[3][counter].fetchone()[0]]
		
		values[0].append(int(cursor[0][counter].fetchone()[0]))

		
		values[1].append(int(cursor[1][counter].fetchone()[0]))
		
		values[2].append(int(cursor[2][counter].fetchone()[0]))

		values[3].append(date)
		
		values[4].append((values[0][counter]) +int(values[1][counter])+int(values[2][counter]))

		counter=counter+1

	return values

def slide_flux_tickets(cursor , months):
	counter=0
	values = [ [] , [] , [] , [] , [] ]
	

	while counter<months:


		date= month_dict[cursor[3][counter].fetchone()[0]]
		values[3].append(date)
		new_slide("le mois "+values[3][counter])
		

		
		output_md.write("le flux pour le mois "+values[3][counter]+" : ")
		end_line()
		
		values[0].append(int(cursor[0][counter].fetchone()[0]))
		output_md.write("** le nombre de demande d'information est ** : "+ str(values[0][counter]))
		end_line()
		
		values[1].append(int(cursor[1][counter].fetchone()[0]))
		output_md.write("** le nombre de demande de support est ** : "+str(values[1][counter]))
		end_line()
		
		values[2].append(int(cursor[2][counter].fetchone()[0]))
		output_md.write("** le nombre d'autre demande ** : "+str(values[2][counter]))
		end_line()
		
		values[4].append((values[0][counter]) +int(values[1][counter])+int(values[2][counter]))

		output_md.write("** le nombre total de demande est ** : " + str(values[4][counter]))
		end_line()
		counter=counter+1

	return values
def slide_severities_tickets(cursor , months):
	counter = 0
	values_severities = [[] ,[] , [] , [] ]

	while counter<months:

		# output_md.write("La repartition pour le mois "+values[3][counter]+" : ")
		# end_line()
			
		new_slide("repartition")

		values_severities[0].append(int(cursor[0][counter].fetchone()[0]))
		output_md.write("** le nombre d'anomalie mineures ** : "+ str(values_severities[0][counter]))
		end_line()
		
		values_severities[1].append(int(cursor[1][counter].fetchone()[0]))
		output_md.write("** le nombre d'anomalie majeures ** : "+str(values_severities[1][counter]))
		end_line()
		
		values_severities[2].append(int(cursor[2][counter].fetchone()[0]))
		output_md.write("** le nombre de demandes bloquantes ** : "+str(values_severities[2][counter]))
		end_line()
		
		values_severities[3].append((values_severities[0][counter]) +int(values_severities[1][counter])+int(values_severities[2][counter]))

		output_md.write("** le nombre total de demande est ** : " + str(values_severities[3][counter]))
		end_line()
		counter=counter+1
	return values_severities

def percentage(a , b):
	out = []
	if a == b == 0:
		return [0 , 0]
	out.append(a*100/(a+b))
	out.append(b*100/(a+b))
	return out

def slide_resolution_time(cursor , months):
	details = [[] , [] , [] , [] , []  ]		
	new_slide("Delai de resolution")
	
	list_types = ["** Information **" , "** Anomalie Mineure **" , "** Anomalie Majeure **" , "** Anomalie Bloquante **"]

	output_md.write("** Type de demande ** => ** Nombre de tickets ** => ** delais respectes ** ")
	end_line()
	i=0
	for i in range(0,4):
		positive_time = cursor[i][0].fetchone()[0]
		negative_time = cursor[i][1].fetchone()[0]
		details[i].append(list_types[i])
		details[i].append(positive_time)
		details[i].append(negative_time)
		details[i].append(positive_time+negative_time)
		details[i].append(percentage(positive_time , negative_time)[0])
		output_md.write(str(details[i][0])+"  ======>  ")
		output_md.write(str(details[i][3])+"  ==========>   ")
		output_md.write(str(details[i][4])+"%")
		end_line()	

	return details


def total_tickets(month , values , values_severities):
	tmp1=0
	tmp2=0
	tmp3=0
	tmp4=0
	tmp5=0
	total=[]
	i=0
	while i<month:
		tmp1=tmp1+values[0][i]
		tmp2=tmp2+values_severities[0][i]
		tmp3=tmp3+values_severities[1][i]
		tmp4=tmp4+values_severities[2][i]
		tmp5=tmp5+values[2][i]
		i=i+1
	total.append(tmp1)
	total.append(tmp2)
	total.append(tmp3)
	total.append(tmp4)
	total.append(tmp5)

	return total


def graph_flow_generator(total):
	ticket_dict = {}
	ticket_dict["Information"] = total[0]
	ticket_dict["Mineure"]=total[1]
	ticket_dict["Majeure"]=total[2]
	ticket_dict["Bloquante"]=total[3]
	ticket_dict["Autre"]=total[4]

	fig=plt.figure()
	ax = fig.add_subplot(111)

	frequencies = ticket_dict.values()
	names = ticket_dict.keys()

	x_coordinates = np.arange(len(ticket_dict))
	ax.bar(x_coordinates, frequencies, align='center')

	ax.xaxis.set_major_locator(plt.FixedLocator(x_coordinates))
	ax.xaxis.set_major_formatter(plt.FixedFormatter(names))

	plt.savefig("flow"+contract_id+".svg")
	# plt.show()

	img_insert("Repartition des demandes" , "flow"+contract_id+".svg" , "Repartition des demandes")

def graph_resolution_time_generator(details):
	number_respected = 0
	number_non_respected = 0
	
	for i in range(1 , 4):
		number_respected = number_respected+details[i][1]
		number_non_respected = number_non_respected+ details[i][2]

	labels = ['respectes' , 'hors delai']
	sizes = [number_respected , number_non_respected]
	explode=(0 , 0)

	fig1 , ax1 = plt.subplots()
	ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
        shadow=True, startangle=90)
	ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
	plt.savefig(contract_id+"resolution_support.svg")

	sizes = [details[0][1] , details[0][2]]
	fig2, ax2 = plt.subplots()
	ax2.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
        shadow=True, startangle=90)
	ax2.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
	plt.savefig(contract_id+"resolution_information.svg")
	
	img_insert("Informations" , contract_id+"resolution_information.svg" , "Delai des informations")
	img_insert("Anomalies" , contract_id+"resolution_support.svg" , "Delai des anomalies")

def table_flux_ticket(values ):
	titles=["Demande d'information" ,"Demande de support" , "Autre" , "Total"]
	months=values[3]
	id=int(contract_id)
	render=tableRender(values , titles , id , months , str(contract_id)+"report.odp")
	page = render.create_page()
	table = render.create_table()
	for i in range(1 , render.x):
		render.set_val(table , i , 0 , months[i-1])
		render.set_val(table , i , 4 , values[4][i-1])
	for i in range(1 , render.y):
		render.set_val(table , 0 , i , titles[i-1])
	
	for i in range(1 , render.y-1):
		for j in range(1 , render.x):
			render.set_val(table , j , i , render.values[i-1][j-1])
	
	render.merge(page , table)

	render.savePresentation()
	
def graph_evolution_tickets_generator():
	pass

def graph_open_closed_generator():	
	pass	

def category_one(conn , month):
	cursor_con = category_contract_customer(conn)
	slide_contract_creator(cursor_con[0] , categories[0])	
	slide_VLA_creator("Softwares" , cursor_con[1])
	
def category_two(conn , month):
	cursor_flow = category_flow_tickets(conn , month )
	cursor_severity = category_severities_tickets(conn , month)
	# values = slide_flux_tickets(cursor_flow,  month)
	values = recovering_flow_results(cursor_flow , month)
	values_severities = slide_severities_tickets(cursor_severity , month)
	total = total_tickets(month_rep , values , values_severities)
	cursor_resolution = category_resolution_time(conn , month_rep)
	details = slide_resolution_time(cursor_resolution , month_rep)
	
	graph_flow_generator(total)
	graph_resolution_time_generator(details)
	output_md.close()
	convert_odpdown(""+contract_id+".md" , "tmplt.odp")
	table_flux_ticket(values)


def convert_odpdown(fileMD , template):
	os.system("/home/djihane/LinagoraProject/odpdown/odpdown "+fileMD +" "+ template +" " +contract_id+"report.odp")	


def showODP_File():
	os.system("libreoffice "+contract_id+"report.odp")




if __name__=="__main__":
	

	logging.basicConfig(filename='reporting.log' , level=logging.DEBUG)
	current_template_odp = "tmplt.odp"
	current_target_odp = str(contract_id)+"report.odp"
	
	conn = connexion_db()
	category_one(conn , month_rep)
	category_two(conn , month_rep)
	


	

	showODP_File()





























