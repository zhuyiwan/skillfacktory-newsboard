from django import template

import os
import re
register = template.Library()

def load_swear_words(filepath):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    filepath = os.path.join(dir_path, "swear_words.txt")

    with open(filepath, "r", encoding="utf-8") as file:
        return [line.strip() for line in file if line.strip()]

def replace_with_stars(word):
    return '*' * len(word.group())

@register.filter()
def no_swear_words(basic_text):
    swear_words = load_swear_words('swear_words.txt')
    for word in swear_words:
        comparison = re.escape(word)
        basic_text = re.sub(comparison, replace_with_stars, basic_text, flags=re.IGNORECASE)
    return basic_text
