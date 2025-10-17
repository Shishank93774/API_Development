from typing import List, Optional
from fastapi import Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from .. import models, schemas, database, oauth2

router = APIRouter(
    prefix="/vote",
    tags=["Votes"]
)


# noinspection PyTypeChecker,PyShadowingNames
@router.post("/", status_code=status.HTTP_201_CREATED)
def vote(vote: schemas.Vote, db: Session = Depends(database.get_db), current_user: schemas.Token = Depends(oauth2.get_current_user)):

    filter_query = db.query(models.Vote).filter(models.Vote.post_id == vote.post_id)
    post = filter_query.first()
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    filter_query = filter_query.filter(models.Vote.user_id == current_user.id)
    found_vote = filter_query.first()

    if vote.dir:
        if found_vote:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already voted for this post")

        new_vote = models.Vote(post_id=vote.post_id, user_id=current_user.id)
        db.add(new_vote)
    else:
        if not found_vote:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vote not found")

        filter_query.delete(synchronize_session=False)

    db.commit()
    return {"message": "Vote successful"}
