insert_user_query = """
    INSERT INTO users (email, full_name, password)
    VALUES ($1, $2, $3)
    RETURNING id, email, full_name, created_at;
"""
