class UseCaseError(Exception):
    pass


class UserAlreadyExistsError(UseCaseError):
    pass
