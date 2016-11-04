from errors import BaseException


def handle_dispatch_exceptions(func):
    def inner(connection, request, *args, **kwargs):
        try:
            return func(connection, request, *args, **kwargs)
        except BaseException as e:
            resp = request.data
            resp.update({
                "error": e.ERROR,
                "message": e.DEFAULT_MESSAGE if not e.message else e.message,
            })
            connection.reply(resp)
        except Exception as e:
            resp = request.data
            resp.update({
                "error": -1,
                "message": str(e),
            })
            connection.reply(resp)
    return inner
