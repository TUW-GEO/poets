function poetsViewer(div, host, port) {
	this.host = 'http://'+host+':'+port.toString();
}

poetsViewer.prototype.loadTS = function(lon, lat, sp_res, anom) {
	
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
		    fillGraph: true
		});
		
	});
}
