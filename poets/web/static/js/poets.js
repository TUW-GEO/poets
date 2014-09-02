function poetsViewer(div) {
	this.host = 'http://127.0.0.1:5000'
}

poetsViewer.prototype.loadTS = function() {
	
	$.getJSON(this.host+'/create_json', function(data){
		
		for(var i=0;i<data.data.length;i++) { 
	        data.data[i][0] = new Date(data.data[i][0]);
	    }
		
		graph = new Dygraph(document.getElementById('graph1'), data.data, {
		    labels: data.labels,
		    drawPoints: true,
		    ylabel: 'Data',
		    labelsSeparateLines: false,
		    connectSeparatedPoints:true,
		    title: 'test',
		    legend: 'always',
		    colors: ['#DF7401'],
		    fillGraph: true
		});
		
	});
}
