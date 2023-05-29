#importing All requied Lib
import pandas as pd
import streamlit as st
from PIL import Image
import re
import  time
import easyocr as ocr
import  cv2
import os
import numpy as np
from geopy.geocoders import Nominatim
import mysql.connector
from io import BytesIO


#connecting to MySQL database
mydb=mysql.connector.connect(
    host="localhost",
    port='3306',
    user='root',
    password='achuthan@13',
    database='Business_card_data'
)
cursor=mydb.cursor()


#using Geocode to get place and state name from pincode
geolocator= Nominatim(user_agent="geoapiExercises")

#set  page
st.set_page_config(page_title="Business card",  layout="wide" )
st.header(':green[Data extraction from business card]')

#page navigation
c1,c2=st.columns([5,3])
with c1:
    #page_select=st.selectbox(":blue[Select Page]",("Extract Data","Explore data"))
    tab1,tab2=st.tabs(["Extract Data","Explore data"])
def convertToBinaryData(filename):
    # Convert digital data to binary format
    with open(filename, 'rb') as file:
        blobData = file.read()
    return blobData
def convert_data(binarydata,filename):
    with open(filename,'wb')as file:
        image=file.write(binarydata)
    return image


with tab1:

    img1 = st.file_uploader(":blue[Upload Image]", type=["png", "jpg", "jpeg"])
    if img1 is not None:
        st.image(img1)
        img_path = os.path.abspath(img1.name)
        image = convertToBinaryData(img_path)

    @st.cache_data
    def load_model():
        reader = ocr.Reader(['en'])  # ,model_storage_directory='.')
        return reader
    result_text=[]
    reader = load_model()  # load model

    if img1 is None:
        st.write(":red[No Image selectd yet .!]")
    else:
        #st.write("Extracting...")

        input_image = Image.open(img1)  # read image
        result = reader.readtext(np.array(input_image))
        result_text = []  # empty list for results
        for text in result:
            result_text.append(text[1])
            #st.write(text[1])

    keywords = ['road', 'floor', ' st ', 'st,', 'street', ' dt ', 'district',
                    'near', 'beside', 'opposite', ' at ', ' in ', 'center', 'main road',
                    'state', 'country', 'post', 'zip', 'city', 'zone', 'mandal', 'town', 'rural',
                    'circle', 'next to', 'across from', 'area', 'building', 'towers', 'village',
                    ' ST ', ' VA ', ' VA,', ' EAST ', ' WEST ', ' NORTH ', ' SOUTH ']

    #displaying extracted Raw data
    st.markdown(":blue[Extracted Raw data:]")
    co1,co2=st.columns(2)
    with co1:
        st.write([i for i in result_text][:(len(result_text)//2)])
    with co2:
        st.write([i for i in result_text][(len(result_text) // 2):])

#storing extracted values
    company_name=''
    card_holder=''
    name=''
    designation=''
    mobile_number=''
    email_address=''
    website_URL=''
    area=""
    city=''
    state=""
    pin_code=''

#seperating  the extracted data accordingly
#dat=[card_holder,company_name,name,designation,mobile_number,email_address,website_URL,area,city,state,pin_code]
    for i, string in enumerate(result_text):
        # TO FIND EMAIL
        if re.search(r'@', string.lower()):
            email_address = string.lower()
            result_text[i]= ''

        # TO FIND PINCODE
        match = re.search(r'\d{6,7}', string.lower())
        if match:
            pin_code = match.group()

            #st.write(type(pin_code),len(pin_code),pin_code)
            result_text[i] = ''
            #result_text = result_text.replace(string, ''
            try:
                location = geolocator.geocode(pin_code)
                address1 = (location.address).split(',')
                city = address1[-4]
                state = address1[-3]
            except AttributeError:
                st.write("Invalid Pincode")


        #to Find phone number
        phoneNumber_regex = re.search(r'\+*\d{2,3}-\d{3,10}-\d{3,10}',string)
        if phoneNumber_regex:
            mobile_number= string
            result_text[i]= ''
            #result_text = result_text.replace(string, '')

        #to find address

        # Check if the string contains any of the keywords or a sequence of six or seven digits
        if any(keyword in string.lower() for keyword in keywords):
            area = string
            result_text[i]= ''
            #result_text = result_text.replace(string, '')

        #link_regex = re.search(r'www.?[\w.]+', string)
        link_regex = re.compile(r'www.?[\w.]+', re.IGNORECASE)
        for lin in link_regex.findall(string):
            website_URL += lin
            result_text[i]=''
            #result_text = result_text1.replace(lin, '')

        desig_list = ['DATA MANAGER', 'CEO & FOUNDER', 'Managing Director',
                      'General Manager', 'Marketing Executive', 'Technical Manager']
        for j in desig_list:
            if re.search(j, string):
                designation = string
                result_text[i] = ''

    text=' '.join(result_text)




    #displaying the data seperatly
    col1,col2=st.columns(2)

    with col1:
        # card_holder
        card_holder1 = st.text_input("Card holder", value=card_holder, label_visibility='visible', disabled=False)

        # Name
        name1 = st.text_input("Name",value=name,label_visibility='visible',disabled=False)

        # designation
        designation1 = st.text_input("Designation", value=designation, label_visibility='visible', disabled=False)

        # Company name
        company_name1 = st.text_input("Company Name", value=company_name, label_visibility='visible', disabled=False)

        # mobile_number
        mobile_number1 = st.text_input("Mobile number",value=mobile_number,label_visibility='visible',disabled=False)

        # email_address
        email_address1 = st.text_input("Email Id",value=email_address,label_visibility='visible',disabled=False)

        # website_URL
        website_URL1 = st.text_input("Web URL",value=website_URL.lower(),label_visibility='visible',disabled=False)

    with col2:

        #Area
        Area1 = st.text_input("Area",value=area,label_visibility='visible',disabled=False)

        #Pin coe
        pin_code1 = st.text_input("Pin code :",value=pin_code,label_visibility='visible',disabled=False)
        if pin_code1 is not None:
            #finding city and state with pincode
            try:
                location = geolocator.geocode(pin_code1)
                address1 = (location.address).split(',')
                city = address1[-4]
                state = address1[-3]
            except AttributeError:
                pass
        else:
            pass

        # City
        City1 = st.text_input("City", value=city, label_visibility='visible', disabled=False)

        # State
        state1 = st.text_input("State", value=state, label_visibility='visible', disabled=False)

    #convering image to binary image for saving in database
    def convertToBinaryData(filename):
        # Convert digital data to binary format
        with open(filename, 'rb') as file:
            blobData = file.read()
        return blobData

    #fetching data from MYSQL DB
    def show_database():
        query1 = "SELECT * FROM card_data"
        ex = cursor.execute(query1)
        new_df = cursor.fetchall()
        df = pd.DataFrame(new_df,columns=cursor.column_names)
        return df

    #inserting or saving data accordingly in mysql
    Save=st.button("Save")
    if Save:
        data_insert = '''INSERT INTO card_data (
                      Card_holder,
                      Name, 
                      Designation, 
                      Company_name,
                      Contact_number, 
                      Mail_id ,
                      Website_link ,
                      Address,
                      City  ,
                      State ,
                      PinCode ,
                      Image) 
                      VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);'''

        dat = (card_holder1,
               name1,
               designation1,
               company_name1,
               mobile_number1,
               email_address1,
               website_URL1,
               Area1,
               City1,
               state1,
               pin_code1,
               image)
        cursor.execute(data_insert, dat)
        mydb.commit()

        st.success('Data Saved to Database successfully!', icon="✅")
        #st.write("Done")

    #display all data from the database
    df1=show_database()
    if st.button("Show Table:"):
        st.dataframe(df1)





#Explore data , View, Edit, update
with tab2:
    st.title(':blue[Explore Card detials :]  :orange[View Edit]')
    #fetching data
    def show_database():
        query1 = "SELECT * FROM card_data"
        ex = cursor.execute(query1)
        new_df = cursor.fetchall()
        df = pd.DataFrame(new_df, columns=cursor.column_names)
        return df

#displaying data
    def show_updated_data(id):
        q3 = (f'SELECT * FROM card_data where ID={id}')
        cursor.execute(q3)
        new_df = cursor.fetchall()
        df1 = pd.DataFrame(new_df, columns=cursor.column_names)
        return df1


    df = show_database()

    if st.button(':red[Show Table]'):
        st.dataframe(df)

    st.subheader(':blue[Search Data by Column]')

    op = ['Card_holder', 'Name', 'Designation', 'Company_name', 'Contact_number',
          'Mail_id', 'Website_link', 'Address', 'City', 'State', 'PinCode']
    column1 = str(st.radio(':blue[Select column to search:]', op, horizontal=True))

    col1, col2 = st.columns(2)


    with col1:
        value1 = str(st.selectbox(':blue[Please select value to search:]', (df[column1].unique())))
        #st.write(df[column1].unique())
        selected = (df[df[column1] == value1])
        if st.checkbox(":red[Show ]Data") :
            st.dataframe((df[df[column1] == value1]).T)

        id = (selected.iat[0, 1])

        image_data=(selected["Image"])
    with col2:
        position=0
        id_op = ([int(i) for i in selected["ID"]])
        if len(id_op) > 1:
            id1 = st.selectbox(":blue[ID :] ", id_op, disabled=False)

        else:
            id1 = st.selectbox("ID: ", id_op, disabled=True)

        row_num = ((selected[selected["ID"] == id1].index)[0])
        #st.write((id1))
        #st.write(row_num)

        column_value = (st.multiselect(':blue[Select column to edit]', op))

        for i in column_value:
            st.write("write",i)
            names = i + '1'
            val=str(selected.at[int(row_num),i])#.iat[0,1])
            #st.write(val)
            names = st.text_input(i, value=val, label_visibility='visible', disabled=False)

            up_bt = st.button(":red[Update]   " + str(i))
            condition = (i + "= '" + names + "'")

            if up_bt:
                sqlFormula = f"UPDATE card_data SET {condition} WHERE ID = %s"
                #st.write(sqlFormula)
                cursor.execute(sqlFormula, (int(id1),))
                mydb.commit()
                container = st.empty()
                container.success("Updated Successfully")  # Create a success alert
                time.sleep(2)  # Wait 2 seconds
                container.empty()
        st.write('')

        if st.button(":red[See] Updated Data"):
            df2 = show_updated_data(id1)
            st.dataframe(df2.T)

    def retrive(id1):
        q4="SELECT * from card_data where ID='{1}'"
        cursor.execute(q4.format(str(id1)))
        res=cursor.fetchone()[-1]
        file_path_toSave = "C:\\Users\\Lenovo\\Desktop\\business card data detection\\Sample_img\\Saved{0}.jpg".format(str(id1))
        with open(file_path_toSave,'wb') as file:
            file.write(res)
            st.image(res)
            file.close()
    st.write("\n\n\n\n")
    col12,col33,col14=st.columns([2,4,1])
    with col12:
        delete = st.button("Delete Now")
        if delete:
            q7 = "DELETE FROM card_data WHERE ID=%s"
            cursor.execute(q7,(id1,))
            mydb.commit()
            st.success("Deleted successfully")

    with col1:
        if st.checkbox(":red[Display] Image"):
            retrive(id1)










