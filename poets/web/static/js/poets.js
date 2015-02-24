function poetsViewer(div, host, port, url) {
	if(url != 'None') {
		this.host = url;
	} else {
		this.host = 'http://'+host+':'+port.toString();
	}
}

poetsViewer.prototype.setVarSelect = function() {
	var reg = $("#region").val()
	link = '/_variables/'+reg;
	// empty select list
	var current = $("#variable").val()
	$("#dataset").empty();
	// fill select again
	$.getJSON(this.host+link, function(data){
		if(data.variables.indexOf(current) == -1) {
			$('#dataset').append(new Option('DATASET', ''));
			$("#dataset option[value='']").attr('selected', 'selected');
		}
		for(var i = 0; i < data.variables.length; i++) {
			var d = data.variables[i];
			$('#dataset').append(new Option(data.variables[i], data.variables[i]));
			if(data.variables[i] == current) {
				$("#dataset option[value="+current+"]").attr('selected', 'selected');
			}
		}
	});
}

poetsViewer.prototype.initLink = function() {
    sel_reg = $("#region").val();
    sel_var = $("#dataset").val();
    if(sel_var == null) {
    	sel_var = $("#variable").val();
    }
    link = "/"+sel_reg+"&"+sel_var
    $("#go").attr('href', link);
}

poetsViewer.prototype.trimSlash = function(str) {
	if(str.substr(-1) == '/') {
        return str.substr(0, str.length - 1);
    }
    return str;
}

poetsViewer.prototype.enableGo = function() {
    if ($("#region").val() == '') {
        $("#go").attr('disabled', 'disabled');
    }
    else if ($("#dataset").val() == '') {
    	$("#go").attr('disabled', 'disabled');
    } else {
        $("#go").removeAttr('disabled');
    }
}

poetsViewer.prototype.loadTS = function(lon, lat, sp_res, range, anom) {
	
	var reg = $("#region").val()
	var src = $("#source").val()
	var dataset = $("#dataset").val()
	
	link = '/_ts/'+reg+'&'+src+'&'+dataset+'&'+lon+','+lat;

	var div = 'graph_';
	
	color = '#DF7401';
	
	var roundr = 1/sp_res;
	var rdec = sp_res.toString()
	rdec = (rdec.split('.')[1].length)
	
	tlon = (Math.round(lon*roundr)/roundr).toFixed(rdec);
	tlat = (Math.round(lat*roundr)/roundr).toFixed(rdec);
	
	title = " ("+tlon+"/"+tlat+")"
	
	if((range[0] != -999) && range[1] != -999) {
		vrange = range;
	}
	else {
		vrange = false;
	}
	
	if(anom == true) {
		link += '&anom';
		div += 'anom_';
		color = '#006699';
		title += ' moving average (window size 100 days)'
	}
	
	$.getJSON(this.host+link, function(data){
		
		for(var i=0;i<data.data.length;i++) {
	        data.data[i][0] = new Date(data.data[i][0]);
	        data.data[i][1] = parseFloat(data.data[i][1]);
	    }
		
		graph = new Dygraph(document.getElementById(div+'body'), data.data, {
		    labels: data.labels,
		    labelsDiv: div+'footer',
		    drawPoints: true,
		    labelsSeparateLines: false,
		    connectSeparatedPoints:true,
		    title: data.labels[1] + title,
		    legend: 'always',
		    colors: [color],
		    fillGraph: true,
		    valueRange: vrange
		});
		
	});
}
