from django.urls import path
from api import views

urlpatterns = [
    path('spell-check/', views.spell_checker, name="spell-checker"),
    path('grammar-check/', views.check_grammar, name="grammar-checker"),
    path('check-both/', views.check_spell_grammar, name="check-both"),
]



'''
{
"text":"kuffaa dhimma kaleessa raawwate"
}

{
"text":"Indaaluu Baayyisaa mana Magaalaa warrajirruu ganda keessa qaban Lakk Obbo"
}
'''

