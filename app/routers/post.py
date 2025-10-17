from typing import List, Optional
from fastapi import Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import func
from .. import models, schemas, database, oauth2

router = APIRouter(
    prefix="/posts",
    tags=["Posts"]
)

# @router.get("/", response_model=List[schemas.PostResponse])
@router.get("/", response_model=List[schemas.PostWithVote])
def get_posts(db: Session = Depends(database.get_db), limit: int = 10, offset: int = 0, search_text: Optional[str] = ""):
    # cursor.execute("""SELECT * FROM posts;""")
    # posts = cursor.fetchall()

    # posts = db.query(models.Post).filter(models.Post.title.contains(search_text)).order_by(models.Post.created_at.desc()).limit(limit).offset(offset)
    # noinspection PyTypeChecker
    posts = (
        db.query(models.Post, func.count(models.Vote.post_id).label("vote_count"))
        .filter(models.Post.title.contains(search_text))
        .join(models.Vote, models.Post.id == models.Vote.post_id, isouter=True)
        .group_by(models.Post.id)
        .order_by(models.Post.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    posts = [{"post": post, "vote_count": vote_count} for post, vote_count in posts]

    return posts

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse)
def create_posts(post: schemas.PostCreate, db: Session = Depends(database.get_db), current_user: schemas.Token = Depends(oauth2.get_current_user)):
    # cursor.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *;""",
    #                (post.title, post.content, post.published))
    # post = cursor.fetchone()
    # conn.commit()
    post_dict = post.model_dump()
    post = models.Post(**post_dict, owner_id=current_user.id)
    db.add(post)
    db.commit()
    db.refresh(post)

    return post

@router.get("/{id}", response_model=schemas.PostWithVote)
def get_post(id: int, db: Session = Depends(database.get_db)):
    # id = str(id)
    # cursor.execute("""SELECT * FROM posts WHERE id = %s;""", (id,))
    # post = cursor.fetchone()
    # noinspection PyTypeChecker
    post = (
        db.query(models.Post, func.count(models.Vote.post_id).label("vote_count")).
        filter(models.Post.id == id)
        .join(models.Vote, models.Post.id == models.Vote.post_id, isouter=True)
        .group_by(models.Post.id)
        .first()
    )

    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    post, vote_count = post

    post = {"post": post, "vote_count": vote_count}

    return post

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(database.get_db), current_user: schemas.Token = Depends(oauth2.get_current_user)):
    id = str(id)
    # cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING *;""", (id,))
    # post = cursor.fetchone()

    # noinspection PyTypeChecker
    filter_query = db.query(models.Post).filter(models.Post.id == id)

    if filter_query.first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    post = filter_query.first()

    if str(post.owner_id) != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")

    filter_query.delete(synchronize_session=False)

    db.commit()
    # conn.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put("/{id}", response_model=schemas.PostResponse)
def update_post(id: int, post: schemas.PostCreate, db: Session = Depends(database.get_db), current_user: schemas.Token = Depends(oauth2.get_current_user)):
    id = str(id)
    # cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *;""",
    #                (post.title, post.content, post.published, id))
    # post = cursor.fetchone()

    # noinspection PyTypeChecker
    filter_query = db.query(models.Post).filter(models.Post.id == id)

    if filter_query.first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    current_post = filter_query.first()

    if str(current_post.owner_id) != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")

    filter_query.update(post.model_dump(), synchronize_session=False)

    db.commit()
    updated_post = filter_query.first()
    # conn.commit()

    return updated_post