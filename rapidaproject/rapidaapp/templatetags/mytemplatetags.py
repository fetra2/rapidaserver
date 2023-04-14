from django import template

register = template.Library()
@register.filter
def underscore_to_blank(value):
    return value.replace("_"," ")

#ftr constants
DICOS ={'A':'Dépot(A)', 'B':'En route vers prochain bureau(B)', 'C':'Entrée(C)', 'D':'En route vers prochain bureau(D)', 'E':'Arrivée au bureau de destination(E)', 'LIVRE(Avecsucces)':'LIVRE(Avecsucces)'}
def statut_meaning(x):
    x = x.replace(" ","")
    try:
        meaning = DICOS[x]
    except KeyError:
        meaning = x
    return meaning
register.filter('statut_meaning', statut_meaning)
