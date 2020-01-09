import requests
from bs4 import BeautifulSoup as bs

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import (
    Base,
    BlogPost,
    Writer,
    Tag,
)


class BlogDb:
    def __init__(self, url, base=Base):
        engine = create_engine(url)
        base.metadata.create_all(engine)
        session_db = sessionmaker(bind=engine)
        self.__session = session_db()

    @property
    def session(self):
        return self.__session


if __name__=='__main__':
    db_url = 'sqlite:///blogpost.sqlite'
    db = BlogDb(db_url)
    print(1)

# Процедура для получения автора по имени, если значение не найдено, то создает новый.
def GetWriter(name,url):
    tags = db.session.query(Writer)
    result = tags.filter(Writer.name.like(u"%%%s%%" % name))
    if result.count() == 0:
        return Writer(name, url)
    else:
        return tags.filter(Writer.name.like(u"%%%s%%" % name)).first()

# Процедура для получения тега по имени, если значение не найдено, то создает новый.
def GetTag(name):
    tags = db.session.query(Tag)
    result = tags.filter(Tag.name.like(u"%%%s%%" % name))
    if result.count() == 0:
        return Tag(name)
    else:
        return tags.filter(Tag.name.like(u"%%%s%%" % name)).first()

# Процедура с помошью BS4 "разбиват" код-HTML на данные и заносит их в таблицы
def post_details(i):
    domian = 'https://geekbrains.ru'

    post = i.find('a', attrs={'class': 'post-item__title h3 search_text'})
    title = post.text

    post_ref = domian + post.attrs['href']

    r = requests.get(post_ref)
    text = r.text
    soap = bs(text, 'lxml')
    date_post = soap.find('div', attrs={'class': 'blogpost-date-views'})
    date_post = soap.find('time', attrs={'class': 'text-md text-muted m-r-md'})
    date_post = date_post.attrs['datetime']
    ref_post = domian + post.attrs['href']

    tag_post = soap.find('i', attrs={'class': 'i i-tag m-r-xs text-muted text-xs'})
    tag_post = tag_post.attrs['keywords']

    tagSp = list()
    for t in tag_post.split(','):
        tagM = GetTag(t)
        tagSp.append(tagM)
        db.session.add(tagM)

    tag_post = soap.find('div', attrs={'class': 'col-md-5 col-sm-12 col-lg-8 col-xs-12 padder-v'})

    name_author = list(list(tag_post.children)[0].children)[2].text

    ref_author = domian + tag_post.find('a').attrs['href']

    WriterM = GetWriter(name_author, ref_author)

    db.session.add(BlogPost(title, date_post, post_ref, WriterM, tagSp))

db = BlogDb('sqlite:///blogpost.sqlite')
domian = 'https://geekbrains.ru'
main_ref = 'https://geekbrains.ru/posts'
while True:
    print('обработка ссылки: ', main_ref)
    r = requests.get(main_ref)
    text = r.text
    soap = bs(text, 'lxml')

    # Обход страницы, считывания блогов
    for i in soap.find('div', attrs={'class': 'post-items-wrapper'}):
        post_details(i)

    # Получение следующей страницы
    r = requests.get(main_ref)
    text = r.text
    soap = bs(text, 'lxml')

    ul = soap.find('ul', attrs={'class': 'gb__pagination'})
    al = ul.find_all('li', attrs={'class': 'page'})

    lenS = len(ul)
    try:
        main_ref = list(ul)[lenS - 1].find('a').attrs['href']
    except:
        break

    main_ref = domian + main_ref

db.session.commit()