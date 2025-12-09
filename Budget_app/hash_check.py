from src.auth.security import get_password_hash, verify_password

# 1. Хешируем пароль
password = "super_secret_password"
hashed = get_password_hash(password)

print(f"Original: {password}")
print(f"Hashed:   {hashed}")

# 2. Проверяем правильный пароль
is_correct = verify_password("super_secret_password", hashed)
print(f"Verification (Correct): {is_correct}")  # Должно быть True

# 3. Проверяем неправильный пароль
is_wrong = verify_password("wrong_password", hashed)
print(f"Verification (Wrong):   {is_wrong}")    # Должно быть False