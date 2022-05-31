import fastapi as fapi
import fastapi.security as sec
import sqlalchemy.orm as _orm
from typing import List
import schemas as sch
import services as serv

from fastapi.middleware.cors import CORSMiddleware

app = fapi.FastAPI()

# enabling CORS in Backend Fast Api
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.post("/api/v1/users")
async def register_user(
        user: sch.UserRequest, daba: _orm.Session = fapi.Depends(serv.get_db)
):
    # call to check if user with email exist
    db_user = await serv.getUserByEmail(email=user.email, db=daba)
    # if user found throw exception
    if db_user:
        raise fapi.HTTPException(status_code=400, detail="Email already exist, try with another email")

    # create the user and return a token
    db_user = await serv.create_user(user=user, db=daba)
    return await serv.create_token(user=db_user)


@app.post("/api/v1/login")
async def login_user(
        form_data: sec.OAuth2PasswordRequestForm = fapi.Depends(),
        db: _orm.Session = fapi.Depends(serv.get_db)
):
    db_user = await serv.login(email=form_data.username,
                               password=form_data.password, db=db)

    # Invalid login then throw exception
    if not db_user:
        raise fapi.HTTPException(status_code=401, detail="Wrong Login Credentials!")

    # create and return the token
    return await serv.create_token(db_user)


@app.get("/api/v1/users/current-user", response_model=sch.UserResponse)
async def current_user(user: sch.UserResponse = fapi.Depends(serv.current_user)):
    return user

@app.post("/api/v1/posts", response_model=sch.PostResponse)
async def create_post(
        post_request: sch.PostRequest,
        user: sch.UserRequest = fapi.Depends(serv.current_user),
        db: _orm.Session = fapi.Depends(serv.get_db)
):
    return await serv.create_post(user=user, db=db, post=post_request)

@app.get("/api/v1/posts/user", response_model=List[sch.PostResponse])
async def get_posts_by_user(
        user: sch.UserRequest = fapi.Depends(serv.current_user),
        db: _orm.Session = fapi.Depends(serv.get_db)
):

    return await serv.get_posts_by_user(user=user, db=db)

@app.get("/api/v1/posts/all", response_model=List[sch.PostResponse])
async def get_posts_by_all(
        db: _orm.Session = fapi.Depends(serv.get_db)
):
    return await serv.get_posts_by_all(db=db)

@app.get("/api/v1/posts/{post_id}/", response_model=sch.PostResponse)
async def get_post_detail(
        post_id:int, db: _orm.Session = fapi.Depends(serv.get_db)
):
    post = await serv.get_post_detail(post_id=post_id, db=db)
    if post is None:
        raise fapi.HTTPException(status_code=404, detail="Post not found")
    return post

@app.get("/api/v1/users/{user_id}/", response_model=sch.UserResponse)
async def get_user_detail(
    user_id:int, db: _orm.Session = fapi.Depends(serv.get_db)
):
    return await serv.get_user_detail(user_id=user_id, db=db)

@app.delete("/api/v1/posts/{post_id}/")
async def delete_post(
        post_id: int,
        db: _orm.Session = fapi.Depends(serv.get_db),
        user: sch.UserRequest = fapi.Depends(serv.current_user),
):

    post = await serv.get_post_detail(post_id=post_id, db=db)

    await serv.delete_post(post=post, db=db)

    return "Post deleted successfully"

@app.put("/api/v1/posts/{post_id}/", response_model=sch.PostResponse)
async def update_post(
        post_id: int,
        post_request: sch.PostRequest,
        db: _orm.Session = fapi.Depends(serv.get_db)
):
    db_post = await serv.get_post_detail(post_id=post_id, db=db)

    return await serv.update_post(post_request=post_request, post=db_post, db=db)