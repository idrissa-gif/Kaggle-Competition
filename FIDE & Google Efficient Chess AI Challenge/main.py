from Chessnut import Game
import subprocess
import os
import random


class ChessEngine:
    def __init__(self, engine_path):
        try:
            self.engine = subprocess.Popen(
                [engine_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
        except:
            self.engine = subprocess.Popen(
                ['./mcu-max-uci'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
        self._initialize_engine()

    def _initialize_engine(self):
        self._send_command("uci")
        while True:
            output = self._read_output()
            if output == "uciok":
                break

        self._send_command("setoption name Hash value 1")

    def _send_command(self, command):
        self.engine.stdin.write(command + "\n")
        self.engine.stdin.flush()

    def _read_output(self):
        output = self.engine.stdout.readline().strip()
        return output

    def get_best_move(self, fen, movetime = 100):
        self._send_command(f"position fen {fen}")
        self._send_command(f"go movetime {movetime}")
        best_move = None
        while True:
            output = self._read_output()
            if output.startswith("bestmove"):
                best_move = output.split()[1]
                break
        self._send_command("setoption name Clear Hash")
        return best_move

    def stop(self):
        self._send_command("quit")
        self.engine.terminate()
        self.engine.wait()

ultima = None
def chess_bot(obs):
    global ultima
    fen = obs['board']
    engine_path = '/kaggle_simulations/agent/mcu-max-uci'
    if ultima is None:
        ultima = ChessEngine(engine_path)
    best_move = ultima.get_best_move(fen)

    # Fix for an issue where the promoting move does not actually promote pawns.
    # Changes a pawn move of f7f8 to f7f8q which is recognised.
    if ((best_move[1] == '7' and best_move[3] == '8') or (best_move[1] == '2' and best_move[3] == '1')):
        game = Game(fen)  
        moves = list(game.get_moves())

        promote = False
        for move in moves:
            if len(move) == 5 and best_move in move:
                promote = True
                break

        if promote:
            best_move += 'q'
    return best_move
