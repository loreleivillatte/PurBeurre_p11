from django import forms
from favorites.models import Board, Favorite


class BoardCreateForm(forms.Form):
    name = forms.CharField(label='Nouveau tableau')

    class Meta:
        model = Board
        fields = ['name']

    def clean_fields(self):
        board = self.cleaned_data.get('board').lower()
        return board

    def clean(self):
        name = self.cleaned_data.get('name')
        obj = Favorite.objects.filter(board__name__icontains=name)
        if obj:
            raise forms.ValidationError("Impossible d'enregistrer le tableau. Ce nom de tableau existe déjà.")
        return self.cleaned_data



