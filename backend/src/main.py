from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

from src.config.settings import AppSettings
from src.web.fastapi.auth_router import auth_router
from src.web.fastapi.films_router import films_router
from src.web.fastapi.playlists_router import playlists_router
from src.web.fastapi.users_router import users_router
from src.dependencies import lifespan

app_settings = AppSettings().from_yaml()

app = FastAPI(
    title=app_settings.APP_NAME,
    lifespan=lifespan,
    root_path=f"/api/v{str(app_settings.API_VERSION)}",
    openapi_tags=[
        {
            "name": "auth",
            "description": "Входная точка. Выдает access_token по login, password и производит регистрацию пользователей.",
        },
        {
            "name": "films",
            "description": "Реализует операции поиска, а также добавления, оценки и прочей персонализации фильмов. Требует access_token в куки.",
        },
        {
            "name": "playlists",
            "description": "Реализует операции над плейлистами. Требует access_token в куки.",
        },
        {
            "name": "users",
            "description": "Реализует операции кастомизации профиля, подписок. Требует access_token в куки."
        }
    ],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=app_settings.ORIGINS,  # указываем конкретный origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(films_router)
app.include_router(playlists_router)
app.include_router(users_router)
app.include_router(auth_router)


@app.get("/")
def root():
    return RedirectResponse(url="/docs")
