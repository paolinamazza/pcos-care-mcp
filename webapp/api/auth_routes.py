"""
Authentication routes to be included in main.py
Copy these routes into main.py after health check section
"""

# ============================================================================
# Authentication Routes
# ============================================================================

@app.post("/api/auth/register", response_model=Token)
async def register(user_data: UserRegister):
    """Register a new user"""
    try:
        # Create user
        user = create_user(
            email=user_data.email,
            username=user_data.username,
            password=user_data.password,
            full_name=user_data.full_name
        )

        # Create access token
        access_token = create_access_token(
            data={"sub": user.id},
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )

        return {
            "access_token": access_token,
            "token_type": "bearer"
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")


@app.post("/api/auth/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login with username/email and password"""
    user = authenticate_user(form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username/email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Update last login
    update_last_login(user.id)

    # Create access token
    access_token = create_access_token(
        data={"sub": user.id},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@app.get("/api/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Get current authenticated user info"""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "username": current_user.username,
        "full_name": current_user.full_name,
        "is_active": current_user.is_active,
        "has_anthropic_key": bool(current_user.anthropic_api_key),
        "has_openai_key": bool(current_user.openai_api_key)
    }


@app.put("/api/auth/api-keys")
async def update_api_keys(
    keys_data: UserAPIKeysUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """Update user's API keys for AI services"""
    session = db_manager.get_session()

    try:
        user = session.query(User).filter(User.id == current_user.id).first()

        if keys_data.anthropic_api_key is not None:
            user.anthropic_api_key = keys_data.anthropic_api_key

        if keys_data.openai_api_key is not None:
            user.openai_api_key = keys_data.openai_api_key

        session.commit()

        return {
            "success": True,
            "message": "API keys updated successfully",
            "has_anthropic_key": bool(user.anthropic_api_key),
            "has_openai_key": bool(user.openai_api_key)
        }

    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update API keys: {str(e)}")
    finally:
        session.close()
