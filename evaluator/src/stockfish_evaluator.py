import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
import logging
import json

from chess import Board
from chess.pgn import GameNode
from flask import Flask, render_template
from flask_restful import Resource, Api
import lichess.api
from lichess.format import PYCHESS
from stockfish import Stockfish

# Constant parameters.
BLUNDER_THRESHOLD = 200
DEBUG = 1
MATE_CP_VALUE = 10000
PORT_NUMBER = 8000
STOCKFISH_PATH = "/bc/Stockfish-sf_15/src/stockfish"
STOCKFISH_THREADS = 4
STOCKFISH_DEPTH = 17

app = Flask(__name__)

class GetPuzzles(Resource):
    """GetPuzzles api call to get user games and generate puzzles."""

    def get(self, username: str):
        """get api entry point.

        Args:
            username (str): username to retrieve puzzles for.

        Returns:
            json of puzzles and status code.
        """
        puzzles = self.eval(username)
        return json.dumps(puzzles), 200

    def eval(self, username: str) -> list:
        """Start evaluation for username to get puzzles.

        Args:
            username (str) : username to retrieve puzzles for.

        Returns:
            list: list of puzzles and solutions.
        """
        if DEBUG:
            app.logger.debug(f'Getting puzzles for {username}')
        full_puzzle_list = []
        games = lichess.api.user_games(username, max=1, format=PYCHESS)

        thread_pool = ThreadPoolExecutor(max_workers=4)
        with thread_pool as executor:
            game_futures = {
                executor.submit(self.evaluate_game, game, username): game
                for game in games
            }
            for future in concurrent.futures.as_completed(game_futures):
                puzzles = future.result()
                if puzzles:
                    full_puzzle_list.extend(puzzles)

        return full_puzzle_list

    def evaluate_game(self, game: GameNode, player: str) -> list:
        """Evaluate single game and generate puzzles from blunders.

        Args:
            game (GameNode): Pychess game object for evaluation.
            player (str): Player whose perspective we are evaluating from.

        Returns:
            list: list of puzzles and solutions for game.
        """
        puzzle_list = []
        sf = Stockfish(
            path=STOCKFISH_PATH,
            depth=STOCKFISH_DEPTH,
            parameters={"Threads": STOCKFISH_THREADS},
        )

        # Determine Color Of Player
        is_white = None
        if game.headers["White"] == player:
            is_white = True
        elif game.headers["Black"] == player:
            is_white = False

        # TODO (dan) Figure out a better way to handle this
        # Make sure the player is in the game
        assert is_white is not None

        # Create variables in prep for evaluation
        last_eval = 0
        last_position = sf.get_fen_position()
        white_turn = True
        for move in game.mainline_moves():
            # Get the best move
            best_move = sf.get_best_move()

            # Make the current move
            sf.make_moves_from_current_position([move])

            # Get the evaluation
            cur_eval_dict = sf.get_evaluation()

            # Need to convert mate to a number...
            if cur_eval_dict["type"] == "cp":
                cur_eval = cur_eval_dict["value"]
            else:
                if cur_eval_dict["value"] < 0:
                    cur_eval = -1 * MATE_CP_VALUE
                else:
                    cur_eval = MATE_CP_VALUE

            # Check if it's the player's turn
            if (white_turn and is_white) or (not white_turn and not is_white):
                if abs(last_eval - cur_eval) >= BLUNDER_THRESHOLD:
                    bd = Board(fen=last_position)
                    if DEBUG:
                        player = "White" if bd.turn else "Black"
                        app.logger.debug(f"Blunder found on {bd.fullmove_number} position is \n Player to Move is {player} \n{bd}")
                    puzzle_list.append(
                        {"position": last_position, "solution": best_move}
                    )

            # Update last values
            last_position = sf.get_fen_position()
            last_eval = cur_eval
            white_turn = not white_turn

        return puzzle_list

@app.route('/')
def index():
    return render_template('index.html')


if __name__ == "__main__":
    api = Api(app)
    api.add_resource(GetPuzzles, "/get_puzzles/<string:username>")
    if DEBUG:
        app.logger.setLevel(logging.DEBUG)
    app.run(host='0.0.0.0', port=PORT_NUMBER, debug=True)
