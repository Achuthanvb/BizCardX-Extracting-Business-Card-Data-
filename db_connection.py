import mysql.connector

mydb=mysql.connector.connect(
    host="localhost",
    port='3306',
    user='root',
    password='achuthan@13',
    database='Business_card_data'
)

cursor=mydb.cursor()


#table Created 