from smartutils.call import call_hook, exit_on_fail


async def test_call_hook():
    await call_hook(None)


def test_exit_on_fail_calls_os_exit(mocker):
    mock_exit = mocker.patch("os._exit")
    exit_on_fail()
    mock_exit.assert_called_once_with(1)
