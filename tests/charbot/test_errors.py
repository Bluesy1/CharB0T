from discord.app_commands import AppCommandError

from charbot import errors


def test_wrong_channel_error():
    """Test wrong channel error."""
    error = errors.WrongChannelError(123456789)
    assert str(error) == "This command can only be run in the channel <#123456789> ."
    assert isinstance(error, AppCommandError)


def test_no_pool_found_default_message():
    """Test no pool error."""
    error = errors.NoPoolFound("test")
    assert error.message == "test pool not found. Please choose one from the autocomplete."
    assert isinstance(error, AppCommandError)


def test_missing_single_program_role():
    """Test missing program role error."""
    error = errors.MissingProgramRole(["role1"])
    assert (
        str(error) == "You are missing at least one of the required roles: 'role1'"
        " - you must be at least level 1 to use this command/button."
    )
    assert isinstance(error, AppCommandError)


def test_missing_multiple_program_roles():
    """Test missing program role error."""
    error = errors.MissingProgramRole(["role1", "role2"])
    assert (
        str(error) == "You are missing at least one of the required roles: 'role1' or 'role2'"
        " - you must be at least level 1 to use this command/button."
    )
    assert isinstance(error, AppCommandError)
