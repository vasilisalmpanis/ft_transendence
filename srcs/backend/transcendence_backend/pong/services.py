from ast import Dict
from typing import Dict, Any, List
from .models        import Pong, pong_model_to_dict
from users.models   import User


def join_game(user , game_id : int):
	'''Joins user to game'''
	game = Pong.objects.get(id=game_id)
	if game.status == 'finished':
		raise ValueError('Game is finished')
	if user in game.players.all():
		return
	if game.players.count() == 2:
		raise ValueError('Game is full')
	game.players.add(user)
	game.save()

def pause_game(game_id: int):
	'''Pauses game'''
	game = Pong.objects.get(id=game_id)
	if game.status == 'running':
		game.status = 'paused'
		game.save()

def resume_game(game_id: int):
	'''Resumes game'''
	game = Pong.objects.get(id=game_id)
	if game.status == 'paused':
		game.status = 'running'
		game.save()
import logging
logger = logging.getLogger(__name__)
def get_side(game_id: int, user: User) -> str:
    '''Returns the side of the user in the game'''
    game = Pong.objects.get(id=game_id)
    first_user = game.players.first()
    if user.username == first_user.username:
        logging.error(f"{user.username} is left {first_user.username}")
        return 'left'
    logging.error(f"{user.username} is right {first_user.username}")
    return 'right'


class PongService:

    @staticmethod
    def get_games(user : User, type : str, skip : int, limit : int) -> List[Dict[Any, Any]]:
        """
        Returns the games of the user
        @param user: User
        @param type: str
        @param skip: int
        @param limit: int
        @return: JsonResponse with game schema
        """
        if type == 'all':
            games = Pong.objects.order_by('-timestamp')[skip:skip+limit]
        elif type == 'pending':
            games = Pong.objects.filter(status='pending').order_by('-timestamp')[skip:skip+limit]
        elif type == 'finished':
            games = Pong.objects.filter(status='finished').order_by('-timestamp')[skip:skip+limit]
        elif type == 'started':
            games = Pong.objects.filter(status='started').order_by('-timestamp')[skip:skip+limit]
        else:
            raise Exception('Invalid type')
        return [pong_model_to_dict(game) for game in games]
    
    @staticmethod
    def check_user_already_joined(user) -> bool:
        """
        Checks if the user has already joined a game
        @param user: User
        @return: bool
        """
        if Pong.objects.filter(players=user).filter(status='pending').exists() or Pong.objects.filter(players=user).filter(status='started').exists():
            return True
        return False

    @staticmethod
    def create_game(user : User) -> Dict[Any, Any]:
        """
        Creates a game for the user and assigns them as participant
        @param user: User
        @return: JsonResponse with game schema
        """
        if PongService.check_user_already_joined(user):
            raise Exception('You have a game in progress')
        game = Pong.objects.create()
        game.players.add(user)
        game.save()
        return pong_model_to_dict(game)
    
    @staticmethod
    def get_game_by_id(game_id : int) -> Dict[Any, Any]:
        """
        Returns the game by id
        @param game_id: int
        @return: JsonResponse with game schema
        """
        game = Pong.objects.filter(id=game_id).first()
        if game is None:
            raise Exception('Game not found')
        return pong_model_to_dict(game)
    

    @staticmethod
    def join_game(user : User, game_id : int) -> Dict[Any, Any]:
        """
        Joins the user to the game
        @param user: User
        @param game_id: int
        @return: JsonResponse with game schema
        """
        game = Pong.objects.filter(id=game_id).first()
        if game is None:
            raise Exception('Game not found')
        if game.status != 'pending':
            raise Exception('Game already started')
        if game.players.filter(id=user.id).exists() and game.players.count() == 2:
            raise Exception('User already joined')
        if PongService.check_user_already_joined(user) and game.players.count() == 2:
            raise Exception('You have a game in progress')
        if not game.players.filter(id=user.id).exists():  
            game.players.add(user)
            game.save()
        return pong_model_to_dict(game)
    

    @staticmethod
    def finish_game(game_id : int, score_1 : int, score_2 : int) -> Dict[Any, Any]:
        """
        Finishes the game
        @param game_id: int
        @return: JsonResponse with game schema
        """
        game = Pong.objects.filter(id=game_id).first()
        if game is None:
            raise Exception('Game not found')
        game.score1 = score_1
        game.score2 = score_2
        game.status = 'finished'
        game.save()
        return pong_model_to_dict(game)
    
    @staticmethod
    def delete_game(game_id : int, user : User) -> None:
        """
        Deletes the game
        @param game_id: int
        """
        game = Pong.objects.filter(id=game_id).first()
        if not game:
            raise Exception('Game not found')
        if game.players.filter(id=user.id).exists() and game.status == 'pending':
            game.delete()
        else:
            raise Exception('You are either not a participant or the game has already started')
