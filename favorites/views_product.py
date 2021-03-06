from django.shortcuts import render
from django.http import HttpResponseRedirect
from urllib.parse import urlparse
from django.urls import resolve
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from .models import Product, Favorite, Board
from .forms import BoardCreateForm
from .utils import result_api, translate


def search(request):
    """
    search for a product in the database :
    if input is empty return index
    else get products sorted alphabetically
    """
    query = request.POST.get('research')
    if not query:
        return render(request, 'index.html')
    else:
        products = Product.objects.filter(generic__icontains=query).order_by('generic')
        context = {
            'query': query,
            'products': products,
        }

        if not products.exists():
            message = f"Aucun résultat pour la recherche {query}"
            context = {'message': message}
    return render(request, 'favorites/search.html', context)


def results(request, product_id, query):
    """
    This method is used to find a better substitute
    :param request:
    :param product_id: get product ID chosen by the user in the previous view(search)
    :param query: get the list of products from the previous view
    :return: page results, products __contains the same category (product ID) with a nutri-score <=
    """
    product_selected = Product.objects.get(pk=product_id)
    category = product_selected.category
    listing = Product.objects.filter(
        Q(generic__icontains=query),
        Q(category__contains=category),).order_by('grade').exclude(pk=product_id)
    # built-in function ord() return an integer representing the Unicode code point of that character
    list_substitute = [product for product in listing if ord(product.grade) <= ord(product_selected.grade)]
    context = {
        'product_selected': product_selected, 'list_substitute': list_substitute
    }
    return render(request, 'favorites/results.html', context)


@login_required
def create_board(request, product_id):
    """
    :param request:
    :param product_id: get product ID chosen by the user in the previous view(results)
    :return:
    """
    product_selected = Product.objects.get(pk=product_id)
    favorite_saved = Favorite.objects.filter(user_id=request.user.id, product_id=product_selected) \
        .values('board__name')
    boards = Favorite.objects.filter(user_id=request.user.id).values('board__name', 'board_id', 'product__image') \
        .distinct('board__name')
    next_url = request.GET.get("next")
    if favorite_saved:
        return HttpResponseRedirect(next_url)
    elif request.method == 'POST':
        form = BoardCreateForm(request.POST)
        if form.is_valid():
            board, created = Board.objects.get_or_create(name=form.cleaned_data.get('name'))
            Favorite.objects.update_or_create(user_id=request.user.id, board_id=board.id, product_id=product_selected.id)
            messages.success(request, 'Ce produit fait maintenant parti de vos favoris !')
            return HttpResponseRedirect(next_url)
    else:
        form = BoardCreateForm()
    return render(request, 'favorites/save_product.html', locals())


@login_required
def save_product(request, product_id, board_id):
    """
    :param request:
    :param product_id: product_selected
    :param board_id: board_selected
    :return:
    """
    product_selected = product_id
    board_selected = board_id
    Favorite.objects.update_or_create(
        user_id=request.user.id, product_id=product_selected, board_id=board_selected)
    messages.success(request, 'Ce produit fait maintenant parti de vos favoris !')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'), locals())


def detail_product(request, product_id):
    """
    This method retrieves the product information from the database
    and retrieves the rest of data from the open food facts API
    :param request:
    :param product_id: get product with ID
    :return: detail.html, product information
    """
    product_selected = Product.objects.get(pk=product_id)
    # get static file
    grade = 'favorites/img/nutrient/grade-' + product_selected.grade + '.svg'
    code = product_selected.code
    url = f"https://fr.openfoodfacts.org/produit/{code}"
    # use function result_api() from utils.py return data from API
    detail = result_api(code)
    nutrient_levels = detail['nutrient_levels']
    # get static files
    dot_fat = 'favorites/img/nutrient/dot-' + nutrient_levels['fat'] + '.svg'
    dot_sat = 'favorites/img/nutrient/dot-' + nutrient_levels['saturated-fat'] + '.svg'
    dot_sugar = 'favorites/img/nutrient/dot-' + nutrient_levels['sugars'] + '.svg'
    dot_salt = 'favorites/img/nutrient/dot-' + nutrient_levels['salt'] + '.svg'
    # function translate()(utils.py)
    tr_fat = translate(nutrient_levels['fat'])
    tr_sat = translate(nutrient_levels['saturated-fat'])
    tr_sugar = translate(nutrient_levels['sugars'])
    tr_salt = translate(nutrient_levels['salt'])
    context = {'grade': grade, 'url': url, 'product_selected': product_selected,
               'dot_fat': dot_fat, 'dot_sat': dot_sat, 'dot_sugar': dot_sugar,
               'dot_salt': dot_salt, 'fat': detail['nutriments']['fat_100g'],
               'sat': detail['nutriments']['saturated-fat'], 'sugars': detail['nutriments']['sugars_100g'],
               'salt': detail['nutriments']['salt_100g'], 'tr_fat': tr_fat, 'tr_sat': tr_sat, 'tr_sugar': tr_sugar,
               'tr_salt': tr_salt}
    return render(request, 'favorites/detail.html', context)


@login_required
def board_page(request):
    """
    GET user ID
    :param request:
    :return: the user's boards
    """
    list_board = Favorite.objects.filter(user_id=request.user.id).values('board__name', 'product__image', 'board_id')\
        .distinct('board__name')
    return render(request, 'favorites/boards_page.html', locals())


@login_required
def favorites_page(request, board_id):
    """
    GET user ID
    :param request:
    :param board_id:
    :return: the user's favorites list
    """
    board_selected = Board.objects.filter(pk=board_id).values('name')
    list_favorite = Favorite.objects.filter(user_id=request.user.id).order_by('-id')
    return render(request, 'favorites/favorites_page.html', locals())
