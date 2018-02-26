function toggleDark() {
    for (i=0; i<document.styleSheets.length; i++) {
        if( document.styleSheets.item(i).href.includes("dark.min.css")) {
            var dark = document.styleSheets.item(i)
            if (dark.disabled) {
                Cookies.set("dark", 1);
                dark.disabled = false;
            } else {
                Cookies.set("dark", 0);
                dark.disabled = true;
            }
        }
    }
}
$(function() {
    for (i=0; i<document.styleSheets.length; i++) {
        if( document.styleSheets.item(i).href.includes("dark.min.css")) {
            var dark = document.styleSheets.item(i)
            if (Cookies.get("dark") == 0) {
                dark.disabled = true;
            } else {
                dark.disabled = false;
            }
        }
    }
});

function add_upcoming(url, recipeId, sourceElem, destElem) {
    $.post(url, {
        recipe_id: recipeId,
        upcoming_servings: $(sourceElem).text()
    }).done(function(response) {
        if(response["upcoming"]) {
            $(destElem).removeClass("collapse");
            if (!window.location.pathname.includes("recipes")) {
                location.reload();
            }
        }
    }).fail(function() {
        $(destElem).text("failed");
        $(destElem).show();
    });
}

function remove_upcoming(url, recipeId, destElem) {
    $.post(url, {
        recipe_id: recipeId
    }).done(function(response) {
        if(!response["upcoming"]) {
            $(destElem).addClass("collapse");
            if (!window.location.pathname.includes("recipes")) {
                location.reload();
            }
        }
    }).fail(function() {
        $(destElem).text("failed");
        $(destElem).show();
    });
}

function change_servings(elem, nb) {
    var upcoming_servings = parseInt($(elem).text());
    upcoming_servings += nb
    if (upcoming_servings > 0) {
        $(elem).text(upcoming_servings);
    }
}
