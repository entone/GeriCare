var modal_obj = "";
var ajax_obj = ""
var controller = "";
var UTCDATES = [];

$(document).ready(function(){
    do_rows();
    modal_obj = new simplemodal("modal", "<img src='"+base_url+"static/images/rotation.gif' />"); 
    ajax_obj = new ajax("loader_indicator");
    bind_search();
    // size_elements();
    menus();
    //create_new();
});

function menus() {
    $('.menu.button').each(function(){
        $(this).menu({
            content: $(this).siblings(".menu_contents").first().html(),
            maxHeight: 100,
//            positionOpts: { posX: 'right' },
            showSpeed: 0
        });
    });
}

function load_discount_form(){
    var val = $("#discount_selector").val();
    ajax_obj.call("Discounts", "load_discount_form", {d_type:val}, "#form_update", function(data){
        $("#form_update").html(data.result.html)
        set_forms();
    });
}

function formsetExpand() {
	$('.fieldset .fieldset > .legend').each(function(){
	    if(!this.expander){
	        this.expander = true;
            $(this).click(function(e){
                $(this).parent().toggleClass('open');
            });
        }
	});
}

function bind_email_templates(id){
    $(".email_templates").change(function(){
        var val = $(this).val();
        console.log(val);
        ajax_obj.call(controller, "load_email_template", {id:id, template:val}, "#nada", function(data){
            modal_obj.display(data.result.html, "Sending to: "+data.result.data.address);
            set_forms();
            bind_email_templates(id);
        })
    })
}

var search_interval = 0;
function bind_search(){
    $("#search").keypress(function(e){            
        clearInterval(search_interval);
        search_interval = setInterval(function(){
            do_search();
            clearInterval(search_interval)
        }, 500);
    });
}

function bind_ticket(){
    $(".ticket").each(function(){
        console.log("Ticket");
        $(this).click(function(e){
            modal_obj.loading();
            var id = $(this).attr("id").split(":_:")[1];
            ajax_obj.call(controller, "start_ticket", {id:id}, "", function(data){
                modal_obj.display(data.result, "Tickets")
                set_forms();
            })
        });
    })
}

function load_tickets(id){
    window.open(base_url+"merchants/start_ticket/?id="+id, "_blank", "status=1,location=1,scrollbars=1,width=300,height=600");
}

function size_elements(){
    $("#table").height($(window).height()-30);
    $("#form_wrap").height($(window).height()-30);
}

function init_remove(){
    $(".remove_element").each(function(){
        console.log("removing");
        if(!this.remove_set){       
            $(this).click(function(e){
                e.stopPropagation();
                console.log("Click!")
                var identifier = $(this).parent().parent().parent().children("h5").children(".item-loader").attr("id");
                console.log(identifier);
                if(!$(this).attr("id").ends_with("null")){
                    id = $(this).attr("id").split(":_:")[1]
                    var callback_data = {val:"", name:"", id:id}
                    ajax_obj.call(controller, "remove_element", {element:$(this).attr("id"), callback_data:callback_data}, "", function(data){
                        var id = data.callback_data.id;
                        focus("#"+id);
                    });
                }
                $(this).parent().parent().remove();
                enable_option(identifier);
            });
            this.remove_set = true;
            
        }
    });
}

function do_search(){
    q = $("#search").val();
    ajax_obj.call(controller, "search", {query:q}, false, function(data){
        $("#table").html(data.result.html);
        do_rows();
        menus();
        return false;
    });
    return false;
}

function load_sms_history(id){
    modal_obj.loading()
    ajax_obj.call(controller, "load_sms_history", {id:id}, false, function(data){
        modal_obj.display(data.result.html, data.result.data.title);            
    });
}

function load_transactions(id){
    modal_obj.loading()
    ajax_obj.call(controller, "load_transactions", {id:id}, false, function(data){
        //console.log("hmmm");
        modal_obj.display(data.result.html, "Transactions");            
    });
}

function load_changes(id){
    modal_obj.loading()
    ajax_obj.call(controller, "load_changelog", {id:id}, false, function(data){
        modal_obj.display(data.result.html, "Changelog");            
    });
}

function load_customers(id){
    modal_obj.loading()
    ajax_obj.call(controller, "load_customers", {id:id}, false, function(data){
        modal_obj.display(data.result.html, "Customers");
    });
}

function load_callback(id){
    modal_obj.loading()
    ajax_obj.call(controller, "load_callback", {id:id}, false, function(data){
        modal_obj.display(data.result.html, "Callback Notification");
        set_forms();
    });
}

function completed_callback(id){
	ajax_obj.call(controller, "completed_callback", {id:id}, false, function(data) {
	});
}

function load_users(id){
    modal_obj.loading()
    ajax_obj.call(controller, "load_users", {id:id}, false, function(data){
        modal_obj.display(data.result.html, "Users");
        set_forms();
        expanders();
        bind_unique();
        $("tr.merchant_user_row").each(function(){
            $('.edit_user', this).click(function(e){
                load_merchant_user($(e.target).attr("data-id"))
                e.stopPropagation()
                return false;
            });
        })
    });
}

function load_promotions(id){
    modal_obj.loading()
    ajax_obj.call(controller, "load_promotions", {id:id}, false, function(data){
        modal_obj.display(data.result.html, "Promotions");
        set_forms();
        expanders();
        $("tr.merchant_user_row").each(function(){
            $('.edit_promo', this).click(function(e){
                load_merchant_promo($(e.target).attr("data-id"))
                e.stopPropagation()
                return false;
            });
        })
    });
}

function load_shipments(id){
    modal_obj.loading()
    ajax_obj.call(controller, "load_shipments", {id:id}, false, function(data){
        modal_obj.display(data.result.html, "Shipments");
        set_forms();
        expanders();
        loader_buttons();
        $("tr.merchant_user_row").each(function(){
            $('.edit_shipment', this).click(function(e){
                load_merchant_shipment($(e.target).attr("data-id"))
                e.stopPropagation()
                return false;
            });
        })
    });
}

function view_dashboard(user_id, merchant_id){
    ajax_obj.call(controller, "change_username", {user_id:user_id, merchant_id:merchant_id}, false, function(data){
        window.open(base_url+"dashboard/login/?next=%2F#/Home/");
    });
}

function show_occurences(id){
    modal_obj.loading()
    ajax_obj.call(controller, "show_occurences", {id:id}, false, function(data){
        modal_obj.display(data.result.html, "Occurences");            
    });
}

function run_report(id){
    ajax_obj.call(controller, "run", {id:id}, false, function(data){
        console.log("RAN!");
        load_object(id);
        modal_obj.close();
    });
}

function get_params(id){
    modal_obj.loading()
    ajax_obj.call(controller, "get_params", {id:id}, false, function(data){
        modal_obj.display(data.result.html, "Configure");
        set_forms();
        expanders();
    });
}

function view_report_output(id){
    modal_obj.loading();
    ajax_obj.call(controller, "view_output", {id:id}, false, function(data){
        modal_obj.display(data.result.html, "Output");
    });
}

function load_merchant_promo(id){
    ajax_obj.call(controller, "merchant_promo", {id:id}, false, function(data){
        $("#merchant_promo").html(data.result.html);
        set_forms();
        expanders();
    })
}

function load_merchant_shipment(id){
    ajax_obj.call(controller, "merchant_shipment", {id:id}, false, function(data){
        $("#merchant_shipment").html(data.result.html);
        set_forms();
        expanders();
        loader_buttons();
    })
}

function load_merchant_user(id){
    ajax_obj.call(controller, "merchant_user", {id:id}, false, function(data){
        $("#merchant_user").html(data.result.html)
        bind_unique();
        set_forms();
        expanders();
    })
}

function load_changes_made(id){
    modal_obj.loading()
    ajax_obj.call(controller, "changes_made", {id:id}, false, function(data){
        modal_obj.display(data.result.html, "Changes Made");            
    });
}

function load_bills(id){
    modal_obj.loading()
    ajax_obj.call(controller, "bills", {id:id}, false, function(data){
        modal_obj.display(data.result.html, "Bills");            
    });
}

function do_rows(){
    $("tr.merchant_row").each(function(){
        $(this).click(function(ev){
            focus(this);
        });        
    });
    sortables_init();
    /*
    $(".transactions").click(function(e){
        console.log("WOOT!!!")
        load_transactions($(e.target).attr("data-id"));
        e.stopPropagation();
        return false;
    })
    $(".changes").click(function(e){
        load_changes($(e.target).attr("data-id"));
        e.stopPropagation();
        return false;
    })
    
    $(".customers", this).click(function(e){
        load_customers($(e.target).attr("data-id"));
        e.stopPropagation();
        return false;
    })
    $(".users", this).click(function(e){
        load_users($(e.target).attr("data-id"));
        e.stopPropagation();
        return false;
    })
    $(".changes_made", this).click(function(e){
        load_changes_made($(e.target).attr("data-id"));
        e.stopPropagation();
        return false;
    })
    */
}

function focus(obj){
    $("table tbody > tr").removeClass("selected");
    $(obj).addClass("selected");
    load_object($(obj).attr("id"));
}

function create_new(cont, title){
    controller = cont ? cont : controller
    modal_obj.loading();
    ajax_obj.call(controller, "get_new", false, false, function(data){
        modal_obj.display(data["result"], title);
        set_forms();
        loaders();
        expanders();
        loader_buttons();
        bind_unique();
        bind_discount_drop();
    });
}

function view_email(id){
    modal_obj.loading();
    ajax_obj.call("Dashboard", "view_email", {id:id}, false, function(data){
        modal_obj.display(data["result"].html, data['result'].data.title);
    });
}

function compose_email(id){
    modal_obj.loading();
    ajax_obj.call("Emailsystem", "compose_email", false, false, function(data){
        modal_obj.display(data["result"].html, data['result'].data.title);
    });
}

function send_email(email_subject,email_body){
    ajax_obj.call("Emailsystem", "send_email", {email_subject:email_subject, email_body:email_body}, false, function(data){
    })
}

function parse_fieldsets(element){
    var obj = {};
    $(element).children(":not(a, legend, label, span, .ignore, input[type=submit], input[type=checkbox]:not(:checked), input[type=radio]:not(:checked))").each(function(){
        var tag = $(this)[0].tagName.toLowerCase();
        if(tag != 'div' && tag != 'form'){
            try{
            	var name = $(this).attr('name');
            	for(dat in UTCDATES){
                	if(name == UTCDATES[dat].key){
                		var val = DateTime.getTimestamp(UTCDATES[dat].date, UTCDATES[dat].time);
                		var name = UTCDATES[dat].name;
                	}
            	}
            	
                if(!val){
                	var val = $(this).val();
                }
                obj[name] = val
            }catch(e){
                console.log(e);
                return false;
            }
        }else if(tag == 'div' && $(this).hasClass('fieldset')){
            var id = $(this).attr('data-id').split(".").pop();
            obj[id] = parse_fieldsets(this);
        }
    });
    return obj
}

var unique_interval = 0
function bind_unique(){
    console.log("Looking for unique fields");
    $(".unique").each(function(){
        $(this).keypress(function(e){
            var id = $(this).attr('id');            
            clearInterval(unique_interval);
            var self = this;
            unique_interval = setInterval(function(){
                var val = $(self).val();
                clearInterval(unique_interval)
                ajax_obj.call('Util', 'unique_field', {namespace:id, ns_controller:controller, value:val}, 'feedback-'+id, function(data){
                    console.log(data.result)
                    var name = "feedback-"+id;
                    if(data.result){
                        result = "Valid"                        
                        $("span[id='"+name+"']").addClass('validator').removeClass('invalid').html(result);
                    }else{
                        result = "Already in use"
                        $("span[id='"+name+"']").addClass('validator invalid').html(result);                        
                    }
                    $("span[id='"+name+"']").show();
                    if($("span[id='"+name+"']").prev().hasClass('form_error')) $("span[id='"+name+"']").prev().remove();
                    console.log(result);
                })
            }, 500);
        });
    })
    bind_sms();
    bind_username();
    bind_hotspot_username()
}

var unique_interval = 0
function bind_sms(){
    console.log("Looking for unique SMS fields");
    $(".unique-sms").each(function(){
        this.current_val = $(this).val();
        this.form_id = $(this).closest("form").children(".fieldset:first-child").attr("data-id").split(".")[1];
        $(this).keypress(function(e){
            var id = $(this).attr('id');
            clearInterval(unique_interval);
            var self = this;
            unique_interval = setInterval(function(){
                var val = $(self).val();
                clearInterval(unique_interval)
                ajax_obj.call('Util', 'unique_field', {namespace:id, ns_controller:controller, parent_id:self.form_id, value:val, current_val:self.current_val, extra:"{channels.platform:'sms'}"}, 'feedback-'+id, function(data){
                    console.log(data.result)
                    var name = "feedback-"+id;
                    if(data.result){
                        result = "Valid"
                        $("span[id='"+name+"']").addClass('validator').removeClass('invalid').html(result);
                    }else{
                        result = "Already in use"
                        $("span[id='"+name+"']").addClass('validator invalid').html(result);
                    }
                    $("span[id='"+name+"']").show();
                    if($("span[id='"+name+"']").prev().hasClass('form_error')) $("span[id='"+name+"']").prev().remove();
                    console.log(result);
                })
            }, 500);
        });
    })
}

var unique_interval = 0
function bind_username(){
    console.log("Looking for unique Username fields");
    $(".unique-username").each(function(){
        this.current_val = $(this).val();
        this.form_id = $(this).closest("form").children(".fieldset:first-child").attr("data-id").split(".")[1];
        $(this).keypress(function(e){
            var id = $(this).attr('id');            
            clearInterval(unique_interval);
            var self = this;
            unique_interval = setInterval(function(){
                var val = $(self).val();
                clearInterval(unique_interval)
                ajax_obj.call('Util', 'unique_field', {namespace:id, ns_controller:"Merchantuser", parent_id:self.form_id, value:val, current_val:self.current_val}, 'feedback-'+id, function(data){
                    console.log(data.result)
                    var name = "feedback-"+id;
                    if(data.result){
                        result = "Valid"
                        $("span[id='"+name+"']").addClass('validator').removeClass('invalid').html(result);
                    }else{
                        result = "Already in use"
                        $("span[id='"+name+"']").addClass('validator invalid').html(result);
                    }
                    $("span[id='"+name+"']").show();
                    if($("span[id='"+name+"']").prev().hasClass('form_error')) $("span[id='"+name+"']").prev().remove();
                    console.log(result);
                })
            }, 500);
        });
    })
}

var unique_interval = 0
function bind_hotspot_username(){
    console.log("Looking for unique Username fields");
    $(".unique-hotspot-username").each(function(){
        this.current_val = $(this).val();
        this.form_id = $(this).closest("form").children(".fieldset:first-child").attr("data-id").split(".")[1];
        $(this).keypress(function(e){
            var id = $(this).attr('id');            
            clearInterval(unique_interval);
            var self = this;
            unique_interval = setInterval(function(){
                var val = $(self).val();
                clearInterval(unique_interval)
                ajax_obj.call('Util', 'unique_field', {namespace:id, ns_controller:"Users", parent_id:self.form_id, value:val, current_val:self.current_val}, 'feedback-'+id, function(data){
                    console.log(data.result)
                    var name = "feedback-"+id;
                    if(data.result){
                        result = "Valid"
                        $("span[id='"+name+"']").addClass('validator').removeClass('invalid').html(result);
                    }else{
                        result = "Already in use"
                        $("span[id='"+name+"']").addClass('validator invalid').html(result);
                    }
                    $("span[id='"+name+"']").show();
                    if($("span[id='"+name+"']").prev().hasClass('form_error')) $("span[id='"+name+"']").prev().remove();
                    console.log(result);
                })
            }, 500);
        });
    })
}


function set_forms(){
    $("form").each(function(){
        if(!this.submit_set){
            console.log("adding new FORM: "+this);
            $(this).submit(function(){
                $("input[type=submit]").attr("disabled", "disabled");
                var data = {};
                
                try{
                    data.form = JSON.stringify(parse_fieldsets(this));
                    console.log(data);
                }catch(e){
                    console.log(e);
                }
                var mod = modal_obj;
                var action = $(this).attr("action") ? $(this).attr("action") : 'save';
                console.log(action);
                console.log(controller);
                ajax_obj.call(controller, action, data, "#response", function(data){                    
                    console.log(data.result.success);
                    if(data.result.success){
                        if(mod.open) mod.close();
                        if(action == 'save'){ 
                            var old_data = data.result 
                            ajax_obj.call(controller, "get_all", false, "#table", function(data){ 
                                do_rows(); 
                                focus($("#"+old_data.data.id));
                                menus();
                            }); 
                        } 
                    }
                    $("input[type=submit]").removeAttr("disabled");
                });
                return false;
            });
            this.submit_set = true;
        }
    })
    formsetExpand();
}

function expanders(){
    $(".expando").each(function(){
        $(this).click(function(){
            var id = "#"+$(this).attr("id").substr(7);
            $(id).toggle();
        })
    })
}

function loader_buttons(){
    $(".item-loader-button").click(function(ev){
        return do_load($(this).parent("div").parent(".fieldset"));
    });
}

function merchant_email(id){
    modal_obj.loading();
    ajax_obj.call(controller, "merchant_email", {id:id}, "", function(data){
        modal_obj.display(data.result.html, "Sending to: "+data.result.data.address);
        set_forms();
        bind_email_templates(id);
    });
    return false;
}

function do_load(obj){
    console.log(obj);
    var attr = $(obj).attr("data-id");
    var type = $("#"+attr+"_channel_selector").val();
    
    ajax_obj.call(controller, "load_object", {attr:attr, type:type}, attr, function(data){
        $(".fieldset[data-id="+data.identifier+"]").children(".add_widget").after(data.result.html);
        init_remove();
        bind_unique();
    });
    return false;
}


function loaders(){}

function disable_option(obj, key){
    //console.log($("#"+obj+" option:selected"));
    if(!$("#"+obj).hasClass("nodisable")) $("#"+obj+" option:selected").attr("disabled", "disabled");
}

function enable_option(obj){
    if(!$("#"+obj).hasClass("nodisable")) $("#"+obj+" option:selected").attr("disabled", "");
}

function load_object(id){
    //console.log(id);
    ajax_obj.call(controller, "get_one", {id:id}, "#form_wrap", function(data){
        set_forms();
        bind_unique();
        loaders();
        loader_buttons();
        init_remove();
        set_tabs(id);
        bind_checklist(id);
    });
}

function bind_cancel_reason(){
    $('#form').delegate('select[name="status"]','change',function() {
    	cancel_reason();
    });
    cancel_reason();
}

function cancel_reason(){
	var el_status = $('select[name="status"]');
	var el_cancel = $('select[name="cancel_reason"]');
	if (el_status.val()=="Cancelled"){
		el_cancel.removeAttr('disabled');
	}
	else{
		el_cancel.prop('value', 0);
		el_cancel.prop('disabled', true);
	}
}

function bind_discount_drop(){
    console.log("woot");
    $("#discount_selector").change(function(){
        console.log("yo");
        load_discount_form();
    });
}

function bind_checklist(id){
    console.log("binding")
    $(".onboarding_task").click(function(){
        var task_id = $(this).attr("id");
        console.log(id);
        $("span[id='feedback_"+task_id+"']").html("...");
        var clear = false
        if(!$(this).is(":checked")) clear = true
        ajax_obj.call(controller, "complete_task", {id:id, task:task_id, clear:clear}, "#feedback_"+id, function(data){
            console.log(data.result.data);
            if(data.result.data != "NA") $("span[id='feedback_"+task_id+"']").html(data.result.data);
            else $("span[id='feedback_"+task_id+"']").html("");
        });
    });
}

var current_tab = 'tasks';
var loading_tab = false

function set_tabs(id){
    $(".tabs").children().each(function(){
        $(this).click(function(){
            $(this).parent().children().each(function(){
                var ele_a = $(this).children("a")[0];
                $(ele_a).removeClass("selected");
            });
            var ele_a = $(this).children("a")[0];
            var class_list = $(ele_a).attr('class').split(/\s+/);
            for(var c in class_list){
                if(class_list[c] != 'tab_wrap'){
                    var cls = class_list[c];
                    break;
                }
            }
            $(ele_a).addClass('selected');
            loading_tab = cls;
            current_tab = false;
            $("#form").html("<div class='content'>Loading...</div>");
            ajax_obj.call(controller, "tab_"+cls, {id:id}, "none", function(data){
                current_tab = cls
                if(loading_tab == current_tab){
                    $("#form").html(data.result.html);
                    set_forms();
                    bind_unique();
                    loaders();
                    loader_buttons();
                    init_remove();
                    bind_checklist(id);
                    bind_cancel_reason();               
                }
                
            });
        });
    });
}
