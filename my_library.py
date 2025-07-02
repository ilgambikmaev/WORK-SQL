from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import sessionmaker, declarative_base, relationship

db_engine = create_engine("sqlite:///my_library.db")

Base = declarative_base()


class Volume(Base):
    __tablename__ = 'volumes'
    vol_id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    main_author = Column(String, nullable=False)
    release_year = Column(Integer, nullable=True)
    publishing = relationship("PublishingHouse", back_populates="volume", uselist=False)
    critiques = relationship("Critique", back_populates="volume")
    coauthors = relationship("Writer", secondary="volume_writer", back_populates="volumes")

    def __repr__(self):
        return f"<Volume(vol_id={self.vol_id}, title='{self.title}', main_author='{self.main_author}', release_year={self.release_year})>"


class PublishingHouse(Base):
    __tablename__ = 'publishing_houses'
    pub_id = Column(Integer, primary_key=True)
    pub_name = Column(String, nullable=False)
    vol_id = Column(Integer, ForeignKey('volumes.vol_id'), unique=True)
    volume = relationship("Volume", back_populates="publishing")

    def __repr__(self):
        return f"<PublishingHouse(pub_id={self.pub_id}, pub_name='{self.pub_name}', vol_id={self.vol_id})>"


class Critique(Base):
    __tablename__ = 'critiques'
    crit_id = Column(Integer, primary_key=True)
    content = Column(String, nullable=False)
    vol_id = Column(Integer, ForeignKey('volumes.vol_id'))
    volume = relationship("Volume", back_populates="critiques")

    def __repr__(self):
        return f"<Critique(crit_id={self.crit_id}, content='{self.content}', vol_id={self.vol_id})>"


volume_writer = Table(
    'volume_writer', Base.metadata,
    Column('vol_id', Integer, ForeignKey('volumes.vol_id')),
    Column('writer_id', Integer, ForeignKey('writers.writer_id'))
)


class Writer(Base):
    __tablename__ = 'writers'
    writer_id = Column(Integer, primary_key=True)
    full_name = Column(String, nullable=False)
    volumes = relationship("Volume", secondary="volume_writer", back_populates="coauthors")

    def __repr__(self):
        return f"<Writer(writer_id={self.writer_id}, full_name='{self.full_name}')>"


Base.metadata.create_all(bind=db_engine)
print("База данных и таблицы успешно созданы.")


SessionLocal = sessionmaker(bind=db_engine)
db_session = SessionLocal()


def create_volume_with_publisher(title, main_author, publisher, year=None):
    vol = Volume(title=title, main_author=main_author, release_year=year)
    pub = PublishingHouse(pub_name=publisher, volume=vol)
    db_session.add(vol)
    db_session.add(pub)
    db_session.commit()
    print(f"Том '{title}' опубликован издательством '{publisher}'.")


def append_critique(vol_id, text):
    vol = db_session.query(Volume).filter_by(vol_id=vol_id).first()
    if vol:
        crit = Critique(content=text, volume=vol)
        db_session.add(crit)
        db_session.commit()
        print(f"К рецензия к '{vol.title}' успешно добавлена.")
    else:
        print(f"Том с ID {vol_id} не найден.")


def attach_writer_to_volume(vol_id, writer_name):
    vol = db_session.query(Volume).filter_by(vol_id=vol_id).first()
    if vol:
        writer = Writer(full_name=writer_name)
        vol.coauthors.append(writer)
        db_session.add(writer)
        db_session.commit()
        print(f"Соавтор '{writer_name}' добавлен к тому '{vol.title}'.")
    else:
        print(f"Том с ID {vol_id} не найден.")


def display_volume_with_critiques(vol_id):
    vol = db_session.query(Volume).filter_by(vol_id=vol_id).first()
    if vol:
        print(f"Том: {vol.title}, Автор: {vol.main_author}, Год: {vol.release_year}")
        if vol.critiques:
            print("Рецензии:")
            for crit in vol.critiques:
                print(f"  - {crit.content}")
        else:
            print("Рецензий нет.")
    else:
        print(f"Том с ID {vol_id} не найден.")


def display_volume_with_writers(vol_id):
    vol = db_session.query(Volume).filter_by(vol_id=vol_id).first()
    if vol:
        print(f"Том: {vol.title}, Автор: {vol.main_author}, Год: {vol.release_year}")
        if vol.coauthors:
            print("Соавторы:")
            for writer in vol.coauthors:
                print(f"  - {writer.full_name}")
        else:
            print("Соавторов нет.")
    else:
        print(f"Том с ID {vol_id} не найден.")


# Демонстрация работы
create_volume_with_publisher("Властелин колец", "Дж. Р. Р. Толкин", "Allen & Unwin", 1954)
append_critique(1, "Эпично и захватывающе!")
attach_writer_to_volume(1, "Джон Рональд Руэл Толкин")
display_volume_with_critiques(1)
display_volume_with_writers(1)
db_session.close()
