d3.csv('ue.industry.csv', data => {
    console.log(
	d3.extent(data, d=> +d.index)
    );
});

d3.select('#part1')
            .selectAll('circle')
            .data(dataset)
            .enter()
            .append('circle')
            .attr('r', d => 5)
            .attr('cx', d => d.x)
            .attr('cy', d => d.y)
      
d3.csv('ue_industry.csv', data => {
    Object.keys(data[0]).forEach(key => {
	console.log(key);
    })
});

d3.csv('ue_industry.csv', data => {
    console.log(Object.keys(data[0]));
});


d3.csv('ue_industry.csv', data => {

    industries = ['Agriculture','Business services','Construction','Education and Health',
			'Finance','Government','Information','Leisure and hospitality','Manufacturing',
			'Mining and Extraction','Other','Self-employed','Transportation and Utilities',
			'Wholesale and Retail Trade'];
    colors = ['#393b79', '#5253a3', '#6b6ecf', '#9c9ede', '#637939', '#8ca252', '#b5cf6b', 
                '#cedb9c', '#8b6d31', '#bd9e38', '#e7ba52', '#e7cb93', '#843c39', '#ad494a'];

    totalYmax = d3.sum(
	industries.map(
	    d => d3.max(data, e => +e[d])
	)
    );
        
    xScale = d3.scaleLinear()
                .domain(d3.extent(data, d => +d.index))
                .range([20, 1180]);
            
    yScale = d3.scaleLinear()
                .domain([0, totalYmax])
                .range([580, 20]);
        
    fillScale = d3.scaleOrdinal()
                .domain(industries)
                .range(colors);
        
    stackLayout = d3.stack()
                .keys(industries);
                
    stackArea = d3.area()
                .x((d, i) => xScale(i))
                .y0(d => yScale(d[0]))
                .y1(d => yScale(d[1]));

    console.log(stackLayout(data));
});
