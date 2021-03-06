from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
import json
from django.contrib.auth import authenticate,login, logout as auth_logout
from .models import *
from django.contrib.auth.models import User
# from amazon.api import AmazonAPI
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.csrf import csrf_exempt
from .models import *
import requests
import bottlenose
from bs4 import BeautifulSoup
import xmltodict
import ast
from social_django.models import *
import urllib
import urllib2
import datetime
from django.db.models import Q
import operator

def populate_db_amazon_user_req(request, gender, main_cloth, cloth):
    print "gender = ", gender
    print "cloth = ", cloth
    try:
        amazon = bottlenose.Amazon('AKIAJOR5NTXK2ERTU6AQ',
                                   'kck/SKuTJif9bl7qeq5AyB4CU8HWsdz14VW4Iaz2',
                                   'can037-20',
                                   MaxQPS=0.9
                                   )
        pages = [1,2,3,4,5]
        for each_page in pages:
            product = amazon.ItemSearch(Keywords="%s's %s" % (gender, cloth),
                                        SearchIndex="All",
                                        ResponseGroup="Images, SalesRank, OfferFull, ItemAttributes",
                                        Availability="Available",
                                        paginate=True,
                                        ItemPage=each_page)
            soup = BeautifulSoup(product, "xml")

            newDictionary = xmltodict.parse(str(soup))
            try:
                # print "item = ", newDictionary['ItemSearchResponse']['Items']
                for each_item in newDictionary['ItemSearchResponse']['Items']['Item']:
                    try:
                        current_clothing = clothing.objects.get(carrier='amazon',
                                                                carrier_id=each_item['ASIN'])
                    except:
                        #clothing does not exist in db
                        try:
                            if "women" in gender.lower() or "female" in gender.lower() or "girl" in gender.lower():
                                gender_bool = True
                            else:
                                gender_bool = False
                            new_clothing = clothing(name=each_item['ItemAttributes']['Title'],
                                                    carrier="amazon",
                                                    carrier_id=each_item['ASIN'],
                                                    small_url=each_item['SmallImage']['URL'],
                                                    large_url=each_item['LargeImage']['URL'],
                                                    gender=gender_bool,
                                                    price=each_item['OfferSummary']['LowestNewPrice']['FormattedPrice'],
                                                    color=each_item['ItemAttributes']['Color'],
                                                    brand=each_item['ItemAttributes']['Brand'],
                                                    aff_url=generate_amazon_link(each_item['ASIN']),
                                                    cloth_type=main_cloth,
                                                    cloth_sub_type="%s, all" % cloth)
                            new_clothing.save()
                            newbrand = brands.objects.filter(name=each_item['ItemAttributes']['Brand'])
                            if len(newbrand) == 0:
                                newbrand = brands(name=each_item['ItemAttributes']['Brand'])
                                newbrand.save()
                            print "added item ", each_item['ItemAttributes']['Title'],
                        except Exception as e:
                            print "error ", e
                            pass
            except Exception as e:
                print "Error on upper try: ", e
        return HttpResponse("Success")
    except Exception as e:
        print "error ", e
        return HttpResponse("Error")

def populate_db_amazon(request):
    try:
        amazon = bottlenose.Amazon('AKIAJOR5NTXK2ERTU6AQ',
                                   'kck/SKuTJif9bl7qeq5AyB4CU8HWsdz14VW4Iaz2',
                                   'can037-20',
                                   MaxQPS=0.9
                                   )
        # cloth_types = ["Shirt", "Pants", "Shoes", "sweaters", "tanks", "tops", "swim top", "jeans", "joggers", "shorts", "swim shorts",
        #                "skirts", "leggings", "athletic shoes", "boots", "sandals", "professional" "shoes", "belts", "sunglasses", "wallets",
        #                "scarves & wraps", "watches", "jewelry"
        #                ]
        cloth_types = {
            "Shirt": ["Sweaters", "Tanks", "Tops", "Swim Top", "Shirt"],
           # "Pants": ["Jeans", "Joggers", "Shorts", "Swim Shorts", "Skirts", "Leggings", "Pants"],
           # "Shoes": ["Athletic Shoes", "Boots", "Sandals", "Professional Shoes"],
           # "Accessories": ["Belts", "Sunglasses", "Wallets", "Scarves & Wraps", "Watches", "Jewelry"]
        }
        gender = [
            # "Women",
            "Men"
        ]
        pages = [1,2,3,4,5]
        for each_gender in gender:
            for each_cloth_type in cloth_types:
                for each_cloth_subtype in cloth_types[each_cloth_type]:
                    for each_page in pages:
                        product = amazon.ItemSearch(Keywords="%s's %s" % (each_gender, each_cloth_subtype),
                                                    SearchIndex="All",
                                                    ResponseGroup="Images, SalesRank, OfferFull, ItemAttributes",
                                                    Availability="Available",
                                                    paginate=True,
                                                    ItemPage=each_page)
                        soup = BeautifulSoup(product, "xml")

                        newDictionary = xmltodict.parse(str(soup))
                        try:
                            # print "item = ", newDictionary['ItemSearchResponse']['Items']
                            for each_item in newDictionary['ItemSearchResponse']['Items']['Item']:
                                try:
                                    current_clothing = clothing.objects.get(carrier='amazon',
                                                                            carrier_id=each_item['ASIN'])
                                except:
                                    #clothing does not exist in db
                                    try:
                                        if each_gender == "Women":
                                            gender_bool = True
                                        else:
                                            gender_bool = False
                                        new_clothing = clothing(name=each_item['ItemAttributes']['Title'],
                                                                carrier="amazon",
                                                                carrier_id=each_item['ASIN'],
                                                                small_url=each_item['SmallImage']['URL'],
                                                                large_url=each_item['LargeImage']['URL'],
                                                                gender=gender_bool,
                                                                price=each_item['OfferSummary']['LowestNewPrice']['FormattedPrice'],
                                                                color=each_item['ItemAttributes']['Color'],
                                                                brand=each_item['ItemAttributes']['Brand'],
                                                                aff_url=generate_amazon_link(each_item['ASIN']),
                                                                cloth_type=each_cloth_type,
                                                                cloth_sub_type="%s, all" % each_cloth_subtype)
                                        new_clothing.save()
                                        newbrand = brands.objects.filter(name=each_item['ItemAttributes']['Brand'])
                                        if len(newbrand) == 0:
                                            newbrand = brands(name=each_item['ItemAttributes']['Brand'])
                                            newbrand.save()
                                        print "added item"
                                    except Exception as e:
                                        print "error ", e
                                        pass
                        except Exception as e:
                            print "Error on upper try: ", e
        return HttpResponse("Success")
    # try:
    #     all_clothes = clothing.objects.filter()
    #     print "all clothes"
    #     print "len - ", len(all_clothes)
    #     for each_clothing in all_clothes:
    #         if each_clothing.aff_url == "https://www.amazon.com/dp/"+each_clothing.carrier_id+"/?tag=can037-20":
    #             each_clothing.aff_url = "https://www.amazon.com/dp/"+each_clothing.carrier_id+"/?tag=fashionly02-20"
    #             each_clothing.save()
    #             print "Changed ", each_clothing
    #     return HttpResponse("Success")
    except Exception as e:
        print "error ", e
        return HttpResponse("Error")

def populate_db(request):
    try:
        amazon = bottlenose.Amazon('AKIAJOR5NTXK2ERTU6AQ',
                                    'kck/SKuTJif9bl7qeq5AyB4CU8HWsdz14VW4Iaz2',
                                    'can037-20',
                                   # Parser=lambda text: BeautifulSoup(text, 'xml')
                                    # region="US",
                                   MaxQPS=0.9
                                   )
        # cloth_types = ["Shirt", "Pants", "Shoes"]
        # gender = ["Women", "Men"]
        # for each_gender in gender:
        #         for each_cloth_type in cloth_types:
        product = amazon.ItemSearch(Keywords="Women's Shirt",
                                    SearchIndex="All",
                                    ResponseGroup="Images, SalesRank, OfferFull, ItemAttributes",
                                    Availability="Available",
                                    paginate=True,
                                    ItemPage=2)
        soup = BeautifulSoup(product, "xml")
        print soup

        newDictionary = xmltodict.parse(str(soup))
        for each_item in newDictionary['ItemSearchResponse']['Items']['Item']:
            print each_item
            print "_____"
                        # try:
                        #     current_clothing = clothing.objects.get(carrier='amazon',
                        #                                             carrier_id=each_item['ASIN'])
                        # except:
                        #     #clothing does not exist in db
                        #     try:
                        #         if each_gender == "Women":
                        #             gender_bool = True
                        #         else:
                        #             gender_bool = False
                        #         new_clothing = clothing(name=each_item['ItemAttributes']['Title'],
                        #                                 carrier="amazon",
                        #                                 carrier_id=each_item['ASIN'],
                        #                                 small_url=each_item['SmallImage']['URL'],
                        #                                 large_url=each_item['LargeImage']['URL'],
                        #                                 gender=gender_bool,
                        #                                 price=each_item['OfferSummary']['LowestNewPrice']['FormattedPrice'],
                        #                                 color=each_item['ItemAttributes']['Brand'],
                        #                                 brand=each_item['ItemAttributes']['Color'],
                        #                                 aff_url=generate_amazon_link(each_item['ASIN']),
                        #                                 cloth_type=each_cloth_type)
                        #         new_clothing.save()
                        #         print "added item"
                        #     except Exception as e:
                        #         print "error ", e
                        #         pass
            # print "item = ", each_item['ASIN']
            # print "img = ", each_item['SmallImage']['URL']
            # print "large = ", each_item['LargeImage']['URL']
            # print "offer summary = ", each_item['OfferSummary']['LowestNewPrice']['FormattedPrice']
            # print "url = ", generate_amazon_link(each_item['ASIN'])
            # print "title = ", each_item['ItemAttributes']['Title']
            # # response = amazon.ItemLookup(ItemId=each_item['ASIN'])
            # # print "response = ", response
            # print "________"



        # products = amazon.search_n(1, Keywords="Women's Shirt", SearchIndex="Apparel")
        # for each_product in products:
        #     print dir(each_product)
        #     print each_product.availability
        #     print each_product.availability_type
        #     print each_product.price_and_currency
        #     print each_product.list_price
        #     print each_product.formatted_price
        #     print each_product.get_parent

    #     for each_gender in gender:
    #         for each_cloth_type in cloth_types:
    #             products = amazon.search_n(99, Keywords=each_gender + "'s " + each_cloth_type, SearchIndex="Apparel")
    #             for each_product in products:
    #                 current_id = each_product.asin
    #                 current_carrier = "amazon"
    #                 print "price = ", each_product.price_and_currency
    #                 if each_product.price_and_currency[0] is not None:
    #                     try:
    #                         current_clothing = clothing.objects.get(carrier=current_carrier,
    #                                                                 carrier_id=current_id)
    #                     except:
    #                         #clothing does not exist in db
    #                         if gender == "Women":
    #                             gender_bool = True
    #                         else:
    #                             gender_bool = False
    #                         new_clothing = clothing(name=each_product.title,
    #                                                 carrier="amazon",
    #                                                 carrier_id=each_product.asin,
    #                                                 small_url=each_product.small_image_url,
    #                                                 large_url=each_product.large_image_url,
    #                                                 gender=gender_bool,
    #                                                 price=each_product.price_and_currency[0],
    #                                                 cloth_type=each_cloth_type)
    #                         new_clothing.save()
    #                         print "added item"
        return HttpResponse("Success")
    except Exception as e:
        print "error ", e
        return HttpResponse("Error")

def generate_amazon_link(ASIN):
    return "https://www.amazon.com/dp/%s/?tag=fashionly02-20" % (ASIN)

def logout(request):
    auth_logout(request)
    return HttpResponseRedirect("/")

@csrf_exempt
def headerSignIn(request):
    if request.is_ajax():
        if request.method == "POST":
            data = request.POST.getlist("data[]")
            print "data = ", data

            user = authenticate(username=str(data[0]), password=str(data[1]))
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponse("Success")
            else:
                return HttpResponse("Does not match")

@csrf_exempt
def headerSignUp(request):
    if request.is_ajax():
        if request.method == "POST":
            data = request.POST.getlist("data[]")
            if str(data[0]) == "Admin":
                return HttpResponse("Username Exists")
            try:
                user = User.objects.create_user(username=str(data[0]),
                                                email=str(data[2]),
                                                password=str(data[1]))
                user.backend='django.contrib.auth.backends.ModelBackend'
                user.save()
                gender = data[3]
                if gender == "true":
                    gender = True
                else:
                    gender = False
                #create profile
                profile_obj = profile(user=user,
                                      gender=gender)
                profile_obj.save()

                #check for promo
                promoCode = data[4]
                if promoCode is not "none":
                    try:
                        promo_user = profile.objects.get(user__username=str(data[4]))
                        promo_user.has_recruited.add(profile_obj)
                        promo_user.save()
                    except Exception as e:
                        print "exception on promocode: ", e
            except Exception as e:
                print "e = ", str(e)
                if str(e) == "column username is not unique":
                    return HttpResponse("Username Exists")

            if user is not None:
                if profile_obj is not None:
                    if user.is_active:
                        login(request, user)
                        return HttpResponse("Success")
            else:
                return HttpResponse("Does not match")

def get_featured_outfits(current_profile):
    outfit_objs = outfit.objects.filter()
    outfits = get_outfit_items(outfit_objs, current_profile)
    return outfits

def get_new_outfits(current_profile):
    outfit_objs = outfit.objects.filter().order_by('-id')[:10]
    outfits = get_outfit_items(outfit_objs, current_profile)
    return outfits

def get_popular_outfits(current_profile):
    outfit_objs = outfit.objects.filter().order_by('-likes')[:10]
    outfits = get_outfit_items(outfit_objs, current_profile)
    return outfits

def get_tag_list(outfit):
    tag_arr = []
    for each_tag in outfit.tag_list.all():
        tag_arr.append(each_tag.word)
    return tag_arr

def get_outfit_items(outfits, current_profile):
    outfits_arr = []
    for each_outfit in outfits:
        outfit_items = outfit_item.objects.filter(outfit=each_outfit)
        inner_outfit = []
        for each_outfit_item in outfit_items:
            inner_outfit.append({"pk": each_outfit_item.pk,
                                 "transform": ast.literal_eval(each_outfit_item.transform_matrix,),
                                 "large_url": each_outfit_item.clothing.large_url,
                                 "zIndex": each_outfit_item.zIndex})
        is_following = each_outfit.profile.is_following(current_profile)
        outfits_arr.append({"outfit": inner_outfit,
                        "user": {"username": each_outfit.profile.user.username,
                                 "profile_img": each_outfit.profile.profile_image,
                                 "location": each_outfit.profile.location,
                                 "user_id": each_outfit.profile.pk,
                                 "is_following": is_following,
                                 "is_self": each_outfit.profile == current_profile},
                        "outfit_pk": each_outfit.pk,
                        "canvasHeight": each_outfit.canvas_height,
                        "canvasWidth": each_outfit.canvas_width,
                        "total_likes": each_outfit.likes,
                        "tags": get_tag_list(each_outfit),
                        "liked": each_outfit.does_user_like(current_profile),})
    return outfits_arr

def get_front_page(request):
    # if request.user.is_authenticated():
    if request.method == "POST":
        if request.is_ajax():
            index = request.POST.get("index")
            try:
                current_profile = profile.objects.get(user=request.user)
            except:
                #user is likely not logged in
                current_profile = None
            featured_outfits = get_featured_outfits(current_profile)
            popular_outfits = get_popular_outfits(current_profile)
            new_outfits = get_new_outfits(current_profile)

            print "index = ", index
            json_stuff = json.dumps({"featured": featured_outfits,
                                     "new": new_outfits,
                                     "popular": popular_outfits,})
            return HttpResponse(json_stuff, content_type="application/json")
    return HttpResponse("Error")

def signUpLogIn(request):
    # if request.user.is_authenticated():
        #send them to /home
    template = loader.get_template('discover.html')
    # try:
    print "in login"
    try:
        current_profile = profile.objects.get(user=request.user)
    except Exception as e:
        print "error ", e
        current_profile = None
    brand_list = brands.objects.filter()
    brand_json = {}
    for each_item in brand_list:
        brand_json[each_item.name] = None
    context = {
        "current_profile": current_profile,
        "brands": json.dumps(brand_json)
    }
    # except Exception as e:
    #     print "error ", e
    #     template = loader.get_template('headerLogin.html')
    #     context = {
    #         "asd": "asd"
    #     }
    # else:
    #     template = loader.get_template('headerLogin.html')
    #     context = {
    #         "asd": "asd"
    #     }
    return HttpResponse(template.render(context, request))

def discover_clothing(request):
    # if request.user.is_authenticated():
        #send them to /home
    template = loader.get_template('discover_clothing.html')
    # try:
    try:
        current_profile = profile.objects.get(user=request.user)
    except Exception as e:
        print "error ", e
        #user likely not logged in
        current_profile = None
    brand_list = brands.objects.filter()
    brand_json = {}
    for each_item in brand_list:
        brand_json[each_item.name] = None
    context = {
        "current_profile_self": current_profile,
        "brands": json.dumps(brand_json)
    }
    #     except Exception as e:
    #         print "error ", e
    #         template = loader.get_template('headerLogin.html')
    #         context = {
    #             "asd": "asd"
    #         }
    # else:
    #     template = loader.get_template('headerLogin.html')
    #     context = {
    #         "asd": "asd"
    #     }
    return HttpResponse(template.render(context, request))

def about(request):
    template = loader.get_template('about.html')
    context = {}
    return HttpResponse(template.render(context, request))

def contact(request):
    template = loader.get_template('contact.html')


    context = {}
    return HttpResponse(template.render(context, request))

@csrf_exempt
def user_submit_outfit(request):
    if request.is_ajax():
        if request.method == 'POST':
            items = request.POST.getlist('data[]')
            items = json.loads(items[0])
            print "items = ", items['caption']
            try:
                current_profile = profile.objects.get(user=request.user)
            except Exception as e:
                #user is likely not logged in
                print "Error ", e
                return HttpResponse("Login")
            #create tags
            tag_list = []
            for each_tag in items['tag']:
                try:
                    new_tag = tag.objects.get(word=each_tag)
                except:
                    new_tag = tag(word=each_tag)
                    new_tag.save()
                tag_list.append(new_tag)
            #create outfit
            new_outfit = outfit(profile=current_profile,
                                gender=items['gender'],
                                description=items['caption'],
                                canvas_height=items['canvasHeight'],
                                canvas_width=items['canvasWidth'])
            new_outfit.save()
            for each_tag in tag_list:
                new_outfit.tag_list.add(each_tag)
            new_outfit.save()

            #create outfit items
            for each_item in items['items']:
                current_clothing = clothing.objects.get(carrier_id = each_item['item_id'],
                                                        carrier=each_item['carrier'])
                new_item = outfit_item(clothing=current_clothing,
                                       outfit=new_outfit,
                                       transform_matrix=each_item['transform'],
                                       zIndex=each_item['zIndex'])
                new_item.save()


            json_stuff = json.dumps({"success":"yes"})
            return HttpResponse(json_stuff, content_type="application/json")
    return HttpResponse("Error")

@csrf_exempt
def get_product(request):
    if request.is_ajax():
        if request.method == 'POST':
            cloth_type = request.POST.get('cloth_type')
            cloth_sub_type = request.POST.get('cloth_sub_type')
            current_profile = profile.objects.get(user=request.user)

            # amazon = AmazonAPI('AKIAJOR5NTXK2ERTU6AQ',
            #                    'kck/SKuTJif9bl7qeq5AyB4CU8HWsdz14VW4Iaz2',
            #                    'can037-20',
            #                    region="US")
            # products = amazon.search_n(15, Keywords="Women's " + cloth_type, SearchIndex="Apparel")
            current_gender = request.POST.get('gender')
            if current_gender == 'true':
                current_gender = True
            else:
                current_gender = False

            if cloth_type == "Favorites":
                products = current_profile.favorite_clothing.all()
            elif cloth_sub_type == "All":
                products = clothing.objects.filter(gender=current_gender,
                                                   cloth_type=cloth_type,
                                                   # cloth_sub_type__icontains=cloth_sub_type
                                                  )
            else:
                if cloth_sub_type == "Scarves & Wraps":
                    products = clothing.objects.filter(
                        (Q(cloth_sub_type__icontains="Scarves") |
                         Q(cloth_sub_type__icontains="Wraps") |
                         Q(cloth_sub_type__icontains="Scarves & Wraps")),
                        gender=current_gender
                    )
                else:
                    products = clothing.objects.filter(gender=current_gender,
                                                       # cloth_type=cloth_type,
                                                       cloth_sub_type__icontains=cloth_sub_type
                                                       )
            product_list = []
            for each_product in products:
                if (each_product.small_url is not None) and (each_product.large_url is not None):
                    is_in_cart = False
                    product_list.append({'small_url': each_product.small_url,
                                         'cloth_type': cloth_type,
                                         'item_id': str(each_product.carrier_id),
                                         'large_url': each_product.large_url,
                                         'carrier': each_product.carrier,
                                         'price': each_product.price,
                                         'brand': each_product.brand,
                                         'name': each_product.name,
                                         'color': each_product.color,
                                         'pk': each_product.pk,
                                         'is_in_cart': each_product.is_in_cart(current_profile)})
            json_stuff = json.dumps({"products": product_list,
                                     "cloth_type": cloth_type,
                                     })
            return HttpResponse(json_stuff, content_type="application/json")
    return HttpResponse("Error")

@csrf_exempt
def get_product_offset(request):
    if request.is_ajax():
        if request.method == 'POST':
            cloth_type = request.POST.get('cloth_type')
            brand = request.POST.get('brand')
            offset = int(request.POST.get('offset'))
            cloth_sub_type = request.POST.get('cloth_sub_type')
            try:
                current_profile = profile.objects.get(user=request.user)
            except Exception as e:
                print "Error ", e
                #user is likely not logged in
                current_profile = None

            current_gender = request.POST.get('gender')
            try:
                pagesize = int(request.POST.get('pagesize'))
                new_search = request.POST.get('new_search')
            except:
                pagesize = 15
                new_search = "Ignore"
            if current_gender == 'true':
                current_gender = True
            else:
                current_gender = False
            if cloth_type == "Favorites":
                try:
                    products = current_profile.favorite_clothing.all()
                except Exception as e:
                    #user is likely not logged in
                    print "Error ", e
                    products = clothing.objects.none()
            elif cloth_sub_type == "All":
                products = clothing.objects.filter(gender=current_gender,
                                                   cloth_type=cloth_type,
                                                   # cloth_sub_type__icontains=cloth_sub_type
                                                   )
            else:
                if cloth_sub_type == "Scarves & Wraps":
                    products = clothing.objects.filter(
                        (Q(cloth_sub_type__icontains="Scarves") |
                         Q(cloth_sub_type__icontains="Wraps") |
                         Q(cloth_sub_type__icontains="Scarves & Wraps")),
                        gender=current_gender
                    )
                else:
                    products = clothing.objects.filter(gender=current_gender,
                                                       # cloth_type=cloth_type,
                                                       cloth_sub_type__icontains=cloth_sub_type
                                                       )
            if brand != "":
                products = products.filter(brand__contains=brand,
                                           gender=current_gender)
            products = products[offset:pagesize+offset]
            product_list = []
            for each_product in products:
                if (each_product.small_url is not None) and (each_product.large_url is not None):
                    product_list.append({'small_url': each_product.small_url,
                                         'cloth_type': cloth_type,
                                         'item_id': str(each_product.carrier_id),
                                         'large_url': each_product.large_url,
                                         'carrier': each_product.carrier,
                                         'price': each_product.price,
                                         'brand': each_product.brand,
                                         'name': each_product.name,
                                         'color': each_product.color,
                                         'pk': each_product.pk,
                                         'gender': each_product.gender,
                                         'is_in_cart': each_product.is_in_cart(current_profile),
                                         'is_in_favorites': each_product.is_in_favorites(current_profile)})
            less_than_pagesize = len(products) < pagesize
            json_stuff = json.dumps({"products": product_list,
                                     "cloth_type": cloth_type,
                                     "offset": offset + len(products),
                                     "less_than_pagesize": less_than_pagesize,
                                     "new_search": new_search
                                     })
            return HttpResponse(json_stuff, content_type="application/json")
    return HttpResponse("Error")

@csrf_exempt
def get_outfit_discover(request):
    if request.is_ajax():
        if request.method == 'POST':
            offset = int(request.POST.get('offset'))
            cloth_type = request.POST.get('cloth_type')
            brand = request.POST.get('brand')
            print "brand = ", brand
            current_gender = request.POST.get('gender')
            tags = []
            clothing_colors = []
            try:
                tags = request.POST.getlist('tags')[0].split(",")
            except IndexError:
                print "index error on tags"
            try:
                clothing_colors = request.POST.getlist('colors')[0].split(",")
                print "clothing colors in = ", clothing_colors
            except IndexError:
                print "index error on colors"
            print "tags = ", tags
            if current_gender == 'true':
                current_gender = True
            else:
                current_gender = False
            pagesize = 5
            print "cloth type = ", cloth_type
            print "colors = ", clothing_colors
            print "gender = ", current_gender
            print "offset = ", offset

            #check to see if tag is actually just empty string
            if len(tags) == 1:
                if tags[0] == "":
                    tags = []

            has_filter = False
            if len(tags) > 0:
                has_filter = True
            elif brand != "":
                has_filter = True
            elif len(clothing_colors) > 0:
                has_filter = True

            print "has filter = ", has_filter

            if has_filter == False:
                outfits = outfit.objects.filter(gender=current_gender).order_by('-id')[offset:pagesize+offset]
            else:
                outfits = outfit.objects.filter(gender=current_gender).order_by('-id')
                if len(tags) > 0:
                    outfits = outfits.filter(
                        reduce(operator.or_, (
                            # Q(outfit_item__clothing__brand__contains=item) |
                                              Q(tag_list__word__contains=item)
                                              for item in tags)),
                        gender=current_gender
                    ).order_by('-id')
                if brand != "":
                    outfits = outfits.filter(outfit_item__clothing__brand__contains=brand).order_by('-id')
                if len(clothing_colors) > 0:
                    outfits = outfits.filter(
                        reduce(operator.or_, (
                            Q(outfit_item__clothing__color__contains=item)
                            for item in clothing_colors)),
                        gender=current_gender
                    ).order_by('-id')

                outfits = outfits[offset:pagesize+offset]
            print "offset = ", offset + len(outfits)
            product_list = []
            for each_product in outfits:
                duplicate = False
                for each_item in product_list:
                    if each_product.pk == each_item['pk']:
                        duplicate = True
                if not duplicate:
                    tag_list = []
                    for each_tag in each_product.tag_list.all():
                        tag_list.append(each_tag.word)
                    if request.user.is_authenticated():
                        current_profile = profile.objects.get(user=request.user)
                        product_list.append({
                                             'user_pk': each_product.profile.pk,
                                             'username': each_product.profile.user.username,
                                             'userPhoto': each_product.profile.profile_image,
                                             'num_likes': each_product.likes,
                                             'has_liked': each_product.does_user_like(current_profile),
                                             'is_following': each_product.profile.is_following(current_profile),
                                             'description': each_product.description,
                                             'tags': tag_list,
                                             'brands': each_product.get_brands(),
                                             'pk': each_product.pk,
                                             'pictures': each_product.get_pictures(),
                                             'location': each_product.profile.location
                                             })
                    else:
                        product_list.append({
                            'user_pk': each_product.profile.pk,
                            'username': each_product.profile.user.username,
                            'userPhoto': each_product.profile.profile_image,
                            'num_likes': each_product.likes,
                            'has_liked': False,
                            'is_following': False,
                            'description': each_product.description,
                            'tags': tag_list,
                            'brands': each_product.get_brands(),
                            'pk': each_product.pk,
                            'pictures': each_product.get_pictures(),
                            'location': each_product.profile.location
                        })
            less_than_pagesize = len(outfits) < pagesize
            print "product list = ", product_list
            print "length of list = ", len(product_list)
            json_stuff = json.dumps({"products": product_list,
                                     "cloth_type": cloth_type,
                                     "offset": offset + len(outfits),
                                     "less_than_pagesize": less_than_pagesize
                                     })
            return HttpResponse(json_stuff, content_type="application/json")
    return HttpResponse("Error")

@csrf_exempt
def get_product_full(request):
    if request.is_ajax():
        if request.method == 'POST':
            try:
                cloth_type = request.POST.get('cloth_type')
                amazon = AmazonAPI('AKIAJOR5NTXK2ERTU6AQ',
                                   'kck/SKuTJif9bl7qeq5AyB4CU8HWsdz14VW4Iaz2',
                                   'can037-20',
                                   region="US")
                products = amazon.search_n(99, Keywords="Women's " + cloth_type, SearchIndex="Apparel")
                product_list = []
                for each_product in products:
                    if each_product.small_image_url is not None:
                        product_list.append({'small_url': each_product.small_image_url,
                                             'cloth_type': cloth_type,
                                             'item_id': str(each_product.asin),
                                             'large_url': each_product.large_image_url,
                                             'carrier': each_product.carrier})
                json_stuff = json.dumps({"products": product_list,
                                         "cloth_type": cloth_type})
                return HttpResponse(json_stuff, content_type="application/json")
            except Exception as e:
                print "Error ", e
    return HttpResponse("Error")

def addNew(request):
    # if request.user.is_authenticated():
    template = loader.get_template('addNew.html')
    try:
        current_profile = profile.objects.get(user=request.user)
    except Exception as e:
        print "Error ", e
        current_profile = None
    context = {
        "current_profile": current_profile
    }
    # else:
    #     template = loader.get_template('headerLogin.html')
    #     context = {
    #     }
    return HttpResponse(template.render(context, request))

def test(request):
    if request.user.is_authenticated():
        template = loader.get_template('test.html')
        current_profile = profile.objects.get(user=request.user)
        context = {
            "current_profile": current_profile
        }
    else:
        template = loader.get_template('headerLogin.html')
        context = {
        }
    return HttpResponse(template.render(context, request))

def discover(request):
    # if request.user.is_authenticated():
    template = loader.get_template('index.html')
    try:
        current_profile = profile.objects.get(user=request.user)
    except:
        #user is likely not logged in
        current_profile = None
    context = {
        "current_profile": current_profile,
    }
    # else:
    #     template = loader.get_template('headerLogin.html')
    #     context = {
    #     }
    return HttpResponse(template.render(context, request))

def myCart(request):
    if request.user.is_authenticated():
        template = loader.get_template('myCart.html')
        current_profile = profile.objects.get(user=request.user)
        all_cart_items = current_profile.cart_items.all()
        ASIN = ""

        outfit_clothes = []
        for each_item in all_cart_items:
            outfit_clothes.append({'large_url': each_item.clothing.large_url,
                                   'name': each_item.clothing.name,
                                   'carrier': each_item.clothing.carrier,
                                   'brand': each_item.clothing.brand,
                                   'price': each_item.clothing.price,
                                   'is_in_cart': each_item.clothing.is_in_cart(current_profile),
                                   'pk': each_item.clothing.pk,
                                   'outfit_pk': each_item.outfit.pk})
            ASIN = each_item.clothing.carrier_id
        if len(outfit_clothes) == 0:
            is_empty = True
        else:
            is_empty = False
        amazon = bottlenose.Amazon('AKIAJOR5NTXK2ERTU6AQ',
                           'kck/SKuTJif9bl7qeq5AyB4CU8HWsdz14VW4Iaz2',
                           'can037-20',
                           MaxQPS=0.9
                           )
        cart_link = None
        try:
            kwargs = {
                "Item.0.ASIN": ASIN,
                "Item.0.Quantity": 1
            }
            response = amazon.CartCreate(**kwargs)
            soup = BeautifulSoup(response, "xml")
            newDictionary = xmltodict.parse(str(soup))
            CartId = newDictionary['CartCreateResponse']['Cart']['CartId']
            HMAC = newDictionary['CartCreateResponse']['Cart']['HMAC']
            counter = 0
            kwargs = {"CartId": CartId,
                      "HMAC": HMAC}
            for each_item in all_cart_items:
                kwargs["Item."+str(counter)+".ASIN"] = each_item.clothing.carrier_id
                kwargs["Item."+str(counter)+".Quantity"] = 1
                counter += 1
            print "kwargs = ", kwargs
            response = amazon.CartAdd(**kwargs)
            print "response = ", response
            soup = BeautifulSoup(response, "xml")
            newDictionary = xmltodict.parse(str(soup))
            cart_link = newDictionary['CartAddResponse']['Cart']['PurchaseURL']
            print newDictionary['CartAddResponse']['Cart']['PurchaseURL']
        except Exception as e:
            print "error: ", e

        context = {
            "access_key": "AKIAJOR5NTXK2ERTU6AQ",
            "associate_tag": "can037-20",
            "signature": "AJmBIow2qBu5GtdtJcYo9y8glhexQgxolmcIJK2xnlQ=",
            "link": cart_link,
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "current_profile": current_profile,
            "is_empty": is_empty,
            "all_clothing": outfit_clothes
        }
    else:
        template = loader.get_template('myCart.html')
        context = unregistered_cart(request)
    return HttpResponse(template.render(context, request))

def unregistered_cart(request):
    # current_profile = profile.objects.get(user=request.user)
    # all_cart_items = current_profile.cart_items.all()
    try:
        all_cart_items = request.session['cart']
    except:
        all_cart_items = []
    ASIN = ""

    outfit_clothes = []
    for each_item in all_cart_items:
        each_item = clothing.objects.get(pk=each_item)
        outfit_clothes.append({'large_url': each_item.large_url,
                               'name': each_item.name,
                               'carrier': each_item.carrier,
                               'brand': each_item.brand,
                               'price': each_item.price,
                               'is_in_cart': True,
                               'pk': each_item.pk,
                               'outfit_pk': 0})
        ASIN = each_item.carrier_id
    if len(outfit_clothes) == 0:
        is_empty = True
    else:
        is_empty = False
    amazon = bottlenose.Amazon('AKIAJOR5NTXK2ERTU6AQ',
                               'kck/SKuTJif9bl7qeq5AyB4CU8HWsdz14VW4Iaz2',
                               'can037-20',
                               MaxQPS=0.9
                               )
    cart_link = None
    try:
        kwargs = {
            "Item.0.ASIN": ASIN,
            "Item.0.Quantity": 1
        }
        response = amazon.CartCreate(**kwargs)
        soup = BeautifulSoup(response, "xml")
        newDictionary = xmltodict.parse(str(soup))
        CartId = newDictionary['CartCreateResponse']['Cart']['CartId']
        HMAC = newDictionary['CartCreateResponse']['Cart']['HMAC']
        counter = 0
        kwargs = {"CartId": CartId,
                  "HMAC": HMAC}
        for each_item in all_cart_items:
            each_item = clothing.objects.get(pk=each_item)
            kwargs["Item."+str(counter)+".ASIN"] = each_item.carrier_id
            kwargs["Item."+str(counter)+".Quantity"] = 1
            counter += 1
        print "kwargs = ", kwargs
        response = amazon.CartAdd(**kwargs)
        print "response = ", response
        soup = BeautifulSoup(response, "xml")
        newDictionary = xmltodict.parse(str(soup))
        cart_link = newDictionary['CartAddResponse']['Cart']['PurchaseURL']
        print newDictionary['CartAddResponse']['Cart']['PurchaseURL']
    except Exception as e:
        print "error: ", e

    return {
        "access_key": "AKIAJOR5NTXK2ERTU6AQ",
        "associate_tag": "can037-20",
        "signature": "AJmBIow2qBu5GtdtJcYo9y8glhexQgxolmcIJK2xnlQ=",
        "link": cart_link,
        "timestamp": datetime.datetime.utcnow().isoformat(),
        # "current_profile": current_profile,
        "is_empty": is_empty,
        "all_clothing": outfit_clothes
    }

@csrf_exempt
def like_outfit(request):
    if request.user.is_authenticated():
        if request.is_ajax():
            if request.method == 'POST':
                try:
                    outfit_key = request.POST.get('outfit')
                    current_outfit = outfit.objects.get(pk=outfit_key)
                    current_profile = profile.objects.get(user=request.user)
                    try:
                        current_like_obj = profile_likes_outfit.objects.get(profile=current_profile,
                                                                            outfit=current_outfit)
                        current_like_obj.delete()
                        like_status = "Unlike"
                    except Exception as e:
                        current_like_obj = profile_likes_outfit(profile=current_profile,
                                                                outfit=current_outfit)
                        current_like_obj.save()
                        like_status = "Like"
                    outfit_likes = profile_likes_outfit.objects.filter(outfit=current_outfit)
                    return_dict = {"status": like_status,
                                   "likes": len(outfit_likes)}
                    json_stuff = json.dumps(return_dict)
                    return HttpResponse(json_stuff, content_type="application/json")
                except Exception as e:
                    print "Error ", e

    return HttpResponse("Error")

@csrf_exempt
def follow_user(request):
    if request.user.is_authenticated():
        if request.is_ajax():
            if request.method == 'POST':
                try:
                    profile_key = request.POST.get('user')
                    current_profile = profile.objects.get(user=request.user)
                    selected_profile = profile.objects.get(pk=profile_key)
                    try:
                        current_follow_obj = profile_follows.objects.get(profile_main=current_profile,
                                                                         profile_following=selected_profile)
                        current_follow_obj.delete()
                        return HttpResponse("Unfollow")
                    except Exception as e:
                        current_follow_obj = profile_follows(profile_main=current_profile,
                                                             profile_following=selected_profile)
                        current_follow_obj.save()
                        return HttpResponse("Follow")
                except Exception as e:
                    print "Error ", e
    else:
        return HttpResponse("Not Logged In")
    return HttpResponse("Error")

@csrf_exempt
def add_to_favorites(request):
    if request.user.is_authenticated():
        if request.is_ajax():
            if request.method == 'POST':
                try:
                    clothing_key = request.POST.get('clothing')
                    print "clothing key = ", clothing_key
                    clothing_obj = clothing.objects.get(pk=clothing_key)
                    current_profile = profile.objects.get(user=request.user)
                    #looking to see if item is in cart. If so, remove from cart
                    if current_profile.item_in_favorites(clothing_obj):
                        print "in favorites"
                        current_profile.favorite_clothing.remove(clothing_obj)
                        return HttpResponse("Removed")

                    else:
                        #could not find item in cart, creating instead
                        current_profile.favorite_clothing.add(clothing_obj)
                        current_profile.save()
                        return HttpResponse("Added")

                except Exception as e:
                    print "Error ", e
    else:
        return add_to_cart_single_unregistered(request)
    return HttpResponse("Error")

@csrf_exempt
def add_to_cart_single(request):
    if request.user.is_authenticated():
        if request.is_ajax():
            if request.method == 'POST':
                try:
                    outfit_key = request.POST.get('outfit')
                    clothing_key = request.POST.get('clothing')
                    print "outfit key = ", outfit_key
                    print "tyep = ", type(outfit_key)
                    if int(outfit_key) == -1:
                        admin = profile.objects.get(user__username="admin")
                        print "admin = ", admin
                        outfit_obj = outfit.objects.filter(profile = admin)[0]
                    else:
                        outfit_obj = outfit.objects.get(pk=outfit_key)
                    clothing_obj = clothing.objects.get(pk=clothing_key)
                    current_profile = profile.objects.get(user=request.user)
                    #looking to see if item is in cart. If so, remove from cart
                    cart_item = cartItems(clothing=clothing_obj, outfit=outfit_obj)
                    if current_profile.item_in_cart(cart_item):
                        print "in cart"
                        current_profile.remove_cart_item(cart_item)
                        return HttpResponse("Removed")

                    else:
                        #could not find item in cart, creating instead
                        new_item = cartItems(clothing=clothing_obj, outfit=outfit_obj)
                        new_item.save()
                        current_profile.cart_items.add(new_item)
                        current_profile.save()
                        return HttpResponse("Added")

                except Exception as e:
                    print "Error ", e
    else:
        print "using unregistered"
        return add_to_cart_single_unregistered(request)
    return HttpResponse("Error")

def add_to_cart_single_unregistered(request):
    if request.is_ajax():
        if request.method == 'POST':
            try:
                # outfit_key = request.POST.get('outfit')
                clothing_key = request.POST.get('clothing')
                # outfit_obj = outfit.objects.get(pk=outfit_key)
                clothing_obj = clothing.objects.get(pk=clothing_key)
                #looking to see if item is in cart. If so, remove from cart
                try:
                    if type(request.session['cart']) == type([]):
                        if clothing_obj.pk not in request.session['cart']:
                            old_req = request.session['cart']
                            old_req.append(clothing_obj.pk)
                            request.session['cart'] = old_req
                            return HttpResponse("Added")
                        else:
                            old_req = request.session['cart']
                            old_req.remove(clothing_obj.pk)
                            request.session['cart'] = old_req
                            return HttpResponse("Removed")
                except:
                    request.session['cart'] = []
                    if type(request.session['cart']) == type([]):
                        if clothing_obj.pk not in request.session['cart']:
                            old_req = request.session['cart']
                            old_req.append(clothing_obj.pk)
                            request.session['cart'] = old_req
                            return HttpResponse("Added")
                        else:
                            old_req = request.session['cart']
                            old_req.remove(clothing_obj.pk)
                            request.session['cart'] = old_req
                            return HttpResponse("Removed")



            except Exception as e:
                print "Error ", e

@csrf_exempt
def add_to_cart_whole(request):
    if request.user.is_authenticated():
        if request.is_ajax():
            if request.method == 'POST':
                try:
                    outfit_key = request.POST.get('outfit')
                    outfit_obj = outfit.objects.get(pk=outfit_key)
                    current_profile = profile.objects.get(user=request.user)
                    returned_clothing_id_list = []

                    #get all clothes in outfit
                    clothes = outfit_obj.get_outfit_items()
                    for each_item in clothes:
                        #If item is not in cart, then add it to cart
                        cart_item = cartItems(clothing=each_item.clothing, outfit=outfit_obj)
                        if current_profile.item_in_cart(cart_item) == False:
                            new_item = cartItems(clothing=each_item.clothing, outfit=outfit_obj)
                            new_item.save()
                            current_profile.cart_items.add(new_item)
                            current_profile.save()
                            returned_clothing_id_list.append(each_item.clothing.pk)

                    json_stuff = json.dumps(returned_clothing_id_list)
                    return HttpResponse(json_stuff, content_type="application/json")
                    # return HttpResponse(returned_clothing_id_list)

                except Exception as e:
                    print "Error ", e

    else:
        add_to_cart_whole_unregistered(request)
    return HttpResponse("Error")

def add_to_cart_whole_unregistered(request):
    if request.is_ajax():
        if request.method == 'POST':
            try:
                outfit_key = request.POST.get('outfit')
                outfit_obj = outfit.objects.get(pk=outfit_key)
                returned_clothing_id_list = []

                #get all clothes in outfit
                clothes = outfit_obj.get_outfit_items()
                for each_item in clothes:
                    #If item is not in cart, then add it to cart
                    # cart_item = cartItems(clothing=each_item.clothing, outfit=outfit_obj)
                    try:
                        if type(request.session['cart']) == type([]):
                            if each_item.clothing.pk not in request.session['cart']:
                                old_req = request.session['cart']
                                old_req.append(each_item.clothing.pk)
                                request.session['cart'] = old_req
                                returned_clothing_id_list.append(each_item.clothing.pk)
                    except:
                        request.session['cart'] = []
                        if type(request.session['cart']) == type([]):
                            if each_item.clothing.pk not in request.session['cart']:
                                old_req = request.session['cart']
                                old_req.append(each_item.clothing.pk)
                                request.session['cart'] = old_req
                                returned_clothing_id_list.append(each_item.clothing.pk)

                json_stuff = json.dumps(returned_clothing_id_list)
                return HttpResponse(json_stuff, content_type="application/json")
                # return HttpResponse(returned_clothing_id_list)

            except Exception as e:
                print "Error ", e

@csrf_exempt
def remove_from_cart(request):
    if request.user.is_authenticated():
        if request.is_ajax():
            if request.method == 'POST':
                try:
                    outfit_key = request.POST.get('outfit')
                    clothing_key = request.POST.get('clothing')
                    outfit_obj = outfit.objects.get(pk=outfit_key)
                    clothing_obj = clothing.objects.get(pk=clothing_key)
                    current_profile = profile.objects.get(user=request.user)

                    cart_item = cartItems(outfit=outfit_obj, clothing=clothing_obj)
                    current_profile.remove_cart_item(cart_item)

                    if len(current_profile.cart_items.all()) == 0:
                        return HttpResponse("Removed, Empty")
                    else:
                        return HttpResponse("Removed")

                except Exception as e:
                    print "Error ", e
    else:
        #remove from unregistered cart
        return add_to_cart_single_unregistered(request)
    return HttpResponse("Error")

def userProfile(request, pk):
    # if request.user.is_authenticated():
    template = loader.get_template('userProfile.html')
    current_profile = profile.objects.get(pk=pk)
    try:
        current_profile_self = profile.objects.get(user=request.user)
    except:
        #user is likely not logged in
        current_profile_self = None
    all_outfits = outfit.objects.filter(profile=current_profile)
    outfit_number = len(all_outfits)
    current_profile_outfits = get_outfit_items(all_outfits, current_profile)
    current_profile_json = {}
    print "IS FOLLOWING = ", current_profile.is_following(current_profile_self)
    if current_profile.user == request.user:
        current_profile_json = {
            'fullName': current_profile.full_name,
            'gender': current_profile.gender,
            'joinedDate': str(current_profile.joined_date),
            'email': current_profile.user.email,
            'website': current_profile.website,
            'location': current_profile.location,
            'description': current_profile.description,
            'displayFullName': current_profile.display_fullName,
            'displayGender': current_profile.display_gender,
            'displayJoinedDate': current_profile.display_joined_date,
            'displayEmail': current_profile.display_email,
            'displayWebsite': current_profile.display_website,
            'displayLocation': current_profile.display_location,
            'displayDescription': current_profile.display_description
        }
    context = {
        "current_profile_user": current_profile,
        "current_profile": current_profile_self,
        "is_following": current_profile.is_following(current_profile_self),
        "outfit_number": outfit_number,
        "is_self": current_profile.user == request.user,
        "outfits": json.dumps(current_profile_outfits),
        "current_profile_json": json.dumps(current_profile_json)
    }
    # else:
    #     template = loader.get_template('headerLogin.html')
    #     context = {
    #     }
    return HttpResponse(template.render(context, request))

def outfit_page(request, pk):
    if request.user.is_authenticated():
        template = loader.get_template('outfitPage.html')
        current_outfit = outfit.objects.get(pk=pk)
        current_profile = current_outfit.profile
        current_profile_self = profile.objects.get(user=request.user)
        current_profile_outfits = get_outfit_items([current_outfit], current_profile_self)
        outfit_clothes = []
        outfit_items = outfit_item.objects.filter(outfit=current_outfit)
        for each_item in outfit_items:
            outfit_clothes.append({'large_url': each_item.clothing.large_url,
                                   'name': each_item.clothing.name,
                                   'carrier': each_item.clothing.carrier,
                                   'brand': each_item.clothing.brand,
                                   'price': each_item.clothing.price,
                                   'is_in_cart': each_item.clothing.is_in_cart(current_profile_self),
                                   'pk': each_item.clothing.pk})

        context = {
            "current_outfit": current_outfit,
            "current_outfit_in_cart": current_profile_self.outfit_in_cart(current_outfit),
            "current_profile": current_profile,
            "current_profile_self": current_profile_self,
            "outfits": json.dumps(current_profile_outfits),
            # "outfit_clothes": current_outfit.get_outfit_items()
            "outfit_clothes": outfit_clothes
        }
    else:
        try:
            print "shopping cart = ", request.session['cart']
        except:
            print "no cart"
        template = loader.get_template('outfitPage.html')
        current_outfit = outfit.objects.get(pk=pk)
        current_profile = current_outfit.profile
        # current_profile_self = profile.objects.get(user=request.user)
        current_profile_outfits = get_outfit_items([current_outfit], current_profile)
        outfit_clothes = []
        outfit_items = outfit_item.objects.filter(outfit=current_outfit)
        for each_item in outfit_items:
            outfit_clothes.append({'large_url': each_item.clothing.large_url,
                                   'name': each_item.clothing.name,
                                   'carrier': each_item.clothing.carrier,
                                   'brand': each_item.clothing.brand,
                                   'price': each_item.clothing.price,
                                   'is_in_cart': False,
                                   'pk': each_item.clothing.pk})

        context = {
            "current_outfit": current_outfit,
            # "current_outfit_in_cart": current_profile_self.outfit_in_cart(current_outfit),
            "current_profile": current_profile,
            # "current_profile_self": current_profile_self,
            "outfits": json.dumps(current_profile_outfits),
            # "outfit_clothes": current_outfit.get_outfit_items()
            "outfit_clothes": outfit_clothes
        }
    return HttpResponse(template.render(context, request))

def clothing_page(request, pk):
    # if request.user.is_authenticated():
    template = loader.get_template('clothingPage.html')
    current_clothing = clothing.objects.get(pk=pk)
    try:
        current_profile = profile.objects.get(user=request.user)
    except Exception as e:
        print "Error ", e
        #user is likely not logged in
        current_profile = None
    context = {
        "current_profile_self": current_profile,
        "current_clothing": current_clothing
    }
    # else:
    #     template = loader.get_template('clothingPage.html')
    #     current_clothing = clothing.objects.get(pk=pk)
    #     # current_profile_self = profile.objects.get(user=request.user)
    #     context = {
    #         # "current_profile_self": current_profile_self,
    #         "current_clothing": current_clothing
    #     }
    return HttpResponse(template.render(context, request))

@csrf_exempt
def change_profile_settings(request):
    if request.user.is_authenticated():
        if request.is_ajax():
            if request.method == 'POST':
                try:
                    data = json.loads(request.POST.get('data'))
                    print "data = ", data
                    current_profile = profile.objects.get(user=request.user)
                    for key in data:
                        print "%s, %s" % (key, data[key])
                        if key == "fullName":
                            current_profile.full_name = data[key]
                        if key == "gender":
                            current_profile.gender = data[key]
                        if key == "joinedDate":
                            current_profile.joined_date = data[key]
                        if key == "email":
                            current_profile.user.email = data[key]
                        if key == "website":
                            current_profile.website = data[key]
                        if key == "location":
                            current_profile.location = data[key]
                        if key == "description":
                            current_profile.description = data[key]
                        if key == "displayFullName":
                            current_profile.display_fullName = data[key]
                        if key == "displayGender":
                            current_profile.display_gender = data[key]
                        if key == "displayJoinedDate":
                            current_profile.display_joined_date = data[key]
                        if key == "displayEmail":
                            current_profile.display_email = data[key]
                        if key == "displayWebsite":
                            current_profile.display_website = data[key]
                        if key == "displayLocation":
                            current_profile.display_location = data[key]
                        if key == "displayDescription":
                            current_profile.display_description = data[key]

                        current_profile.save()

                    return HttpResponse("Success")

                except Exception as e:
                    print "Error ", e
                    return HttpResponse("Error")
    return HttpResponse("Error")

def save_profile(backend, user, response, *args, **kwargs):
    # if backend.name == 'twitter':
    print "user = ", user
    # profile = user.get_profile()
    social_media_profile_obj = UserSocialAuth.objects.filter(user=user)[0]
    print "profile obj = ", social_media_profile_obj
    try:
        current_profile = social_media_profile.objects.get(social_media=social_media_profile_obj)
        print "found current profile"
    except Exception as e:
        print "error: ", e
        profile_obj = profile(user=user)
        if backend == 'facebook':
            profile_obj.user.email = response.get('email')
        if backend == 'twitter':
            print "response = ", response
            profile_obj.user.email = response.get('email')
        profile_obj.save()

        new_social_media = social_media_profile(profile=profile_obj, social_media=social_media_profile_obj)
        new_social_media.save()
    print "profile = ", profile
    # if profile is None:
        # profile = profile(user_id=user.id)
        # print "profile does not exist"
    # profile.gender = response.get('gender')
    # profile.link = response.get('link')
    # profile.timezone = response.get('timezone')
    # profile.save()
    print "bang"

def social_user(backend, uid, user=None, *args, **kwargs):
    '''OVERRIDED: It will logout the current user
    instead of raise an exception '''

    provider = backend.name
    social = backend.strategy.storage.user.get_social_auth(provider, uid)
    if social:
        if user and social.user != user:
            logout(backend.strategy.request)
            #msg = 'This {0} account is already in use.'.format(provider)
            #raise AuthAlreadyAssociated(backend, msg)
        elif not user:
            user = social.user
    return {'social': social,
            'user': user,
            'is_new': user is None,
            'new_association': False}

def get_avatar(backend, strategy, details, response,
               user=None, *args, **kwargs):
    url = None
    if backend.name == 'facebook':
        print "response = ", response
        url = "http://graph.facebook.com/%s/picture?type=large"%response['id']
    if backend.name == 'twitter':
        print "response = ", response
        url = response.get('profile_image_url', '').replace('_normal','')
        print "url = ", url
    if backend.name == 'pinterest':
        print response
        if response.get('image'):
            url = response.get('image')
    if url:
        current_profile = profile.objects.get(user=user)
        current_profile.profile_image = url
        current_profile.save()
        # user.avatar = url
        # user.save()
    print "end of get avatar"

def terms(request):
    template = loader.get_template('terms.html')
    context = {}
    return HttpResponse(template.render(context, request))

def blog(request):
    template = loader.get_template('blogPage.html')
    all_posts = blog_post.objects.filter()
    try:
        current_profile = profile.objects.get(user=request.user)
    except:
        current_profile = None
    context = {"posts": all_posts,
               "current_profile": current_profile}
    return HttpResponse(template.render(context, request))

def blog_item(request, slug):
    print "slug = ", slug
    current_post = blog_post.objects.get(slug=slug)
    template = loader.get_template('blogArticlePage.html')
    try:
        current_profile = profile.objects.get(user=request.user)
    except:
        current_profile = None
    context = {"posts": [current_post],
               "current_profile": current_profile}
    return HttpResponse(template.render(context, request))

def privacy(request):
    template = loader.get_template('privacy.html')
    context = {}
    return HttpResponse(template.render(context, request))

def cart_checkout(request):
    if request.user.is_authenticated():
        if request.is_ajax():
            if request.method == 'GET':
                current_profile = profile.objects.get(user=request.user)
                print request.user
                #create potential purchase object
                cart_referral_obj = cart_referral(profile=current_profile,
                                                  store="Amazon",
                                                  )
                cart_referral_obj.save()
                namestring = ""
                for each_item in current_profile.cart_items.all():
                    namestring = namestring + "-"  + str(each_item.clothing.name)
                    cart_referral_obj.cart_items.add(each_item)
                cart_referral_obj.save()
                #consider dumping user's cart here

                print namestring
                return HttpResponse(namestring)
    return HttpResponse("Error")


