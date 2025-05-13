from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Optional
import uvicorn

app = FastAPI()

# Временное хранилище для пользователей
fake_users_db = {}

# Модель пользователя
class User(BaseModel):
    username: str
    email: str
    full_name: Optional[str] = None

# Модель для аутентификации
class UserInDB(User):
    hashed_password: str

# OAuth2 схема
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Эндпойнт регистрации пользователя
@app.post("/register")
async def register(user: UserInDB):
    if user.username in fake_users_db:
        raise HTTPException(status_code=400, detail="User already exists")
    fake_users_db[user.username] = user
    return {"msg": "User registered successfully"}

# Эндпойнт аутентификации
@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = fake_users_db.get(form_data.username)
    if not user or user.hashed_password != form_data.password:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    return {"access_token": form_data.username, "token_type": "bearer"}

# Эндпойнт получения информации о пользователе
@app.get("/users/me")
async def read_users_me(token: str = Depends(oauth2_scheme)):
    user = fake_users_db.get(token)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user

# Эндпойнт обновления профиля
@app.put("/users/me")
async def update_user(user: UserInDB, token: str = Depends(oauth2_scheme)):
    if token not in fake_users_db:
        raise HTTPException(status_code=401, detail="Not authenticated")
    fake_users_db[token] = user
    return {"msg": "User updated successfully"}

# Эндпойнт выхода из системы
@app.post("/logout")
async def logout(token: str = Depends(oauth2_scheme)):
    if token not in fake_users_db:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return {"msg": "User logged out successfully"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
