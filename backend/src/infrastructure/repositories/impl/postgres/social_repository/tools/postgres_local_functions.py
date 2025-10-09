from sqlalchemy import text
from sqlmodel import Session
from typing import Optional


def create_stored_functions(session: Session) -> None:
    try:
        create_subscribers_count_func = """
        CREATE OR REPLACE FUNCTION get_subscribers_count(userid UUID)
        RETURNS INTEGER AS $$
        BEGIN
            RETURN (
                SELECT COUNT(*)
                FROM subscribers
                WHERE subscribed_id = userid
            );
        END;
        $$ LANGUAGE plpgsql;
                """

        # Создание функции для подсчёта подписок
        create_subscriptions_count_func = """
        CREATE OR REPLACE FUNCTION get_subscriptions_count(userid UUID)
        RETURNS INTEGER AS $$
        BEGIN
            RETURN (
                SELECT COUNT(*)
                FROM subscribers
                WHERE subscriber_id = userid
            );
        END;
        $$ LANGUAGE plpgsql;
        """

        session.execute(text(create_subscribers_count_func))
        session.execute(text(create_subscriptions_count_func))
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"Ошибка при создании функции: {e}")


def get_subscribers_count(userid: str, session: Session) -> Optional[int]:
    query = text("SELECT get_subscribers_count(:userid) AS count")
    result = session.execute(query.bindparams(userid=userid)).first()
    return result[0] if result else None


def get_subscribes_count(userid: str, session: Session) -> Optional[int]:
    query = text("SELECT get_subscriptions_count(:userid) AS count")
    result = session.execute(query.bindparams(userid=userid)).first()
    return result[0] if result else None

