import os
from dotenv import load_dotenv
import google.generativeai as genai
import pymysql
import json

# class for database manipulation
class Database_Manipulation(object):
    # initialize variable for class
    def __init__(self):
        self.database_name = "study_content_db"
        self.database_user = "root"
        self.database_password = '12345678'

    def replace_filename_exception(self,default_filename):
        self.default_filename = default_filename

        if " " in default_filename or "-" in default_filename:
            # Remove spaces, hyphens, and underscores, then strip the .pdf extension if present
            self.filename = default_filename.replace(" ", "").replace("-", "").replace(".pdf", "")
        else:
            self.filename = default_filename.replace(".pdf", "")

        return self.filename

    # create database function
    def create_database(self,uploaded_filename):
        print(f"filename_before={uploaded_filename}")
        self.replace_filename_exception(uploaded_filename)

        print(f"filename_after={self.filename}")


        # open db connection
        conn = pymysql.connect(host='localhost',
                            user=self.database_user,
                            password=self.database_password,
                            charset="utf8"
                            )
        
        # create cursor object
        cursor = conn.cursor()
        
        # SQL command
        # create database if database is not exist
        cursor.execute("CREATE DATABASE IF NOT EXISTS study_content_db")
        
        # submit
        conn.commit()
        
        # close database connections
        conn.close()

        # call create table function
        self.create_table()

    # create table function
    def create_table(self):
        # open db connection
        conn = pymysql.connect(host='localhost',
                            user = self.database_user,
                            password = self.database_password,
                            charset = "utf8",
                            database = self.database_name
                            )

        # create cursor object
        cursor = conn.cursor()

        # SQL command
        # create question table if it is not exists
        create_info_tab_sql = f"""CREATE TABLE IF NOT EXISTS {self.filename}_questions (
            NO_QUESTION INT PRIMARY KEY AUTO_INCREMENT,
            QUESTION VARCHAR(500), 
            OPTION_1 VARCHAR(500),
            OPTION_2 VARCHAR(500),
            OPTION_3 VARCHAR(500),
            OPTION_4 VARCHAR(500),
            ANSWER VARCHAR(500),
            DIFFICULTY CHAR(25),
            STATUS CHAR(25)
        );"""

        # create history table
        create_history_table_sql = f"""CREATE TABLE IF NOT EXISTS history_table (
            NO_FILE INT PRIMARY KEY AUTO_INCREMENT,
            FILENAME VARCHAR(250)
        );"""

        # execute sql command
        cursor.execute(create_info_tab_sql)
        cursor.execute(create_history_table_sql)

        # commit action
        conn.commit()

        # close database connection
        conn.close()

        # save filename
        self.save_filename()

    def save_filename(self):
        print("Start saving filename")
        # open db connection
        conn = pymysql.connect(
            host='localhost',
            user=self.database_user,
            password=self.database_password,
            charset="utf8",
            database=self.database_name
        )

        # create cursor object
        cursor = conn.cursor()

        # SQL command to insert into question table
        insert_data_sql = f"""
            INSERT INTO history_table (FILENAME)
            VALUES (%s)
        """

        # Execute the insertion
        cursor.execute(insert_data_sql, self.default_filename)

        # commit action
        conn.commit()

        print("Insertion of Filename Done!")

    # insert data into database function
    def insert_data(self,questions_list,multiple_option_list,answers_list,difficulty_list):
        # open db connection
        conn = pymysql.connect(
            host='localhost',
            user=self.database_user,
            password=self.database_password,
            charset="utf8",
            database=self.database_name
        )

        # create cursor object
        cursor = conn.cursor()

        # SQL command to insert into question table
        insert_data_sql = f"""
            INSERT INTO {self.filename}_questions (QUESTION, OPTION_1, OPTION_2, OPTION_3, OPTION_4, ANSWER, DIFFICULTY, STATUS)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """

        # literate to insert data
        for index in range(len(questions_list)):
            data = (questions_list[index], multiple_option_list[index][0], multiple_option_list[index][1], multiple_option_list[index][2], multiple_option_list[index][3], answers_list[index], difficulty_list[index], "ENABLED")

            # Execute the insertion
            cursor.execute(insert_data_sql, data)

        # commit action
        conn.commit()

        print("Insertion of NEW Data Done!")

    def get_history_table(self):
        # open db connection
        conn = pymysql.connect(
            host='localhost',
            user=self.database_user,
            password=self.database_password,
            charset="utf8",
            database=self.database_name
        )
        
        #create cursor object
        cursor = conn.cursor()
        
        #define query   textbook_questions
        query = f'select FILENAME from history_table'
        
        #Run query
        cursor.execute(query)
        
        #Fetch the results
        result = cursor.fetchall()
        print(result[0])
        print(type(result))
        history_filename_list = []
        for item in result:
            history_filename_list.append(item[0])

        print(f"history_filename_list:{history_filename_list}")

        return history_filename_list

    #Function that get the question from database
    def get_question(self,difficulty,selected_file_name):
        self.replace_filename_exception(selected_file_name)
        print(f"self.filename:{self.filename}")

        # open db connection
        conn = pymysql.connect(
            host='localhost',
            user=self.database_user,
            password=self.database_password,
            charset="utf8",
            database=self.database_name
        )
        
        #create cursor object
        cursor = conn.cursor()
        
        #define query textbook_questions
        query = f'select NO_QUESTION, QUESTION, OPTION_1, OPTION_2, OPTION_3, OPTION_4, ANSWER from {self.filename}_questions where DIFFICULTY = "{difficulty}" AND STATUS = "ENABLED" LIMIT 10'
        
        #Run query
        cursor.execute(query)
        
        #Fetch the results
        result = cursor.fetchall()
        
        #Initialize a list 
        sorted_question_list = []
        
        #insert retrieved data into the list using dictionaries method
        for row in result:
            question_data = {
                "No_Question ":row[0],
                "Question":row[1],
                "Option":(row[2],row[3],row[4],row[5]),
                "Answer": row[6]
            }
            sorted_question_list.append(question_data)

        #close the cursor and database connection
        cursor.close()
        conn.close()

        #return the list that containing the data
        return sorted_question_list
    
        # Function to disable a question if answered correctly
    def disable_question(self, question_no):
        # Open db connection
        conn = pymysql.connect(
            host='localhost',
            user=self.database_user,
            password=self.database_password,
            charset="utf8",
            database=self.database_name
        )

        # Create cursor object
        cursor = conn.cursor()

        #define update qury which is disable the question textbook_questions
        updated_query = f'UPDATE {self.filename}_questions SET STATUS = "DISABLED" WHERE NO_QUESTION = %s'

        #execute the query
        cursor.execute(updated_query,question_no)

        #commit the change
        conn.commit()

        #close the cursor and database connection
        cursor.close()
        conn.close()

class AI_Model(object):
    def __init__(self):
        self.api = "GOOGLE_API_KEY"
        # set up AI model
        self.model = genai.GenerativeModel("gemini-1.5-flash",
                                system_instruction="""
                                    You are a professional study content analyzer.
                                """)
        
        self.prompt = '''
            Based on the content of the provided PDF, generate a list of 20 multiple-choice questions(easy, medium, hard). 
            Each question should follow the specific data structure format given below. 
            Please avoid using JSON formatting terminology and respond in a plain, list format as shown(Prevent response too long content):
            
            Format:
            [
                {
                    "question": "Question text here",
                    "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
                    "answer": "Correct answer here",
                    "difficulty": "easy/medium/hard"
                },...
            ]
            
            Note: Follow this structure precisely for each question generated.
        '''

    # AI content generator function
    def content_generator(self,material_content):
        # load dot
        load_dotenv()

        # Get google api key from .env file
        genai.configure(api_key=os.getenv(self.api))

        print("Start Generating Content....")
        # generate questions_info_list based on the prompt given
        questions_info_list = self.model.generate_content([self.prompt, material_content])

        # sort content for insertion of data into database
        aim.sort_content(questions_info_list.text)

        # sort content function
    def sort_content(self,questions_info_list):
        # turn string data into list format
        data_list = json.loads(questions_info_list)

        # create an empty lists
        questions_list = []
        answers_list = []
        multiple_option_list = []
        difficulty_list = []

        # for loop
        for i in range(len(data_list)):
            # get questions from data set
            question = data_list[i]["question"]
            multiple_options = data_list[i]["options"]
            answer = data_list[i]["answer"]
            difficulty = data_list[i]["difficulty"]

            # append data into list
            questions_list.append(question)
            multiple_option_list.append(multiple_options)
            answers_list.append(answer)
            difficulty_list.append(difficulty)

        db.insert_data(questions_list,multiple_option_list,answers_list,difficulty_list)

# uploaded_file = r"materials\\Pendidikan Moral Tingkatan 4 KSSM.pdf"

# initialize Database Manipulation class
db = Database_Manipulation()

# initialize AI_Model class
aim = AI_Model()
