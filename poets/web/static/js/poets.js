function poetsViewer(div) {
	this.host = 'http://127.0.0.1:5000'
}

poetsViewer.prototype.loadTS = function(lon, lat, anom) {
	
	var reg = $("#region").val()
	var src = $("#source").val()
	var dataset = $("#dataset").val()
	
	link = '/_ts/'+reg+'&'+src+'&'+dataset+'&'+lon+','+lat;
	
	var div = 'graph_';
	
	color = '#DF7401';
	
	if(anom == true) {
		link += '&anom';
		div += 'anom_';
		color = '#006699'
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
		    title: data.labels[1]+' ('+lon+'/'+lat+')',
		    legend: 'always',
		    colors: [color],
		    fillGraph: true
		});
		
	});
}
