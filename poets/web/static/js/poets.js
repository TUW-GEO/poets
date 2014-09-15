function poetsViewer(div) {
	this.host = 'http://127.0.0.1:5000'
}

poetsViewer.prototype.loadTS = function(lon, lat) {
	
	var reg = $("#region").val()
	var src = $("#source").val()
	var dataset = $("#dataset").val()
	
	link = '/_ts/'+reg+'&'+src+'&'+dataset+'&'+lon+','+lat;
	
	$.getJSON(this.host+link, function(data){
		
		for(var i=0;i<data.data.length;i++) { 
	        data.data[i][0] = new Date(data.data[i][0]);
	    }
		
		graph = new Dygraph(document.getElementById('graph_body'), data.data, {
		    labels: data.labels,
		    labelsDiv: 'graph_footer',
		    drawPoints: true,
		    //ylabel: data.labels[1],
		    labelsSeparateLines: false,
		    connectSeparatedPoints:true,
		    title: data.labels[1]+' ('+lon+'/'+lat+')',
		    legend: 'always',
		    colors: ['#DF7401'],
		    fillGraph: true
		});
		
	});
}
