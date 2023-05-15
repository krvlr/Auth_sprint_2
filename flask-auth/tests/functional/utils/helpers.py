from http.cookies import SimpleCookie


def get_cookies(simple_cookies: SimpleCookie, filters: list = []) -> dict:
    return {key: value.value for key, value in simple_cookies.items() if key in filters}
