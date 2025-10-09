from src.web.models.users import AccessModel, UserSearchingFilters


class SocialServiceException(Exception):
    pass


class UserDoesntHavePermissionException(SocialServiceException):
    code = "NOT ENOUGH RIGHTS"

    def __init__(self, access_model: AccessModel, filters: UserSearchingFilters, action: str):
        super().__init__(
            f"User {access_model.current_user} can't {action} {filters} belonging user {filters.target_user}.")


class UserNotFoundException(SocialServiceException):
    code = "NOT FOUND"

    def __init__(self, access_model: AccessModel, filters: UserSearchingFilters):
        super().__init__(
            f"User {access_model.current_user} can't find {filters.target_user}")


class UserNotExistsException(SocialServiceException):
    pass
