import time
from typing import Optional
import psycopg2
from psycopg2.extras import RealDictCursor

from fastapi import Body, FastAPI, HTTPException, status, Response
from pydantic import BaseModel
from random import randrange

app = FastAPI()


class Post(BaseModel):
    title: str
    content: str
    published: Optional[bool] = False
    rating: Optional[int] = None


class UpdatedPost(BaseModel):
    title: str
    content: str
    published: Optional[bool] = False


while True:
    try:
        conn = psycopg2.connect(host='localhost', database='fastapidb', user='allgift', password='Matt6:33',
                                cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("Database connection successful")
        break
    except Exception as error:
        print("Database connection failed")
        print("Error", error)
        time.sleep(2)


my_posts = [
    {
        "id": 1,
        "title": "Post 1",
        "content": "This is post 1",
    },
    {
        "id": 2,
        "title": "Post 2",
        "content": "This is post 2",
    },
    {
        "id": 3,
        "title": "Post 3",
        "content": "This is post 3",
    }
]


def find_post(id):
    for p in my_posts:
        if p["id"] == id:
            return p


def find_index_post(id):
    for i, p in enumerate(my_posts):
        if p['id'] == id:
            return i


@app.get("/")
def index():
    return {"message": "Hello World"}


@app.get("/posts")
def get_posts():
    posts = cursor.execute("""SELECT * FROM posts""")
    posts = cursor.fetchall()
    # print(posts)
    return {"all posts": posts}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
def get_posts(post: Post):
    # post_dict = post.dict()
    # post_dict["id"] = randrange(1, 10e9)
    # my_posts.append(post_dict)
    cursor.execute("""INSERT INTO posts(title, content, published) VALUES (%s, %s, %s) RETURNING *;""",
                   (post.title, post.content, post.published))
    new_post = cursor.fetchone()
    conn.commit()
    return {"new_post": new_post}


@app.get("/posts/{id}")
def get_post(id: int):
    # post = find_post(id)
    cursor.execute("""SELECT * FROM posts WHERE id = %s ;""", (str(id), ))
    post = cursor.fetchone()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} not found")
    return post


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    # deleting post
    # find the index in the array that the required id
    # my_posts.pop(index)
    # index = find_index_post(id)
    cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING *;""", (str(id),))
    deleted_post = cursor.fetchone()
    conn.commit()
    if deleted_post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} not found")
    # my_posts.pop(index)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{id}", status_code=status.HTTP_201_CREATED)
def update_post(id: int, post: UpdatedPost):
    # print(post)
    # index = find_index_post(id)
    cursor.execute("""UPDATE posts set title= %s, content= %s, published= %s WHERE id = %s RETURNING *;""",
                   (post.title, post.content, post.published, str(id)))
    updated_post = cursor.fetchone()
    conn.commit()
    if updated_post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} not found")
    # post_dict = post.dict()
    # post_dict['id'] = id
    # my_posts[index] = post_dict
    return {"data": updated_post}
