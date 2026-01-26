class UseCaseError(Exception):
    pass


class UserAlreadyExistsError(UseCaseError):
    pass


class AuthenticationError(UseCaseError):
    pass
