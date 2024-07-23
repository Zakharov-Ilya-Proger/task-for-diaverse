from datetime import datetime

from sqlalchemy import text
from config import connection
from models.models import Login
from asgiref.sync import async_to_sync
from fastapi import HTTPException


some_user = {"email": "pelevin@gmail.com", "password": "put_v_elevsin"}


async def get_login(person: Login):
    with connection.connect() as conn:
        result = conn.execute(
            text('select * from public.user where email = :email and password = :password'),
            {"email": person.email, "password": person.password}
        ).fetchone()
        conn.close()
        if result is None:
            raise HTTPException(status_code=404, detail="No such user")
        return {"email": result[1], "id": result[0], "password": result[2]}


async def get_all_books():
    with connection.connect() as conn:
        result = conn.execute(
            text('''select  a.name, a.middle, a.second_name, b.name, b.cost, string_agg(g.name, ', '), b.id
                    from book_genre bg
                    join public.book b on b.id = bg.book
                    join public.genre g on g.id = bg.genre
                    join public.author a on a.id = b.author
                    group by a.name, a.middle, a.second_name, 
                        b.name, b.cost, b.id''')
        ).fetchall()
        conn.close()
        if not result:
            raise HTTPException(status_code=404, detail="No Books in Library")
        response = [{"id": row[6],
                     "author name": f'{row[0]} {row[1]} {row[2]}',
                     "name": row[3],
                     "cost": row[4],
                     "genres": row[5]}
                    for row in result]
        return response


async def is_booked(user_id: int, book_id: int):
    with connection.connect() as conn:
        result = conn.execute(text('''select * from user_book 
                                 where user_book.user = :user 
                                 and user_book.book = :book'''),
                              {"user": user_id, "book": book_id}).fetchall()
        conn.close()
        if not result:
            return False
        return True


async def book_the_book(user_id: int, book_id: int, date: datetime):
    with connection.connect() as conn:
        conn.execute(text('''insert into user_book ("user", book, rent_date)
                             values (:user, :book, :date)'''),
                     {"user": user_id, "book": book_id, "date": date})
        conn.commit()
        conn.execute(text('''update book set status = true where id = :book'''), {"book": book_id})
        conn.commit()
        conn.close()
        return True


async def my_books(user_id: int):
    with connection.connect() as conn:
        result = conn.execute(text('''select  a.name, a.middle, a.second_name, b.name, b.cost, b.id, ub.rent_date
                    from user_book ub
                    join public.book b on b.id = ub.book
                    join public.author a on a.id = b.author
                    join public."user" u on u.id = ub."user"
                    where u.id = :user'''), {"user": user_id}).fetchall()
        conn.close()
        return [{"book_id": row[5],
                 "author": f"{row[0]} {row[1]} {row[2]}",
                 "book_name": row[3],
                 "cost": row[4],
                 "date": row[6]}
                for row in result]


@async_to_sync
async def main():
    books = await my_books(1)
    return books


if __name__ == '__main__':
    print(main())
