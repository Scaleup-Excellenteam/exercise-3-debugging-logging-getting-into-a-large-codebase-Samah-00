import pytest
from unittest.mock import MagicMock, patch
from Piece import Piece, Knight
from enums import Player
from chess_engine import game_state
from ai_engine import chess_ai


# Tests for get_valid_piece_takes(self, game_state) of Knight class:
# Test when no piece can be taken:
def test_get_valid_piece_takes_no_takes(mock_game_state):
    # Set up mock game state where no piece can be taken
    mock_game_state.get_piece.side_effect = lambda row, col: Player.EMPTY
    mock_game_state.is_valid_piece.side_effect = lambda row, col: False

    # Set up Knight on the board
    knight = Knight(Player.PLAYER_1, 3, 3)

    # Verify that no piece can be taken
    assert knight.get_valid_piece_takes(mock_game_state) == []


# Test when all pieces that can be taken belong to the opposite player:
def test_get_valid_piece_takes_opposite_player(mock_game_state):
    # Set up mock game state where all pieces that can be taken belong to the opposite player
    mock_game_state.get_piece.side_effect = lambda row, col: Player.PLAYER_2 if (row + col) % 2 == 0 else Player.EMPTY
    mock_game_state.is_valid_piece.side_effect = lambda row, col: True

    # Set up Knight on the board
    knight = Knight(Player.PLAYER_1, 3, 3)

    # Verify that all pieces that can be taken belong to the opposite player
    assert knight.get_valid_piece_takes(mock_game_state) == [(2, 1), (2, 5), (1, 2), (1, 4), (5, 2), (5, 4), (4, 1), (4, 5)]


# Test when all pieces that can be taken belong to the same player:
def test_get_valid_piece_takes_same_player(mock_game_state):
    # Set up mock game state where all pieces that can be taken belong to the same player
    mock_game_state.get_piece.side_effect = lambda row, col: Player.PLAYER_1 if (row + col) % 2 == 0 else Player.EMPTY
    mock_game_state.is_valid_piece.side_effect = lambda row, col: True

    # Set up Knight on the board
    knight = Knight(Player.PLAYER_1, 3, 3)

    # Verify that no piece can be taken
    assert knight.get_valid_piece_takes(mock_game_state) == []


# Tests for get_valid_peaceful_moves(self, game_state) of Knight class:
def test_get_valid_peaceful_moves_no_moves():
    knight = Knight(Player.PLAYER_1, 0, 0)
    game_state_mock = MagicMock()
    game_state_mock.get_piece.side_effect = lambda r, c: Player.EMPTY
    assert knight.get_valid_peaceful_moves(game_state_mock) == []


def test_get_valid_peaceful_moves_some_moves():
    knight = Knight(Player.PLAYER_1, 3, 3)
    game_state_mock = MagicMock()
    game_state_mock.get_piece.side_effect = lambda r, c: Player.EMPTY if r in [3, 4, 5] and c in [3, 4, 5] else None
    expected_moves = [(2, 1), (2, 5), (1, 2), (1, 4), (5, 2), (5, 4), (4, 1), (4, 5)]
    assert knight.get_valid_peaceful_moves(game_state_mock) == expected_moves


def test_get_valid_peaceful_moves_edge_of_board():
    knight = Knight(Player.PLAYER_1, 0, 0)
    game_state_mock = MagicMock()
    game_state_mock.get_piece.side_effect = lambda r, c: Player.EMPTY if r == 1 and c == 2 else None
    expected_moves = [(2, 1), (2, 3)]
    assert knight.get_valid_peaceful_moves(game_state_mock) == expected_moves


# integration test for get_valid_piece_moves:
@pytest.fixture
def knight():
    return Knight(0, 0, Knight.WHITE)


@pytest.fixture
def get_game_state():
    return game_state()


def test_get_valid_piece_moves(knight):
    game_state = MagicMock(spec=get_game_state)
    game_state.get_piece.side_effect = lambda r, c: None if r in [-1, 8] or c in [-1, 8] else Knight(Knight.BLACK, r, c)
    game_state.is_valid_piece.side_effect = lambda r, c: r not in [-1, 8] and c not in [-1, 8]
    peaceful_moves = [(r, c) for r in range(8) for c in range(8) if abs(r - knight.row_number) + abs(c - knight.col_number) == 3]
    takes = [(r, c) for r in range(8) for c in range(8) if abs(r - knight.row_number) + abs(c - knight.col_number) == 2 and (r, c) not in peaceful_moves]
    expected_moves = peaceful_moves + takes

    with patch.object(knight, 'get_valid_peaceful_moves') as mock_peaceful_moves, patch.object(knight, 'get_valid_piece_takes') as mock_takes:
        mock_peaceful_moves.return_value = peaceful_moves
        mock_takes.return_value = takes

        moves = knight.get_valid_piece_moves(game_state)

        assert set(moves) == set(expected_moves)


# integration test for evaluate_board:
@pytest.fixture
def chess_ai_object():
    return chess_ai()


@pytest.fixture
def mock_game_state():
    game_state = MagicMock()
    game_state.is_valid_piece.side_effect = [
        True, True, False, True, True, True, True, True,
        True, True, True, True, True, True, True, True,
        False, False, False, False, False, False, False, False,
        False, False, False, False, False, False, False, False,
        False, False, False, False, False, False, False, False,
        False, False, False, False, False, False, False, False,
        True, True, True, True, True, True, True, True,
        True, True, False, True, True, True, True, True
    ]
    game_state.get_piece.side_effect = [
        MagicMock(name="black_king", is_player=lambda x: x == "black", get_name=lambda: "k"),
        MagicMock(name="black_queen", is_player=lambda x: x == "black", get_name=lambda: "q"),
        None,
        MagicMock(name="white_pawn", is_player=lambda x: x == "white", get_name=lambda: "p"),
        MagicMock(name="white_knight", is_player=lambda x: x == "white", get_name=lambda: "n"),
        MagicMock(name="white_bishop", is_player=lambda x: x == "white", get_name=lambda: "b"),
        MagicMock(name="white_rook", is_player=lambda x: x == "white", get_name=lambda: "r"),
        MagicMock(name="white_king", is_player=lambda x: x == "white", get_name=lambda: "k")
    ]
    return game_state


def test_evaluate_board(chess_ai_object, mock_game_state):
    expected_score = -160
    actual_score = chess_ai_object.evaluate_board(mock_game_state, Player.PLAYER_1)
    assert actual_score == expected_score
