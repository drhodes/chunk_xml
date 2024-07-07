from lxml import etree
import random

def random_tag():
    return ''.join(random.choice("abcdefghijklmnoprstuvwxyz") for x in range(5))

def random_empty_el():
    return etree.Element(random_tag())

def random_el(depth):        
    el = random_empty_el()
    rel = random_el_helper(el, depth)
    rel.tail = None
    return rel

def random_el_helper(el, depth):
    if depth == 0:
        return el
    num_children = random.randint(0, 5)
    for _ in range(num_children):
        child = random_el(depth-1)
        if random.random() > .5: el.text = random_tag()
        if random.random() > .5: el.tail = random_tag()
        el.append(child)
    return el

def showel(el):
    return etree.tostring(el, pretty_print=True).decode("utf-8")
