# import necessary modules
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, create_engine, MetaData
from sqlalchemy.orm import sessionmaker, relationship, Session, declarative_base
from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
from uuid import uuid4

# initialize fastapi app
app = FastAPI()

# database configuration
DATABASE_URL = "sqlite:///./test.db"  # sqlite database url
SECRET_KEY = "your_secret_key"  # secret key for jwt
ALGORITHM = "HS256"  # algorithm for jwt
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # token expiration time

# cors configuration
origins = [
    "http://mijnsite.com"  # allowed origin for cors
]

# add cors middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# database setup
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})  # create database engine
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)  # create session factory
metadata = MetaData()  # metadata for database
Base = declarative_base()  # base class for orm models

# password hashing setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")  # password context for hashing
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")  # oauth2 scheme for token

# user model
class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid4()))  # unique id for user
    username = Column(String, unique=True, index=True, nullable=False)  # username
    email = Column(String, unique=True, index=True, nullable=False)  # email
    password = Column(String, nullable=False)  # hashed password
    role = Column(String, default="user")  # user role
    created_at = Column(DateTime, default=lambda: datetime.now(tz=timezone.utc))  # creation timestamp
    updated_at = Column(DateTime, default=lambda: datetime.now(tz=timezone.utc))  # update timestamp

# category model
class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)  # unique id for category
    name = Column(String, unique=True, index=True, nullable=False)  # category name
    created_at = Column(DateTime, default=lambda: datetime.now(tz=timezone.utc))  # creation timestamp
    updated_at = Column(DateTime, default=lambda: datetime.now(tz=timezone.utc))  # update timestamp

# post model
class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, index=True)  # unique id for post
    title = Column(String, nullable=False)  # post title
    content = Column(String, nullable=False)  # post content
    author_id = Column(String, ForeignKey("users.id"))  # foreign key to user
    category_id = Column(Integer, ForeignKey("categories.id"))  # foreign key to category
    created_at = Column(DateTime, default=lambda: datetime.now(tz=timezone.utc))  # creation timestamp
    updated_at = Column(DateTime, default=lambda: datetime.now(tz=timezone.utc))  # update timestamp
    author = relationship("User")  # relationship to user
    category = relationship("Category")  # relationship to category

# create database tables
Base.metadata.create_all(bind=engine)

# database session management
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# password hashing function
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# password verification function
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# create jwt token function
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.now(tz=timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# decode jwt token function
def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

# pydantic models for request validation
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class PostCreate(BaseModel):
    title: str
    content: str
    category_id: int

class CategoryCreate(BaseModel):
    name: str

class UserLogin(BaseModel):
    username: str
    password: str

# login route
@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user:
        raise HTTPException(status_code=401, detail="incorrect username or password")
    if not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="incorrect username or password")
    access_token = create_access_token(data={"sub": user.id})
    return {"access_token": access_token, "token_type": "bearer"}

# registration route
@app.post("/register")
async def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="username already registered")
    hashed_password = hash_password(user.password)
    new_user = User(username=user.username, email=user.email, password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# get all users route
@app.get("/users")
async def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users

# get single user route
@app.get("/users/{user_id}")
async def get_user(user_id: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="user not found")
    return user

# create user route
@app.post("/users")
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    hashed_password = hash_password(user.password)
    db_user = User(username=user.username, email=user.email, password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# update user route
@app.put("/users/{user_id}")
async def update_user(user_id: str, user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="user not found")
    db_user.username = user.username
    db_user.email = user.email
    db_user.password = hash_password(user.password)
    db_user.updated_at = datetime.now(tz=timezone.utc)
    db.commit()
    return db_user

# delete user route
@app.delete("/users/{user_id}")
async def delete_user(user_id: str, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="user not found")
    db.delete(db_user)
    db.commit()
    return {"message": "user deleted"}

# get all categories route
@app.get("/categories")
async def get_categories(db: Session = Depends(get_db)):
    categories = db.query(Category).all()
    return categories

# get single category route
@app.get("/categories/{category_id}")
async def get_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="category not found")
    return category

# create category route
@app.post("/categories")
async def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    new_category = Category(name=category.name)
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category

# update category route
@app.put("/categories/{category_id}")
async def update_category(category_id: int, category: CategoryCreate, db: Session = Depends(get_db)):
    db_category = db.query(Category).filter(Category.id == category_id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="category not found")
    db_category.name = category.name
    db_category.updated_at = datetime.now(tz=timezone.utc)
    db.commit()
    return db_category

# delete category route
@app.delete("/categories/{category_id}")
async def delete_category(category_id: int, db: Session = Depends(get_db)):
    db_category = db.query(Category).filter(Category.id == category_id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="category not found")
    db.delete(db_category)
    db.commit()
    return {"message": "category deleted"}

# get all posts route
@app.get("/posts")
async def get_posts(db: Session = Depends(get_db)):
    posts = db.query(Post).all()
    return posts

# get single post route
@app.get("/posts/{post_id}")
async def get_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="post not found")
    return post

# create post route
@app.post("/posts")
async def create_post(post: PostCreate, db: Session = Depends(get_db)):
    new_post = Post(title=post.title, content=post.content, category_id=post.category_id)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

# update post route
@app.put("/posts/{post_id}")
async def update_post(post_id: int, post: PostCreate, db: Session = Depends(get_db)):
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if not db_post:
        raise HTTPException(status_code=404, detail="post not found")
    db_post.title = post.title
    db_post.content = post.content
    db_post.category_id = post.category_id
    db_post.updated_at = datetime.now(tz=timezone.utc)
    db.commit()
    return db_post

# delete post route
@app.delete("/posts/{post_id}")
async def delete_post(post_id: int, db: Session = Depends(get_db)):
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if not db_post:
        raise HTTPException(status_code=404, detail="post not found")
    db.delete(db_post)
    db.commit()
    return {"message": "post deleted"}

