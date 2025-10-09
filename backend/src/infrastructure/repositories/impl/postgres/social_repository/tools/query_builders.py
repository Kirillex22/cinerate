from sqlalchemy import select
from sqlalchemy.orm import selectinload
from src.infrastructure.repositories.impl.postgres.social_repository.orm import UserORM, UserItemORM
from src.web.models.users import UserSearchingFilters


class LocalUserSearchQueryBuilder:
    def __init__(self, base_query):
        self.query = base_query

    def apply_all(self, filters: UserSearchingFilters):
        non_null_filters = filters.get_non_null_fields()

        for field, value in non_null_filters.items():
            self.apply_filter(field, value)

        # Подтягиваем данные user_item для корректного маппинга
        self.query = self.query.options(selectinload(UserORM.user_item))
        return self

    def apply_filter(self, field: str, value: any):
        method_name = f"filter_by_{field}"
        method = getattr(self, method_name, None)
        if method:
            self.query = method(value)

    def filter_by_userid(self, value: str):
        return self.query.where(UserORM.id == value)

    def filter_by_username(self, value: str):
        # Подзапрос для поиска item_id по username
        subquery = (
            select(UserItemORM.item_id)
            .where(UserItemORM.username.ilike(f"%{value}%"))
        )
        return self.query.where(UserORM.item_id.in_(subquery))

    def filter_by_root(self, value: bool):
        if not value:
            subquery = (
                select(UserItemORM.item_id)
                .where(UserItemORM.status == 'PUBLIC')
            )
            return self.query.where(UserORM.item_id.in_(subquery))
        return self.query

    def filter_by_login(self, value: str):
        return self.query.where(UserORM.login == value)

    def build(self):
        return self.query
