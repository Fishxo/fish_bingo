"""
Auto game manager - creates new games after completion
"""
from django.utils import timezone
from datetime import timedelta
from .models import Game, GameSettings
from .game_logic import start_game
import random


def create_new_game_after_completion(completed_game):
    """Create a new waiting game after a game completes"""
    # Get settings from database
    settings = GameSettings.get_settings()
    # Create new game with bet amount from settings
    new_game = Game.objects.create(
        status='waiting',
        bet_amount=settings.bid_amount,
        derash_amount=0
    )
    
    # Add fake users immediately if system accounts are enabled
    if settings.allow_system_account:
        add_fake_users_to_game_immediately(new_game)
    
    return new_game


def check_and_create_new_game():
    """Check if we need to create a new game"""
    # Check if there's already a waiting or active game
    existing_game = Game.objects.filter(status__in=['waiting', 'active']).first()
    
    if existing_game:
        # Ensure fake users are added if system accounts are enabled
        if existing_game.status == 'waiting':
            settings = GameSettings.get_settings()
            if settings.allow_system_account:
                from .fake_user_manager import get_fake_user_count_for_game
                fake_count = get_fake_user_count_for_game(existing_game)
                if fake_count == 0:
                    add_fake_users_to_game_immediately(existing_game)
        return existing_game
    
    # Get the most recent completed game
    last_completed = Game.objects.filter(status='completed').order_by('-completed_at').first()
    
    if last_completed:
        # Create new game with bet amount from settings
        return create_new_game_after_completion(last_completed)
    
    # If no games exist at all, create a new one with bet amount from settings
    settings = GameSettings.get_settings()
    new_game = Game.objects.create(
        status='waiting',
        bet_amount=settings.bid_amount,
        derash_amount=0
    )
    
    # Add fake users immediately if system accounts are enabled
    if settings.allow_system_account:
        add_fake_users_to_game_immediately(new_game)
    
    return new_game


def add_fake_users_to_game_immediately(game):
    """Add fake users to a game with staggered selections and simulate card changes
    Also schedules a task to adjust fake users at 5 seconds before timer ends
    """
    from .fake_user_manager import (
        initialize_fake_users,
        get_random_fake_users
    )
    from .tasks import task_simulate_fake_user_selections, task_adjust_fake_users_before_game_start
    
    # Initialize fake users if needed
    initialize_fake_users()
    
    # Randomly select 15-30 fake users
    fake_user_count = random.randint(15, 30)
    fake_users = get_random_fake_users(fake_user_count)
    
    # Schedule fake user selections with delays using Celery
    # This will handle staggered selections and card changes
    fake_user_ids = [fu.id for fu in fake_users]
    task_simulate_fake_user_selections.delay(game.id, fake_user_ids)
    
    # Schedule task to adjust fake users at 5 seconds before timer ends
    # This will reduce fake users based on real player count
    from .models import GameSettings
    settings = GameSettings.get_settings()
    timer_seconds = settings.card_selection_timer
    # Schedule at (timer_seconds - 5) seconds from now
    countdown = max(0, timer_seconds - 5)
    task_adjust_fake_users_before_game_start.apply_async(args=[game.id], countdown=countdown)
    
    print(f"Scheduled {len(fake_user_ids)} fake users for game {game.id}, will adjust at {countdown}s before game starts")
    return fake_user_ids

