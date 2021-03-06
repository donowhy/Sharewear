(function($){
    $(function(){
        // $('select').material_select();
        $('.button-collapse').sideNav();
        $('.carousel').carousel();
        $('.modal').modal();
        $('input.autocomplete').autocomplete({
            data: BRANDS,
            limit: 20, // The max amount of results that can be shown at once. Default: Infinity.
            onAutocomplete: function(val) {
                populate_product(true);
            },
            minLength: 1, // The minimum length of the input for the autocomplete to start. Default: 1.
        });
    }); // end of document ready
})(jQuery); // end of jQuery name space
$(document).ready(function() {
    $('select').material_select();
});
function getCookie(c_name) {
    if(document.cookie.length > 0) {
        c_start = document.cookie.indexOf(c_name + "=");
        if(c_start != -1) {
            c_start = c_start + c_name.length + 1;
            c_end = document.cookie.indexOf(";", c_start);
            if(c_end == -1) c_end = document.cookie.length;
            return unescape(document.cookie.substring(c_start,c_end));
        }
    }
    return "";
}
var csrftoken = getCookie('csrftoken');
function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
var PAGINATION = [];
var REQUESTS = [];
var HAMMERS = [];
var CURRENT_PAGE = 1;
var GENDER = document.getElementById('gender_check').checked;
var TAG_LIST = [];
var COLOR_LIST = [];
var OFFSET = 0;
populate_product(true);

function remove_requests(){
    for(var i = 0; i < REQUESTS.length; i++) {
        REQUESTS[i].abort();
        REQUESTS.splice( i, 1 );
        console.log("request aborted");

    }
}

function populate_product(new_search){
    var offsetVar = OFFSET;
    if(new_search) {
        $("#product_list").empty();
        offsetVar = 0;
    }
    // $("#routineLoader").show();
    REQUESTS.push(
        $.ajax({
                type: 'POST',
                url: '/get_outfit_discover/',
                headers: {
                    "X-CSRFToken": getCookie("csrftoken")
                },
                data: {
                    'gender': GENDER,
                    'offset': offsetVar,
                    'tags': TAG_LIST,
                    'brand': $("#brandSelect").val(),
                    'colors': COLOR_LIST},
                success: function (json) {
                    if(json.products.length == 0){
                        $("#noResults").show();
                    }
                    else{
                        $("#noResults").hide();
                    }
                    if(new_search){
                        PAGINATION = [];
                    }
                    OFFSET = json.offset;
                    var duplicate = false;
                    for(var i=0; i < json.products.length; i++){
                        duplicate = false;
                        for(var j=0; j < PAGINATION.length; j++){
                            if(json.products[i].pk == PAGINATION[j].pk){
                                duplicate = true;
                                break;
                            }
                        }
                        if(!duplicate) {
                            product_loader_template([json.products[i]], false);
                            PAGINATION.push(json.products[i])
                        }
                    }


                    $("#loading_paginate").show();
                    // $("#routineLoader").hide();
                    $('.carousel').carousel();
                    if(json.less_than_pagesize){
                        OFFSET = "END";
                        $("#product_loader").hide();
                        return 0;
                    }
                },
                error: function (json) {
                    // $("#createRoutine").show();
                    console.log("ERROR", json);
                }
            }
        )
    );
}

function product_loader_template(items, new_search){
    if(new_search) {
        $("#product_list").empty();
    }
    var tag_list = "";
    var brand_list = "";
    var htmlString = "";
    var hasLiked;
    var isFollowing;
    var numLikes;
    var likeString;
    var followString;
    var outfitPictures
    for(var i=0; i < items.length; i++){
        console.log(items[i]);
        tag_list = "";
        brand_list = "";
        htmlString = "";
        likeString = "";
        followString = "";
        outfitPictures = "";
        for(var j=0; j < items[i].tags.length; j++){
            tag_list += "<div class='chip'>"
                +   items[i].tags[j]
                +   "</div>";
        }
        for(var j=0; j < items[i].brands.length; j++){
            brand_list += "<div class='chip'>"
                +   items[i].brands[j]
                +   "</div>";
        }
        hasLiked = items[i].has_liked;
        isFollowing = items[i].is_following;
        numLikes = items[i].num_likes;
        if(hasLiked == true) {
            if (numLikes == 1) {
                likeString = "You like this.";
            }
            else {
                numLikes = numLikes - 1;
                if (numLikes == 1) {
                    likeString = "You and " + numLikes + " person like this.";
                }
                else {
                    likeString = "You and " + numLikes + " people like this.";
                }
            }
        }
        else if(hasLiked == false){
            if(numLikes == 1) {
                likeString = numLikes + " person likes this.";
            }
            else{
                likeString = numLikes + " people like this.";
            }
        }
        if(isFollowing){
            followString ="<a class='waves-effect waves-dark btn' id='follow"+items[i].user_pk+"x"+items[i].pk+"' onClick='followClick(this.id)' style='border:1px solid #2bbbad; background-color:#2bbbad; color:white;'>Following</a>";

        }
        else{
            followString = "<a class='waves-effect waves-dark btn' id='follow"+items[i].user_pk+"x"+items[i].pk+"' onClick='followClick(this.id)' style='border:1px solid #ff6e66; background-color:white; color:#ff6e66;'>Follow</a>";
        }
        for(var j=0; j < items[i].pictures.length; j++){
            outfitPictures += "<a class='carousel-item' href='#one!'><img src='"+items[i].pictures[j]+"'></a>";
        }
        console.log("hasLiked = ", outfitPictures);
        htmlString += "<div id='outfit"+items[i].pk+"' class='row'>"
        +"<div class='card col s12 m6 push-m3' style='padding-bottom:1%; padding-top:1%;'>"
        +"    <div class='col s12' style='margin-top:5%;'>"
        +"    <div class='col s3' style='float:left; margin-top:-15px; margin-left:-25px;'>"
        +"    <img src='"+items[i].userPhoto+"' alt='' class='circle responsive-img profile-post-uer-image'>"
        +"    </div>"
        +"    <div class='col s5' style='margin-top:-10px; margin-left:-20px;'>"
        +"    <h5 class='grey-text text-darken-4 margin profileUser' style='word-wrap:break-word; margin-bottom:0;'><a style='color:#ff6e66 !important;' href='/user/"+items[i].user_pk+"'>"+items[i].username+"</a></h5>"
        +"<span class='grey-text text-darken-1 ultra-small'>"+items[i].location+"</span>"
        +"</div>"
        +"<div class='col s4'>"
        + followString
        +"    </div>"
        +"    </div>"
        +"    <div class='col s12 profileSocialBody'>"
        +"    <div class='col s10'>"
        +"    <div class='col s12 ' style='padding-top:5px;'>"
        +"    <i onClick='addToCart("+items[i].pk+")' class='material-icons left socialIcons featuredProfileSocial'>shopping_cart</i>";
        if(hasLiked == true) {
            htmlString += "    <i id='like"+items[i].pk+"' onClick='likeOutfit(this.id)' class='material-icons left socialIcons featuredProfileSocial'>favorite</i>";
        }
        else{
            htmlString += "    <i id='like"+items[i].pk+"' onClick='likeOutfit(this.id)' class='material-icons left socialIcons featuredProfileSocial'>favorite_border</i>";
        }
        // htmlString += "    <i class='material-icons left socialIcons featuredProfileSocial'>share</i>"
        // +"    <i class='material-icons left socialIcons featuredProfileSocial'>comment</i>"
        htmlString += "    </div>"
        +"    <div class='col s12 featuredProfileSocial' style='padding-top:5px;'>"
        +"    <span id='likeString"+items[i].pk+"' class='left grey-text text-darken-2 ultra-small'>"+likeString+"</span>"
        +"    </div>"
        +"    </div>"
        +"    <div class='col s2'>"
        // +"    <i onClick='featuredVert(this.id)'  class='material-icons left socialIcons right'>keyboard_arrow_down</i>"
        +"    </div>"
        +"    </div>"
        +"    <hr>"
        +"    <div class='col s12 center-align'>";
        if(items[i].pictures.length > 1) {
            htmlString += " <div class='carousel' style='height:250px;'>"
            + outfitPictures
            + "</div>";
        }
        else{
            htmlString +="<img style='height:250px;' class='responsive-img' src='"+items[i].pictures[0]+"'>";
        }

        htmlString += "    </div>"
        +"    <div class='col s12 left-align' style='padding-left:0px;'>"
        +"    <div class='col s12 center-align' style='padding:2%;'>"
        +"    <a href='/outfit/"+items[i].pk+"' class='waves-effect waves-dark btn' style='border:1px solid #ff6e66; background-color:white; color:#ff6e66; width:80%;'>View Outfit</a>"
        +"</div>";
        if(items[i].description.length > 0){
            htmlString += "<div class='col s12'>"
            +"    <p style='margin:0px;padding-left:0px;'>Description: "+items[i].description+"</p>"
            +"</div>"
            +"<br>"
            +"<hr>";
        }

        if(tag_list.length > 0) {
            htmlString += "<div class='col s12'>"
            + "<p style='margin:0px;padding-left:0px;'>Tags:"
            + tag_list
            + "    </p>"
            + "    </div>"
            + "    <hr>";
        }
        if(brand_list.length > 0){
            htmlString += "<div class='col s12'>"
            +"    <p style='margin:0px;padding-left:0px;'>Brands:"
            + brand_list
            + "    </p>"
            +"</div>";
        }
        htmlString += "    </div>"
        +"</div>"
        +"</div>";
        $("#product_list").append(htmlString);
    }
}


// function load_pagination(){
//     var itemsPerPage = 15;
//     console.log("pagination - ", PAGINATION);
//     var itemLength = PAGINATION.length;
//     var pages = Math.ceil(itemLength / itemsPerPage);
//
//     console.log("items per page = ", itemsPerPage);
//     console.log("items length = ", itemLength);
//     console.log("pages = ", pages);
//     $("#pagination").empty();
//     $("#pagination").append("<li onClick='page_prev()' class='disabled'><a href='#!'><i class='material-icons'>chevron_left</i></a></li>"
//         + "<li onClick='load_page(1)' id='pag1' class='active'><a href='#!'>1</a></li>");
//     for(var i=2; i <= pages; i++){
//         $("#pagination").append("<li onClick='load_page("+ i +")' id='pag"+i+"' class='waves-effect'><a href='#!'>"+i+"</a></li>");
//     }
//     $("#pagination").append("<li onClick='page_next()' class='waves-effect'><a href='#!'><i class='material-icons'>chevron_right</i></a></li>");
//     $("#loading_paginate").hide();
// }

// function page_prev(){
//     load_page(CURRENT_PAGE-1);
// }
//
// function page_next(){
//     load_page(CURRENT_PAGE+1);
// }
//
// function load_page(page){
//     console.log("loading page ", page);
//     var itemsPerPage = 15;
//     var itemLength = PAGINATION.length;
//     var pages = Math.ceil(itemLength / itemsPerPage);
//
//     if (pages >= page){
//         if( page > 0) {
//             $("li.active").removeClass("active");
//             $("#pag"+page).addClass("active");
//             CURRENT_PAGE = page;
//             var items = [itemsPerPage * (page - 1), (itemsPerPage * (page)) - 1];
//             product_loader_template(PAGINATION.slice(items[0], items[1]));
//         }
//     }
// }

function signOut(){
    $.ajax({
        type:"GET",
        url:"/logout",
        headers : {
            "X-CSRFToken": getCookie("csrftoken")
        },
        success: function(data){
            window.location.replace("/");
        }
    });
}

function followClick(dom_id){
    var userKey = dom_id.split("follow")[1].split("x")[0];
    var domObject = $("#"+dom_id);
    $.ajax({
            type: 'POST',
            url: '/follow_user/',
            headers: {
                "X-CSRFToken": getCookie("csrftoken")
            },
            data: {'user':userKey},
            success: function (json) {
                console.log("json = ", json);
                if(json == "Follow"){
                    //add is_follow=True to all outfits of this user
                    setUserFollowUnfollow(userKey, true);
                    //re-initialize any outfits whose user is the user we are following
                    reloadFollowBtn(userKey);
                }
                else if(json == "Unfollow"){
                    setUserFollowUnfollow(userKey, false);
                    reloadFollowBtn(userKey);
                }

            },
            error: function (json) {
                // $("#createRoutine").show();
                console.log("ERROR", json);
            }
        }
    )
}

function setUserFollowUnfollow(userKey, followVal){
    //Finds all occurences of the user in the outfit array and sets their 'is_following' property accordingly
    for(var i=0; i < PAGINATION.length; i++){
        if(PAGINATION[i].user_pk == userKey){
            PAGINATION[i].is_following = followVal;
        }
    }
}

function reloadFollowBtn(user_id){
    var domObject;
    for(var i=0; i < PAGINATION.length; i++){
        if(PAGINATION[i].user_pk == user_id){
            domObject = $("#follow"+user_id+"x"+PAGINATION[i].pk);
            if(PAGINATION[i].is_following == true){
                domObject.text("Following");
                domObject.css('color', 'white');
                domObject.css('background-color', '#2bbbad');
                domObject.css('border', '1px solid #2bbbad');
            }
            else if(PAGINATION[i].is_following == false){
                domObject.text("Follow");
                domObject.css('color', '#ff6e66');
                domObject.css('background-color', 'white');
                domObject.css('border', '1px solid #ff6e66');
            }
        }
    }
}

function likeOutfit(id){
    //get current featured
    var currentOutfit = id.split("like")[1];
    console.log("curernt outfit = ", currentOutfit);
    $.ajax({
            type: 'POST',
            url: '/like_outfit/',
            headers: {
                "X-CSRFToken": getCookie("csrftoken")
            },
            data: {'outfit':currentOutfit},
            success: function (json) {
                console.log("json = ", json);
                var numLikes = json.likes;
                if(json.status == "Like"){
                    // numLikes += 1;
                    //modify html of current outfit
                    $("#like"+currentOutfit).html('favorite');
                    if(numLikes == 1){
                        $("#likeString"+currentOutfit).html("You like this.");
                    }
                    else {
                        var total_likes = numLikes-1;
                        if(total_likes == 1){
                            $("#likeString"+currentOutfit).html("You and " + total_likes + " person likes this.");
                        }
                        else {
                            $("#likeString"+currentOutfit).html("You and " + total_likes + " people like this.");
                        }
                    }

                }
                else if(json.status == "Unlike"){
                    $("#like"+currentOutfit).html('favorite_border');
                    console.log("numlikes2 = ", numLikes);
                    if(numLikes == 1){
                        $("#likeString"+currentOutfit).html(numLikes + " person likes this.");
                    }
                    else {
                        $("#likeString"+currentOutfit).html(numLikes + " people like this.");
                    }
                }

            },
            error: function (json) {
                // $("#createRoutine").show();
                console.log("ERROR", json);
            }
        }
    )
}
function throttle(func, wait) {
    var timeout;
    return function() {
        var context = this, args = arguments;
        if (!timeout) {
            // the first time the event fires, we setup a timer, which
            // is used as a guard to block subsequent calls; once the
            // timer's handler fires, we reset it and create a new one
            timeout = setTimeout(function() {
                timeout = null;
                func.apply(context, args);
            }, wait);
        }
    }
}


$(window).scroll(throttle(function (event) {
    if(OFFSET != "END") {
        var scroll = $(window).scrollTop();
        if (scroll >= $(window).height() / 2) {
            console.log("in half");
            populate_product(false);
        }
        console.log(scroll + " - " + $(window).height());
        console.log(scroll > $(window).height() / 4);
    }
    // Do something
},3000));

$('#tag_list').on('change', function (event)
{
    var $element   = $(event.target),
        $container = $element.closest('.example');

    if (!$element.data('materialtags'))
    {
        return;
    }

    var val = $element.val();
    if (val === null)
    {
        val = "null";
    }
    console.log("val = ", val);
    TAG_LIST = val;
    populate_product(true)

}).trigger('change');

$('#colorSelect').on('change', function (event)
{
    var $element   = $(event.target),
        $container = $element.closest('.example');

    if (!$element.data('materialtags'))
    {
        return;
    }

    var val = $element.val();
    if (val === null)
    {
        val = "null";
    }
    console.log("val = ", val);
    COLOR_LIST = val;
    populate_product(true)

}).trigger('change');

$("#gender_check").change(function() {
    console.log("gender checked");
    GENDER = this.checked;
    populate_product(true);
});

function populateBrands(){
    console.log("clicked");
}

function searchVert(id){
    $("#filterOptions").toggle();
    if ($("#filterOptions").is(':hidden')) {
        $("#"+id).html('keyboard_arrow_up');
    }
    else{
        $("#"+id).html('keyboard_arrow_down');
    }
}

function addToCart(id){
    $.ajax({
            type: 'POST',
            url: '/add_to_cart_whole/',
            headers: {
                "X-CSRFToken": getCookie("csrftoken")
            },
            data: {'outfit':id},
            success: function (json) {
                Materialize.toast('Outfit added to cart', 4000) // 4000 is the duration of the toast
            },
            error: function (json) {
                // $("#createRoutine").show();
                console.log("ERROR", json);
            }
        }
    )
}

if( /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) ) {
    $("#visitApp").hide();
}
else{
    $("#visitApp").show();
}

// $("#brandSelect").off("click")(function(e){
//     console.log($("#brandSelect").val());
//     if($("#brandSelect").val().length == 0){
//         console.log("EMPTY");
//     }
// });

