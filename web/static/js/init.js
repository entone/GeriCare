var modal_obj = "";
var ajax_obj = ""
var controller = "";
var UTCDATES = [];

$(document).ready(function(){
    modal_obj = new simplemodal("modal", "<img src='"+base_url+"static/images/rotation.gif' />"); 
    ajax_obj = new ajax("loader_indicator");
});
