# importing fastapi dependencies

from fastapi import FastAPI, Response, status, HTTPException
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional, Any, List 
import random
import psycopg2
from psycopg2.extras import RealDictCursor 
import time  
from app import  schema




app = FastAPI()


    
#Connect to your postgres DB
while True:
    try:
        conn = psycopg2.connect(host = 'localhost', database = 'Fastapi',
        user = 'postgres', password = "postgres", cursor_factory= RealDictCursor)
        cursor = conn.cursor()
        print("Database connected successfully")
        break


    except Exception as error:
        print("connection to the database failed")
        print("Error:", error)
        time.sleep(2)






#create get request
@app.get("/posts")
def get_post():
    cursor.execute("""SELECT * FROM posts """)
    posts = cursor.fetchall()
    print(posts)
    return {"data": posts} # reading from the table post



# create post request
@app.post("/posts", status_code= status.HTTP_201_CREATED, response_model= schema.Post)


#expectation (control)from users what to send: title, content str
def create_post( post: schema.PostCreate):
    cursor.execute("""INSERT INTO posts(title, content, published) VALUES (%s, %s, %s) RETURNING *""", 
    (post.title, post.content, post.published))

    new_post = cursor.fetchone()

    conn.commit()
   
    return  new_post



#create get request for specific column
@app.get("/posts/{id}")
def get_post(id: int):  # the client know what is wrong 
   cursor.execute(""" SELECT * FROM posts WHERE id= %s""",(str(id)))
   post = cursor.fetchone()
   if not post:
       raise HTTPException (status_code= status.HTTP_404_NOT_FOUND, detail= 
       f"the request for the message with id {id} not found") 

        
   print(id)
   return {"post_details": post}


#delete the data

@app.delete("/posts/{id}", status_code= status.HTTP_204_NO_CONTENT)
def delete_post(id: int):  # the client know what is wrong 
   cursor.execute(""" DELETE  FROM posts WHERE id = %s  returning *""",(str(id),))
   deleted_post = cursor.fetchone()
   conn.commit()
   if deleted_post == None:
       raise HTTPException (status_code= status.HTTP_404_NOT_FOUND, detail= 
       f"the request for the message with id {id} not found") 

        
 
   return Response(status_code= status.HTTP_204_NO_CONTENT)


#Updating the database
 
@app.put("/posts/{id}", response_model= schema.Post)
def delete_post(id: int, post:schema.PostUpdate):  
   cursor.execute("""
    UPDATE posts SET title = %s , content = %s, published = %s 
    where id = %s
    returning *""",(post.title, post.content, post. published, id) )
    
   updated_post = cursor.fetchone()
   conn.commit()

   if updated_post == None:
       raise HTTPException (status_code= status.HTTP_404_NOT_FOUND, detail= 
       f"the request for the message with id {id} not found") 

        
 
   return  updated_post

