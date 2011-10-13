var modal_obj = "";
var ajax_obj = ""
var controller = "";
var UTCDATES = [];
var current_page = 0;
var page_limit = 10

$(document).ready(function(){
    modal_obj = new simplemodal("modal", "<img src='"+base_url+"static/images/rotation.gif' />"); 
    ajax_obj = new ajax("loader_indicator");
    init_table();
});

function init_table(){
    $(".page_left").click(function(){
        console.log(current_page);
        console.log(page_limit);
        var start = current_page-page_limit > 0 ? current_page-page_limit : 0; 
        ajax_obj.call(controller, "page", {start:start, limit:page_limit}, "locations", function(data){
            console.log(data);
            current_page = current_page-page_limit < 0 ? 0 : current_page-page_limit;
        });
        return false;
    });
    $(".page_right").click(function(){
        console.log(current_page);
        console.log(page_limit);
        var start = current_page+page_limit;
        ajax_obj.call(controller, "page", {start:start, limit:page_limit}, "locations", function(data){
            console.log(data)
            current_page+=page_limit;
        });
        return false;
    });
    var start = current_page
    ajax_obj.call(controller, "page", {start:start, limit:page_limit}, "locations", function(data){
        current_page+=page_limit;
    });
}


