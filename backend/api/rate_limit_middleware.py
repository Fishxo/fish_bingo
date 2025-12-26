"""
Rate limiting middleware for promo-safe registration
Uses Redis-based rate limiting to prevent abuse
"""
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from api.redis_utils import check_rate_limit
import logging

logger = logging.getLogger(__name__)


class RateLimitMiddleware(MiddlewareMixin):
    """
    Rate limiting middleware for registration endpoints
    
    Limits:
    - Registration: 3 per minute per IP
    - Telegram ID: 1 per hour
    - Referral reward: 10 per day per referrer (handled in Celery task)
    """
    
    # Endpoints that need rate limiting
    RATE_LIMITED_PATHS = [
        '/api/auth/telegram-register/',
        '/api/auth/telegram/',
    ]
    
    # Telegram bot endpoints (handled separately in bot.py)
    TELEGRAM_BOT_PATHS = [
        '/telegram/webhook/',
    ]
    
    def process_request(self, request):
        """Check rate limits before processing request"""
        path = request.path
        
        # Check if this path needs rate limiting
        if any(path.startswith(limited_path) for limited_path in self.RATE_LIMITED_PATHS):
            # Get client IP
            client_ip = self._get_client_ip(request)
            
            # Check IP-based rate limit (3 registrations per minute)
            is_allowed, remaining = check_rate_limit(
                action='register_ip',
                identifier=client_ip,
                limit=3,
                window_seconds=60
            )
            
            if not is_allowed:
                logger.warning(f"Rate limit exceeded for IP {client_ip} on {path}")
                return JsonResponse(
                    {
                        'error': 'Rate limit exceeded',
                        'message': 'Too many registration attempts. Please try again in a minute.',
                        'retry_after': 60
                    },
                    status=429
                )
        
        return None
    
    def _get_client_ip(self, request):
        """Get client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', 'unknown')
        return ip

