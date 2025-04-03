from fastapi import FastAPI, Request, Response, status
from fastapi.routing import APIRoute
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from loguru import logger
from uuid import UUID
from typing import Callable, List
import json
from base64 import b64decode

class JWTAuthMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: FastAPI,
        exclude_paths: List[str] = None,
    ):
        super().__init__(app)
        self.exclude_paths = exclude_paths or ["/docs", "/redoc", "/openapi.json"]
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
        # Check if the path is excluded from authentication
        for path in self.exclude_paths:
            if request.url.path.startswith(path):
                logger.debug(f"Skipping authentication for excluded path: {request.url.path}")
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
        
        # Extract token from Authorization header
        token = auth_header.replace("Bearer ", "").strip()
        
        # Try to process token as JWT
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
                        logger.info(f"User {user_id} authenticated for path: {request.url.path} with JWT")
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
            
            # Store user_id in request state for handlers to use
            request.state.user_id = user_id
            
            # Continue to next middleware or route handler
            return await call_next(request)
        except ValueError:
            logger.error(f"Invalid user_id format in token: {auth_header}")
            return Response(
                content='{"detail":"Invalid authorization token"}',
                status_code=status.HTTP_401_UNAUTHORIZED,
                media_type="application/json"
            ) 