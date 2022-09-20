import enum
from genericpath import exists
from typing import Optional
from fastapi import FastAPI, Body, Response, status, HTTPException
# from fastapi.params import Body
from random import randrange

from pydantic import BaseModel
import psycopg2 #standard python library(not ORM) to talk to db using sql queries
from psycopg2.extras import RealDictCursor
import time

# py -3 -m venv venv #create virtual environment
# uvicorn main:app --reload
# .\venv\Scripts\activate.bat

# pip install fastapi[all] #to install package
# pip freeze #to list installed packages/dependencies

app = FastAPI()

# pydantic schema
# performs automatic validation


class Post(BaseModel):
    title: str
    content: str
    published: bool = True  # defaults to true ie optional field for user
    # rating: Optional[int] = None


while True:
    try:
        conn = psycopg2.connect(host='localhost', database='fastapi',
                                user='postgres', password='postgres', cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("db connection established")
        break
    except Exception as error:
        print("db connection error")
        print("error: ", error)
        time.sleep(3)


class PostTitlePatch(BaseModel):
    title: str


my_posts = [{"title": "title of post 1", "content": "content of post 1", "id": 1}, {
    "title": "title of post 2", "content": "content of post 2", "id": 2}]


def find_post(id):
    for p in my_posts:
        if p["id"] == id:
            return p


def remove_post(id):
    i = 0
    for p in my_posts:
        if p["id"] == id:
            my_posts.pop(i)
            return my_posts
        i = i+1


def find_post_index(id):
    for i, p in enumerate(my_posts):
        if p["id"] == id:
            return i


@app.get("/login")
def login_user():
    # return {"Hey": "World"}
    return "Welcome to my hood nigga"


@app.get("/posts")
def get_posts():
    cursor.execute("""SELECT * FROM posts""")
    posts = cursor.fetchall()
    print(posts)
    return {"data": posts}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
# def create_posts(payload: dict = Body(...)):
def create_post(post: Post):
    # print(payload)
    # print(new_post.rating)
    # print(post.dict())  # converts pydantic model to dictionary
    # post_dict = post.dict()
    # post_dict["id"] = randrange(0, 10000000)
    # my_posts.append(post_dict)
    # return {"message": "succesfully created a post", "new_post": f"title: {payload['title']}, content: {payload['content']}"}

    # cursor.execute(f"INSERT INTO posts (title, content, published) VALUES({post.title}, {post.content}, {post.published})") ## vulnerable to SQL injection 
    cursor.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *""", (post.title, post.content, post.published)) ## performs input sanitization
    new_post = cursor.fetchone() ## staged changes
    conn.commit() ## commit changes
    return {"data": new_post}


@app.get("/posts/{id}")
def get_post(id: int):
    # print(id) #id extracted from path parameter is by default a string
    # post = find_post(int(id))
    cursor.execute("""SELECT * from posts WHERE id = %s""", (str(id), ))
    post = cursor.fetchone()
    # print(post)

    # post = find_post(id)
    if not post:
        # response.status_code = status.HTTP_404_NOT_FOUND
        # return {"detail":f"post with id {id} not found"}
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id {id} not found")
    return {"post_detail": post}


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    # remove_post(id)
    # return {"data": remove_post(id)}

    cursor.execute("""DELETE from posts WHERE id = %s RETURNING *""", (str(id), ))
    deleted_post = cursor.fetchone()
    conn.commit()
    # index = find_post_index(id)

    if deleted_post == None:
        raise HTTPException(status.HTTP_404_NOT_FOUND,
                            f"post with id {id} does not exist")

    # my_posts.pop(index)
    # return {'message': f"post {id} was successfully deleted"}
    return Response(status_code=status.HTTP_204_NO_CONTENT)



@app.patch("/posts/{id}")
def update_post_title(id: int, post: PostTitlePatch):
    # print(post)
    
    post = post.dict()
    npost = find_post(id)

    if npost == None:
        raise HTTPException(status.HTTP_404_NOT_FOUND,
                            f"post with id {id} does not exist")

    npost["title"] = post['title']

    return {"data": my_posts}


@app.put("/posts/{id}")
def update_post(id: int, post: Post):
    # print(post)

    # index = find_post_index(id)

    cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s where id = %s RETURNING *""", (post.title, post.content, post.published, str(id)))
    updated_post = cursor.fetchone()
    conn.commit()

    if updated_post == None:
        raise HTTPException(status.HTTP_404_NOT_FOUND,
                            f"post with id {id} does not exist")



    # post_dict = post.dict()
    # post_dict['id'] = id
    # my_posts[index] = post_dict

    return {"message": updated_post}


# docs/redoc

# uvicorn app.main:app --reload

# pip freeze, list all pip installed packages
