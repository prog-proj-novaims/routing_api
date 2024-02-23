# importing fastapi dependencies

from fastapi import FastAPI, Response, status, HTTPException
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional, Any, List 
import random
import psycopg2 # sql alchemy driver to talk to the database
from psycopg2.extras import RealDictCursor 
import time  
import json


from api import  schema


app= FastAPI()

    



#Connect to your postgres DB
while True:
    try:
        conn = psycopg2.connect(host = 'localhost', database = 'routing',
        user = 'postgres', password = "postgres", cursor_factory= RealDictCursor)
        cursor = conn.cursor()
        print("Database connected successfully")
        break


    except Exception as error:
        print("connection to the database failed")
        print("Error:", error)
        time.sleep(2)




# Check if id exists in results_routes_final table
def id_exists_in_results_table(id: int) -> bool:
    try:
        cursor.execute("""
            SELECT EXISTS(SELECT 1 FROM novaims.results_routes_final WHERE polygon_id = %s)
        """, (id,))
        return cursor.fetchone()['exists']
    except Exception as e:
        print("Error checking id in results_routes_final table:", e)
        raise HTTPException(status_code=500, detail="Internal server error")


# Check if id exists in tb_origin_polygons table
def id_exists_in_origin_table(id: int) -> bool:
    try:
        cursor.execute("""
            SELECT EXISTS(SELECT 1 FROM novaims.tb_origin_polygons WHERE fid = %s)
        """, (id,))
        return cursor.fetchone()['exists']
    except Exception as e:
        print("Error checking id in tb_origin_polygons table:", e)
        raise HTTPException(status_code=500, detail="Internal server error")


# Calculate shortest path
def calculate_shortest_path(id: int):
    cursor.execute("SELECT novaims.route_calc_proj(%s)", (id,))
    # Commit the transaction to ensure the function is executed in the database
    cursor.connection.commit()


@app.get("/results_routes_final/{id}")
def get_post(id: int):
    # Check if id exists in results_routes_final table
    if not id_exists_in_results_table(id):
        # Check if id exists in tb_origin_polygons table
        if id_exists_in_origin_table(id):
            # Calculate shortest path
            calculate_shortest_path(id)
            # Retrieve the calculated results
            cursor.execute("""
                SELECT  polygon_id, route_km, ST_AsGeoJSON( route_geom ) FROM novaims.results_routes_final WHERE polygon_id = %s
            """, (id,))
            route_km = cursor.fetchone()
            if not route_km:
                raise HTTPException(status_code=404, detail=f"No route_km found for ID {id}.")
            
            return {"route_km": route_km}
        else:
            raise HTTPException(status_code=404, detail=f"ID {id} not found in origin table.")
    
    # If the ID exists in results_routes_final table, retrieve the data
    cursor.execute("""
        SELECT polygon_id, route_km, ST_AsGeoJSON( route_geom ) FROM novaims.results_routes_final WHERE polygon_id = %s
    """, (id,))
    route_km = cursor.fetchall()
    if not route_km:
        raise HTTPException(status_code=404, detail=f"No route_km found for ID {id}.")
    
    return {"calculated route": route_km}





#create get request
@app.get("/results_routes_final")
def get_post():
    cursor.execute("""SELECT * FROM novaims.results_routes_final""")
    posts = cursor.fetchall()
    #print(posts)
    return  posts # reading from the table post



# create post request
@app.post("/posts", status_code= status.HTTP_201_CREATED, response_model= schema.PostCreate)


#expectation (control)from users what to send: title, content str
# Check if id exists in tb_origin_polygons table
def id_exists_in_origin_table(id: int, cursor) -> bool:
    cursor.execute("SELECT EXISTS(SELECT 1 FROM novaims.tb_origin_polygons WHERE fid = %s)", (id,))
    return cursor.fetchone()[0]

# Create a Pydantic model for the request body
class DrawnGeometry(BaseModel):
    geometry: dict

# POST endpoint to receive drawn geometry
@app.post("/drawn_geometry")
def process_drawn_geometry(drawn_geometry: DrawnGeometry):
    # You can process the drawn geometry here
    geometry = drawn_geometry.geometry
    # For example, you can save it to the database or perform further analysis
    return {"message": "Drawn geometry received successfully"}






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
 
@app.put("/posts/{id}", response_model= schema.PostCreate)
def update_post(id: int, post:schema.PostUpdate):  
   cursor.execute("""
    UPDATE posts SET title = %s , content = %s, published = %s 
    where id = %s
    returning *""",(post.title, post.content, post. published, id) )
    
   updated_post = cursor.fetchone()
   conn.commit()

   if updated_post == None:
       raise HTTPException (status_code= status.HTTP_404_NOT_FOUND, detail= 
       f"the request for the message with id {id} not found") 

        
 
   return updated_post

