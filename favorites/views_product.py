from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.exceptions import ObjectDoesNotExist
from .models import Product, Favorite
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

    context = {'product_selected': product_selected, 'list_substitute': list_substitute}
    return render(request, 'favorites/results.html', context)


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
    # use function translate()(utils.py)
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
def save_substitute(request, product_id):
    """
    This method is used to allow the user to register a product in his favorites list
    make sure the user has not registered this product yet
    :param request:
    :param product_id: get ID of product
    :return: HttpResponseRedirect(results.html)
    """
    product_selected = product_id
    try:
        Favorite.objects.get(user_id=request.user.id, product_id=product_selected)
        messages.error(request, 'Ce produit fait déjà parti de vos favoris')
    except ObjectDoesNotExist:
        Favorite.objects.create(user_id=request.user.id, product_id=product_selected)
        messages.success(request, 'Ce produit fait maintenant parti de vos favoris')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def favorites_page(request):
    """
    GET user ID
    :param request:
    :return: the user's favorites list
    """
    list_favorite = Favorite.objects.filter(user_id=request.user.id).order_by('-id')
    return render(request, 'favorites/favorites_page.html', locals())
