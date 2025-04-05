from fastapi import Header, HTTPException, status, Request, Response, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from loguru import logger
from typing import Optional, Annotated, Callable
from uuid import UUID
import json
from base64 import b64decode

# Создаем объект схемы безопасности для запросов
security_scheme = HTTPBearer()

async def extract_user_id(credentials: HTTPAuthorizationCredentials = Depends(security_scheme)) -> UUID:
    """
    Extract user_id from the Authorization header using HTTPBearer security scheme.
    
    Args:
        credentials: The credentials extracted from the Authorization header
        
    Returns:
        UUID: The user ID extracted from the token
        
    Raises:
        HTTPException: If the Authorization header is missing or invalid
    """
    try:
        # Получаем токен из credentials
        token = credentials.credentials
        logger.debug(f"Received token: {token}")
        
        # Проверяем, является ли токен JWT форматом
        if '.' in token and len(token.split('.')) == 3:
            try:
                # Разделяем JWT на части
                header_b64, payload_b64, signature = token.split('.')
                
                # Декодируем payload из base64
                # Нормализуем base64 строку, добавляя padding если необходимо
                padding_needed = len(payload_b64) % 4
                if padding_needed:
                    payload_b64 += '=' * (4 - padding_needed)
                
                try:
                    # Иногда base64 содержит URL-safe символы
                    payload_b64 = payload_b64.replace('-', '+').replace('_', '/')
                    payload_bytes = b64decode(payload_b64)
                    payload = json.loads(payload_bytes)
                    logger.debug(f"Decoded JWT payload: {payload}")
                    
                    # Ищем uid в payload
                    if 'uid' in payload:
                        user_id = UUID(payload['uid'])
                        logger.info(f"Authenticated user with JWT, ID: {user_id}")
                        return user_id
                    else:
                        logger.error("JWT payload does not contain uid field")
                        raise HTTPException(
                            status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid JWT token format: missing uid"
                        )
                except Exception as e:
                    logger.error(f"Error decoding JWT payload: {e}")
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid JWT token format"
                    )
            except Exception as e:
                logger.error(f"Error processing JWT token: {e}")
                # Если не удалось обработать как JWT, пробуем как простой UUID
                pass
        
        # Пробуем обработать как прямой UUID
        try:
            user_id = UUID(token)
            logger.info(f"User authenticated with UUID: {user_id}")
            return user_id
        except ValueError as e:
            logger.error(f"Token is neither a valid JWT with uid nor a UUID: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization token"
            )
        
    except Exception as e:
        logger.error(f"Unexpected error during token processing: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization token"
        )

class JWTAuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware to handle JWT authentication.
    
    Checks the Authorization header in each request and extracts the user_id.
    
    Public routes can be exempt from authentication by adding them to the
    public_paths list.
    """
    
    def __init__(
        self,
        app,
        exclude_paths: list[str] = None
    ):
        super().__init__(app)
        self.exclude_paths = exclude_paths or ["/docs", "/openapi.json", "/redoc"]
        logger.info(f"JWT Auth Middleware initialized with excluded paths: {self.exclude_paths}")
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process each request through the middleware.
        
        Args:
            request: The incoming request
            call_next: The next middleware/route handler
            
        Returns:
            Response: The response from the route handler
        """
        # Check if the path is in the public paths list
        for path in self.exclude_paths:
            if request.url.path.startswith(path):
                logger.debug(f"Skipping authentication for public path: {request.url.path}")
                return await call_next(request)
        
        # Get the authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            logger.error(f"Authorization header missing for path: {request.url.path}")
            return Response(
                content='{"detail":"Authorization header is required"}',
                status_code=status.HTTP_401_UNAUTHORIZED,
                media_type="application/json"
            )
        
        try:
            # Extract JWT token from header
            token = auth_header.replace("Bearer ", "").strip()
            
            # Проверяем, является ли токен JWT форматом
            if '.' in token and len(token.split('.')) == 3:
                try:
                    # Разделяем JWT на части
                    header_b64, payload_b64, signature = token.split('.')
                    
                    # Декодируем payload из base64
                    # Нормализуем base64 строку, добавляя padding если необходимо
                    padding_needed = len(payload_b64) % 4
                    if padding_needed:
                        payload_b64 += '=' * (4 - padding_needed)
                    
                    try:
                        # Иногда base64 содержит URL-safe символы
                        payload_b64 = payload_b64.replace('-', '+').replace('_', '/')
                        payload_bytes = b64decode(payload_b64)
                        payload = json.loads(payload_bytes)
                        logger.debug(f"Decoded JWT payload: {payload}")
                        
                        # Ищем uid в payload
                        if 'uid' in payload:
                            user_id = UUID(payload['uid'])
                            logger.info(f"User {user_id} authenticated for path: {request.url.path}")
                            request.state.user_id = user_id
                            return await call_next(request)
                        else:
                            logger.error("JWT payload does not contain uid field")
                            return Response(
                                content='{"detail":"Invalid JWT token format: missing uid"}',
                                status_code=status.HTTP_401_UNAUTHORIZED,
                                media_type="application/json"
                            )
                    except Exception as e:
                        logger.error(f"Error decoding JWT payload: {e}")
                        return Response(
                            content='{"detail":"Invalid JWT token format"}',
                            status_code=status.HTTP_401_UNAUTHORIZED,
                            media_type="application/json"
                        )
                except Exception as e:
                    logger.error(f"Error processing JWT token: {e}")
                    # Если не удалось обработать как JWT, пробуем как простой UUID
                    pass
            
            # Try to handle as direct UUID
            try:
                user_id = UUID(token)
                logger.info(f"User {user_id} authenticated for path: {request.url.path}")
                
                # Set user_id in request state for downstream handlers
                request.state.user_id = user_id
                
                # Continue processing the request
                return await call_next(request)
            except ValueError:
                logger.error(f"Token is neither a valid JWT with uid nor a UUID")
                return Response(
                    content='{"detail":"Invalid authorization token"}',
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    media_type="application/json"
                )
        except Exception as e:
            logger.error(f"Unexpected error during token processing: {e}")
            return Response(
                content='{"detail":"Invalid authorization token"}',
                status_code=status.HTTP_401_UNAUTHORIZED,
                media_type="application/json"
            ) 