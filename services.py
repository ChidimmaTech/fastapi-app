import database as db
import models as mod
import fastapi.security as sec
import sqlalchemy.orm as _orm
import schemas as sch
import email_validator as ev
import fastapi as fapi
import passlib.hash as hash
import jwt as j
_JWT_SECRET ="sygoyuyrfiuotyo"
oauth2schema = sec.OAuth2PasswordBearer("/api/v1/login")

def create_db():
    return db.Base.metadata.create_all(bind=db.engine)

# create_db()

def get_db():
    daba = db.SessionLocal()
    try:
        yield daba
    finally:
        daba.close()

# create_db();

async def getUserByEmail(email: str, db: _orm.Session):
    return db.query(mod.UserModel).filter(mod.UserModel.email == email).first()

async def create_user(user: sch.UserRequest, db: _orm.session):
#     check for valid email
    try:
        isValid = ev.validate_email(email=user.email)
        email = isValid.email
    except ev.EmailNotValidError:
        raise fapi.HTTPException(status_code=400, detail="Provide valid Email")

    # convert normal password to hash form
    hashed_password = hash.bcrypt.hash(user.password_hash)

    # create the user model to be saved in database
    user_obj = mod.UserModel(
        email=email,
        name=user.name,
        phone=user.phone,
        password_hash=hashed_password
    )
    #save the user in the db
    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)
    return user_obj

async def create_token(user: mod.UserModel):
    # convert user model to user schema
    user_schema = sch.UserResponse.from_orm(user)
    print(user_schema)

    # convert object to dictionary
    user_dict = user_schema.dict()
    del user_dict["created_at"]

    token = j.encode(user_dict, _JWT_SECRET)

    return dict(access_token=token, token_type="bearer")

async def login(email: str, password: str, db: _orm.Session):
    db_user = await getUserByEmail(email=email, db=db)

    # RETURN FALSE IF NO USER WITH EMAIL FOUND
    if not db_user:
        return False

    # RETURN FALSE IF NO USER WITH PASSWORD FOUND
    if not db_user.password_verification(password=password):
        return False

    return db_user

async def current_user(db: _orm.Session = fapi.Depends(get_db),
                       token: str = fapi.Depends(oauth2schema)):
    try:
        payload = j.decode(token, _JWT_SECRET, algorithms=["HS256"])
        # Get user by Id and Id is already available in the decoded user payload along with email, phone and name
        db_user = db.query(mod.UserModel).get(payload["id"])
    except:
        raise fapi.HTTPException(status_code=401, detail="Wrong Credentials")

    # If all ok then return the OTO/Schema version of User
    return sch.UserResponse.from_orm(db_user)

async def create_post(user: sch.UserResponse, db: _orm.Session,
                      post: sch.PostRequest):
    post = mod.PostModel(**post.dict(), user_id=user.id)
    db.add(post)
    db.commit()
    db.refresh(post)

    # convert the Post Model to Post DTO/Schema and return to API layer
    return sch.PostResponse.from_orm(post)

async def get_posts_by_user(user: sch.UserResponse, db: _orm.Session):
    posts = db.query(mod.PostModel).filter_by(user_id=user.id)

    # convert each post model to post schema and make a list to be returned
    return list(map(sch.PostResponse.from_orm, posts))

async def get_posts_by_all(db: _orm.Session):
    posts = db.query(mod.PostModel)

    # convert each post model to post schema and make a list to be returned
    return list(map(sch.PostResponse.from_orm, posts))

async def get_post_detail(post_id: int, db: _orm.Session):
    db_post = db.query(mod.PostModel).filter(mod.PostModel.id==post_id).first()
    if db_post is None:
        raise fapi.HTTPException(status_code=404, detail="Post not found")
    # return sch.PostResponse.from_orm(db_post)
    return db_post

async def get_user_detail(user_id: int, db: _orm.Session):
    db_user = db.query(mod.UserModel).filter(mod.UserModel.id==user_id).first()
    if db_user is None:
        raise fapi.HTTPException(status_code=404, detail="User not found")
    return sch.UserResponse.from_orm(db_user)

async def delete_post(post: mod.PostModel, db: _orm.Session):
    db.delete(post)
    db.commit()

async def update_post(
        post_request: sch.PostRequest,
        post: mod.PostModel,
        db: _orm.Session
):
    post.post_title = post_request.post_title
    post.post_description = post_request.post_description
    post.post_image = post_request.post_image

    db.commit()
    db.refresh(post)

    return sch.PostResponse.from_orm(post)