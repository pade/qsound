import pytest
from engine.player import PlayerCommand, InvalidCommand


class TestPlayerCommand:
    def test_createClass(self):
        cmd = PlayerCommand('play')
        assert cmd.command == 'play'
        assert cmd.value is None

    def test_createClassWithValue(self):
        cmd = PlayerCommand('setStart', 4.3)
        assert cmd.command == 'setStart'
        assert cmd.value == 4.3

    def test_createClassError(self):
        with pytest.raises(InvalidCommand):
            PlayerCommand('wrong command')

    def test_fromMessage(self):
        cmd = PlayerCommand.fromMessage({'command': 'loop', 'value': 2})
        assert cmd.command == 'loop'
        assert cmd.value == 2

    def test_fromMessageWithoutValue(self):
        cmd = PlayerCommand.fromMessage({'command': 'loop'})
        assert cmd.command == 'loop'
        assert cmd.value is None

    def test_toMessageWithoutValue(self):
        cmd = PlayerCommand('stop')
        assert cmd.toMessage() == {'command': 'stop'}

    def test_toMessage(self):
        cmd = PlayerCommand('setStart', 4.5)
        assert cmd.toMessage() == {'command': 'setStart', 'value': 4.5}

    def test_toMessageWithNullValue(self):
        cmd = PlayerCommand('setEnd', 0.0)
        assert cmd.toMessage() == {'command': 'setEnd', 'value': 0.0}
