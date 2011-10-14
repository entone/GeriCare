if(!window.console) {
    window.console = new function() {
        this.log = function(str) {};
        this.dir = function(str) {};
    };
}


function ajax(indicator){
    this.indicator = $("#"+indicator);
    this.callbacks = {}
}

ajax.prototype.call = function(controller, method, data, identifier, callback){
    this.indicator.css("visibility", "visible")
    var time = new Date().getTime();
    data = data ? data : {}
    data.callback_key = controller+"."+method+"."+time;
    data.controller = controller;
    data.method = method;
    data.callback_data = data.callback_data ? JSON.stringify(data.callback_data) : null;
    if(callback) this.callbacks[data.callback_key] = callback
    data.identifier = identifier ? identifier : false;
    var that = this;
    $.ajax({
        type:"POST",
        data:data,
        url:base_url,
        beforeSend: function(xhr) {
            // add some local environment variables
            xhr.setRequestHeader('LOCAL-TZ', Date.today().getTimezone() || 'UTC');
            if (data.method == 'save') {
	            $("#form").scrollTop(0,0);
	            $(".form_error_box").remove()
	            $(".loading").show();
            }
        },
        dataType:"json",
        success:function(data){
            if(data.result){
                 try{
                    data.result = JSON.parse(data.result)
                    $(".loading").hide()
                 }catch(e){
                    //console.log(e);
                 }
                that.ajax_response(data.result);
            }
            if(data.callback_key){
                if(data.callback_data){
                    data.callback_data = JSON.parse(data.callback_data);
                }
                if(that.callbacks[data.callback_key]){
                    that.callbacks[data.callback_key](data);
                    delete that.callbacks[data.callback_key];
                }
            }
            that.indicator.css("visibility", "hidden")
        }
    });
}

ajax.prototype.ajax_response = function(response){
    console.log(response);
    if(response.length){
        for(var i in response){
            var resp = response[i]
            if(resp.action) this.handle_response(resp)
            if(resp.finalize){
                console.log("running finalize!")
                try{
                    var func = window[resp.finalize.method];
                    func.apply(window, resp.finalize.arguments);
                }catch(e){
                    console.log(e);
                }
            }
        }
    }else{
        console.log("single response");
        if(response.action) this.handle_response(response);
        var resp = response;
        if(resp.finalize){
            console.log("running finalize!")
            try{
                var func = window[resp.finalize.method];
                func.apply(window, resp.finalize.arguments);
            }catch(e){
                console.log(e);
            }
        }
    }
}

ajax.prototype.handle_response = function(resp){
    console.log(resp);
    switch(resp.action){
        case "replace":            
            $(resp.identifier).html(resp.html);
            break;
        case "after":
            $(resp.identifier).after(resp.html);
            break;
        case "error":
            $(resp.identifier).html(resp.html);
            render_errors(resp.data);
            break;
        default:
            console.log("no action to process");
    }
    return true;
}


function render_errors(errors, parent){
	$(".form_error").remove()
	$(".form_error_box").remove()
	
	$("input, textarea, select").removeClass("input_error");
    $('.unique_feedback').hide();
    for(var i in errors){
        var err = errors[i];
        if(i != '__id__' && err != true && typeof err == 'string'){
            var sp = i.split(".");            
            var $field = false;
            if(sp.length > 1){
                var inp = sp.pop();
                var parent = sp.join(".");
                console.log(parent);
                console.log(inp);
                $field = $("fieldset[data-id='"+parent+"'] > input[name='"+inp+"']");
            }else{
                $field = $("input[name='"+sp[0]+"']");
            }
            console.log($field);
            $field.addClass("input_error");
            var box_err = "<div class='form_error_box'><p>"+i+" : "+err+"</div>";
            var err = "<div class='form_error'>"+err+"</div>";
            
            try{    
            	$(".error_box").after(box_err)
                $field.after(err)
            }catch(e){
                console.log(e);
            }
        }
    }
    return true
}

function simplemodal(id, loader){
    this.id = id;
    this.loader = loader
    this.open = false;
}

simplemodal.prototype.loading = function(){
    this.display(this.loader, "loading...");
}

simplemodal.prototype.display = function(content, title){
    this.open = true;
    $("#"+this.id+" .modal_content").html(content);
    $("#"+this.id).addClass("modal_show");
    var tit = title ? title : "";
    console.log($("#"+this.id+" .modal_title"));
    $("#"+this.id+" .modal_title").html(tit)
    return false;
}

simplemodal.prototype.close = function(){
    this.open = false;
    $("#"+this.id).removeClass("modal_show");
    $("#"+this.id+" .modal_content").html("");
    return false;
}


String.prototype.ends_with = function(str){
    return (this.match(str+"$")==str)
}
