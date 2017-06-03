# -*- coding: utf-8 -*-
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tourism.settings.dev')

import django
django.setup()

from django.core.exceptions import ObjectDoesNotExist
from apps.posts.models import Category, Article


def add_category(title, description="", thumb=None,
                 short_name=None, slug=None, short_d=None):
    """Add category in django

    Arguments:
      title -- Name's category

    Keyword Arguments:
      description {str} -- Full description category (default: {""})
      thumb -- Image for category (default: {None})
      short_name {str} -- Short name (default: {None})
      slug {str} -- slug of category (default: {None})
      short_d {str} -- Short description for category (default: {None})

    Returns:
      Object's category
    """
    try:
        category = Category.objects.get(name=title)
    except ObjectDoesNotExist:
        category = Category.objects.get_or_create(name=title,
                                                  description=description,
                                                  thumb=thumb,
                                                  short_name=short_name,
                                                  slug=slug,
                                                  short_description=short_d)[0]
    return category


def add_article(title, short_content, content, date, slug=None):
    """Add article in django

    Arguments:
      title {str} -- name's category
      short_content {str} -- short article
      content {str} -- full article
      date {date} -- Date of article

    Keyword Arguments:
      slug {str} -- slug of category (default: {None})

    Returns:
      Object's article
    """
    article = Article.objects.get_or_create(name=title,
                                            short_post=short_content,
                                            full_post=content,
                                            date=date,
                                            slug=slug)[0]
    return article
