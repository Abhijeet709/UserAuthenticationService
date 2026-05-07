user_by_email_query = """
    SELECT id, email, full_name, password
    FROM users
    WHERE email = $1
    LIMIT 1;
"""
