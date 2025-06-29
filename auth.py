def login(username, password):
    # Пока просто фиктивная проверка
    print(f"[DEBUG] Авторизация как {username}...")
    if username and password:
        # В будущем здесь будет реальный токен
        with open(".token", "w") as f:
            f.write("dummy_token")
        return True
    return False
