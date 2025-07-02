from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker

# Инициализация базы
db_engine = create_engine("sqlite:///library.db")
Base = declarative_base()


class BookEntry(Base):
    __tablename__ = "library_books"

    book_id = Column(Integer, primary_key=True)
    book_title = Column(String, nullable=False)
    book_author = Column(String, nullable=False)
    publication_year = Column(Integer)

    def __repr__(self):
        return f"<BookEntry(book_id={self.book_id}, book_title='{self.book_title}', book_author='{self.book_author}', publication_year={self.publication_year})>"


# Создание таблицы
Base.metadata.create_all(bind=db_engine)
print("База данных подготовлена, таблица создана.")


# Создание сессии
SessionLocal = sessionmaker(bind=db_engine)
db_session = SessionLocal()


def insert_book(title, author, year=None):
    book_record = BookEntry(book_title=title, book_author=author, publication_year=year)
    db_session.add(book_record)
    db_session.commit()
    print(f"Добавлена книга: '{title}' от автора '{author}'.")


def list_books():
    records = db_session.query(BookEntry).all()
    if records:
        print("Каталог книг:")
        for entry in records:
            print(f"[ID: {entry.book_id}] {entry.book_title} | {entry.book_author} | {entry.publication_year}")
    else:
        print("База данных пуста.")


def search_book(title):
    result = db_session.query(BookEntry).filter_by(book_title=title).first()
    if result:
        print(f"Найдено: ID={result.book_id}, Название='{result.book_title}', Автор='{result.book_author}', Год={result.publication_year}")
    else:
        print(f"Книга с названием '{title}' не найдена.")


def modify_book_year(title, updated_year):
    result = db_session.query(BookEntry).filter_by(book_title=title).first()
    if result:
        result.publication_year = updated_year
        db_session.commit()
        print(f"Год книги '{title}' обновлен на {updated_year}.")
    else:
        print(f"Не удалось найти книгу с названием '{title}'.")


def remove_book(book_id):
    result = db_session.query(BookEntry).filter_by(book_id=book_id).first()
    if result:
        db_session.delete(result)
        db_session.commit()
        print(f"Книга с ID {book_id} успешно удалена.")
    else:
        print(f"Книга с ID {book_id} не найдена.")


# Пример использования
insert_book("Три товарища", "Эрих Мария Ремарк", 1936)
list_books()
search_book("Три товарища")
modify_book_year("Три товарища", 1945)
remove_book(1)
list_books()

db_session.close()
