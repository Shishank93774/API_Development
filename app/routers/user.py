from typing import List, Optional
from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from .. import models, schemas, utils, database, oauth2

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.get("/posts", response_model=List[schemas.PostResponse])
def get_posts_by_user(db: Session = Depends(database.get_db), current_user: schemas.Token = Depends(oauth2.get_current_user),
                      limit: int = 10, offset: int = 0, search_text: Optional[str] = ""):
    # noinspection PyTypeChecker
    posts = (db.query(models.Post).filter((models.Post.owner_id == current_user.id) & (models.Post.title.contains(search_text))).limit(limit).offset(0))

    return posts

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserResponse)
def create_user(user: schemas.UserBase, db: Session = Depends(database.get_db)):
    try:
        user.password = utils.hash(user.password)

        user_dict = user.model_dump()
        user = models.User(**user_dict)
        if user is None:
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="User already exists")

        db.add(user)
        db.commit()
        db.refresh(user)
    except IntegrityError as e:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=f"Command violates integrity: {e}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=f"Error: {e}")

    return user

@router.get("/{id}", response_model=schemas.UserResponse)
def get_user(id: int, db: Session = Depends(database.get_db)):
    id = str(id)

    # noinspection PyTypeChecker
    user = db.query(models.User).filter(models.User.id == id).first()

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return user