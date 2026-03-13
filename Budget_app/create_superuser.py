import sys
import getpass
import asyncio

from sqlalchemy import select

from src.database.db_helper import db_helper
from src.accounts.models import Account
from src.operations.models import Operation
from src.categories.user_categories.models import UserCategory
from src.auth.models import User
from src.auth.security import get_password_hash

async def main():
    print("--- Создание суперпользователя ---")

    try:
        username = input("Введите имя пользователя: ").strip()

        if not username:
            print("Ошибка: имя пользователя не может быть пустым")
            raise KeyboardInterrupt
        
        email = input("Введите почту: ").strip()
        if not email:
            print("Ошибка: почта не может быть пустой")
            raise KeyboardInterrupt
        
        password = getpass.getpass("Введите пароль: ")
        password_confirm = getpass.getpass("Повторите пароль: ")

        if password != password_confirm:
            print("Ошибка: пароли не совпадают")
            raise KeyboardInterrupt
        
        await create_superuser(username, email, password)

    except KeyboardInterrupt:
        print("Отмена операции...")
        sys.exit(0)

async def create_superuser(username: str, email: str, password: str):
    async with db_helper.session_factory() as session:
        query = select(User).where(
            (User.username == username) | (User.email == email)
        )
        result = await session.scalars(query)
        existing_user = result.first()

        if existing_user:
            print("Ошибка: пользователь с таким username или email уже существует")
            raise KeyboardInterrupt
        
        print("Создание пользователя...")

        hashed_password = get_password_hash(password)

        new_admin_user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            is_admin=True,
            is_staff=True
        )

        session.add(new_admin_user)

        try:
            await session.commit()
            print("Суперпользователь успешно создан!")
        except Exception as e:
            print("Ошибка создания суперпользователя")
            print(str(e))
            await session.rollback()
            raise KeyboardInterrupt
        
if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    asyncio.run(main())
