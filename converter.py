#!/usr/bin/env python3
import os
import pymysql
import re
from django.conf import settings
from django.utils.timezone import utc
from django.utils.html import strip_tags
from django.core.files import File
from converter.save_django import add_category, add_article
from converter.config.config import ConfigReader


MEDIA_ROOT = getattr(settings, 'MEDIA_ROOT') + '/images/'


class MySQL:
    def __init__(self, host, user, password, dbname, charset='utf8mb4'):
        self.resource = pymysql.connect(host=host,
                                        user=user,
                                        password=password,
                                        db=dbname,
                                        charset=charset,
                                        cursorclass=pymysql.cursors.DictCursor)

    def __del__(self):
        self.resource.close()

    def get_rows(self, sql, parameters=()):
        """Get all rows"""
        with self.resource.cursor() as cursor:
            cursor.execute(sql, parameters)
            return cursor.fetchall()

    def get_row(self, sql, parameters=()):
        """Get row in sepatate as generator"""
        with self.resource.cursor() as cursor:
            cursor.execute(sql, parameters)
            for row in cursor:
                yield row


def replace_path_image(content):
    return content.replace(config['address_to_images_wp'],
                           config['address_to_images'])


def search_first_image(content):
    regex = re.compile(r"<img\s[^>]*?src\s*=\s*['\"]([^'\"]*?)['\"][^>]*?>",
                       re.IGNORECASE | re.UNICODE)
    r = regex.search(content)
    if r is not None:
        for group in r.groups():
            if config['old_domen'] in group:
                return group.replace(config['address_to_images_wp'],
                                     MEDIA_ROOT)


def generate_short_text(content, num_sentences=2):
    text = strip_tags(content)
    sentences = text.split('.')
    if len(sentences) >= num_sentences:
        return ' '.join(sentences[:num_sentences]).strip()
    else:
        return text


# Get settings for db
config_obj = ConfigReader()
config = config_obj.config_read("converter/config/my.ini")

# Set connection with MySql
db = MySQL(config['mysql_host'],
           config['mysql_user'],
           config['mysql_password'],
           config['mysql_dbname'])

# Get all posts which publish
sql = "SELECT * FROM `wp_posts` WHERE `post_status`=%s AND `post_type`=%s"
rows = db.get_row(sql, ('publish', 'post'))
for row in rows:
    # Search first image in post and replace path
    image = search_first_image(row['post_content'])
    row['post_content'] = replace_path_image(row['post_content'])

    # Search short post in post by tag <!--more-->
    if "<!--more-->" in row['post_content']:
        content = row['post_content'].split("<!--more-->")
        short_content = content[0]
        row['post_content'] = " ".join(content[:2])
    else:
        short_content = generate_short_text(row['post_content'], 3)

    # Get many-to-many relationship post with categories
    sql = "SELECT * FROM `wp_term_relationships` WHERE `object_id`=%s"
    term_relations = db.get_rows(sql, (row['ID']))
    categories = []
    for term_relation in term_relations:
        sql = "SELECT * FROM `wp_terms` WHERE `term_id`=%s"
        term = db.get_rows(sql, (term_relation['term_taxonomy_id']))[0]

        # Get description for category
        sql = "SELECT description FROM `wp_term_taxonomy` WHERE `term_id`=%s"
        cat_description = db.get_rows(sql, (term['term_id']))[0]['description']
        if cat_description:
            cat_description = replace_path_image(cat_description)
            short_descr = generate_short_text(cat_description)
        else:
            cat_description = None
            short_descr = None

        # Create category and it add to list
        print('Creating category is %s' % term['name'])
        categories.append(add_category(term['name'],
                                       description=cat_description,
                                       thumb=None,
                                       short_name=None,
                                       slug=term['slug'],
                                       short_d=short_descr))

    # Create article
    print('Creating article is %s' % row['post_title'])
    a = add_article(row['post_title'],
                    short_content,
                    row['post_content'],
                    row['post_date'].replace(tzinfo=utc),
                    slug=row['post_name'])
    # Add reduce image to article
    if image:
        a.thumb.save(os.path.basename(image), File(open(image, 'rb')))
    a.slug_cat_unique = categories[0].slug
    a.save()

    # Relate categories into article
    for cat in categories:
        a.category.add(cat)
