const margin = { top: 50, right: 50, bottom: 50, left: 20 };

function initAIPlotJs2(radarId,demodata) {
    var radarPlot = new RadarPlotManager2();
    const data = demodata;
    // console.log(data);
    radarPlot.createRadarPlot(radarId, data);
}
class RadarPlotManager2 {
    constructor() {
        this.svg = null;
        this.color = null;
        this.xAxis = null;
        this.yAxis = null;
        this.line = null;
        this.angleScale = null;
        this.radiusScale = null;
        this.circleScale = null;
        this.container = null;
        this.toDate = null;
        this.fromDate = null;
        this.tagName = null;
        this.toTime = null;
        this.fromTime = null;
        this.socketObject = {};
        this.socketObjects = [];
        this.pathTempData = [];
        this.totalLength = null;
    }
    createRadarPlot(radarId, data) {
        var svgHeight = 300;
        this.radarId = radarId;
        this.data = data;
        var container = d3.select("#" + radarId);
        this.container = container;
        let width = container.node()?.getBoundingClientRect()?.width - margin.left - margin.right;
        console.log(width);
        let height = svgHeight - margin.top - margin.bottom;
        this.width = width;
        this.height = height;
        // this.initHeader();
        var svgObject = new Svg();
        svgObject.createSvg(container, width, height);
        this.svg = svgObject.getSVG();

        this.showRadarGraph();
        // window.addEventListener("resize", this.showBarGraph(width, height))

    }
    initHeader() {
        var header = this.container
            .append("div")
            .attr("class", "header")
            .append("form")
            .attr("class", "headerForm")
        header.append("div")
            .attr("class", "mainHeader")
            .append("label")
            .text("Enter Tag Name")
            .attr("class", "label")
            .append("input")
            .attr("type", "text")
            .attr("class", "tagName form-control")
            .attr("remember", "true")
            .attr("autocomplete", "on")
            .on("change", (event) => {
                this.tagName = event.target.value;
                // if (this.fromDate !== null && this.toDate !== null) {
                //     this.loadMeasurments();
                // }
            });
        header.append("div")
            .attr("class", "mainHeader")
            .append("label")
            .text("From Date")
            .attr("class", "label")
            .append("input")
            .attr("type", "date")
            .attr("class", "date form-control")
            .attr("id", "fromDate")
            .on("change", (event) => {
                this.fromDate = new Date(event.target.value).getTime();
                // if (this.tagName !== null && this.toDate !== null) {
                //     this.loadMeasurments();
                // }
            });
        header.append("div").attr("class", "mainHeader")
            .append("label")
            .text("From Time")
            .attr("class", "label")
            .append("input")
            .attr("type", "time")
            .attr("class", "time_field form-control")
            .on("change", (event) => {
                this.fromTime = new Date(event.target.value).getTime();
            });
        header.append("div")
            .attr("class", "mainHeader")
            .append("label")
            .text("To Date")
            .attr("class", "label")
            .append("input")
            .attr("type", "date")
            .attr("class", "date form-control")
            .attr("id", "toDate")
            .on("change", (event) => {
                this.toDate = new Date(event.target.value).getTime();
                this.loadMeasurments();
                // if (this.tagName !== null && this.fromDate !== null) {
                //     this.loadMeasurments();
                // }

            });
        header.append("div").attr("class", "mainHeader")
            .append("label")
            .text("To Time")
            .attr("class", "label")
            .append("input")
            .attr("type", "time")
            .attr("class", "time_field form-control")
            .on("change", (event) => {
                this.toTime = new Date(event.target.value).getTime();
            });
    }
   
    handleWebSocketResponse(result) {
        this.resValue = result.value;
        this.loadTagNames();
    }
    routeData(tagData) {
        const pathDescription = tagData.TagLight[0].code.measurementType.description;
        console.log(pathDescription);
        const dataIndex = this.data.findIndex(obj => obj.path === pathDescription)
        const valuesToAdd = [];
        if (this.resValue === 0) {
            this.resValue = 400;
        }
        valuesToAdd.push(this.resValue);
        if (dataIndex === -1) {
            this.data.push({
                path: tagData.TagLight[0].code.measurementType.description,
                dataArray: valuesToAdd
            });
        }
        else {
            for (let i = 0; i < this.data.length; i++) {
                if (i !== dataIndex) {
                    this.data[i].dataArray.push(-1);
                } else {
                    this.data[dataIndex].dataArray.push(...valuesToAdd);
                }
            }
        }

        // console.log(this.data);
        this.showRadarGraph();
    }
    loadTagNames() {
        var filter = {
            TagFilterRest:
            {
                tagName: this.tagName
            }
        }
        var obj = this;
        $(document).ready(function () {
            $.ajax({
                url: requestConfig.url,
                method: "POST",
                contentType: "application/json",
                data: JSON.stringify(filter),
                crossDomain: true,
                async: true,
                headers: requestConfig.headers,
                success: function (res) {
                    return res.json();
                },
                success: function (data) {
                    console.log(data);
                    obj.routeData(data);
                },
                error: function () {
                    console.log("Error occured");;
                }
            });
        });
    }
    showRadarGraph() {
        // d3.selectAll("g").remove();
        if (this.data.length === 0) {
            return;
        }
        this.graph = this.svg.append("g").attr("class", "graphs");
        // this.totalLength = this.data.reduce((acc, d) => {
        //     return acc + d.dataArray.filter(value => value !== -1).length;
        // }, 0);
        this.xAxisLabel = this.svg.append("text").attr("transform",`translate(${this.width / 2 },${this.height+margin.top + margin.bottom})`).text("time")
        this.yAxisLabel = this.svg.append("text").attr("transform",`translate(10,${(this.height/2) + 20}) rotate(-90)`).text("Amplitude")
        this.renderScales();
        this.drawAxis();
        this.generateLine();
        // this.data.forEach((d, i) => {
        //     this.drawPath(d);
        //   });
        this.drawPath(this.data);
    }
    renderScales() {

        const allArrays = this.data;
        const allValues = allArrays.flat();
        const parseTime = (timeString) => {
            const [timePart, microseconds] = timeString.split('.');
            const [hours, minutes, seconds] = timePart.split(':').map(Number);
            const date = new Date();
            date.setHours(hours);
            date.setMinutes(minutes);
            date.setSeconds(seconds);
            date.setMilliseconds(parseInt(microseconds.substring(0, 3)));
            date.setTime(date.getTime() + micros / 1000);
            return date;
        };


        //  const arr = d3.extent(allValues,d=>d.Time);
        //  console.log(arr)
        allValues.forEach(d => {
            d.Time = d.Time;
            d.Amplitude = +d.Amplitude;
        });
        // console.log(allValues)
        const xmax = d3.max(allValues, d => (d.Time));
        const xmin = d3.min(allValues, d => (d.Time));
        const ymax = d3.max(allValues, d => d.Amplitude);

        const ymin = d3.min(allValues, d => d.Amplitude);
        // console.log(xmin,xmax,ymin,ymax)

        this.xScale = d3
            .scaleBand()
            // .domain([new Date(xmin), new Date(xmax)])
            .domain(allValues.map((d) => d.Time))

            .range([0, this.width])//.nice();
        //   console.log(this.xScale.domain());
        this.yScale = d3
            .scaleLinear()
            .domain([ymin, ymax])
            .range([this.height, 0]);
    }
    drawAxis() {
        var currentObj = this;
        this.xAxis = this.svg
            .append("g")
            .attr("class", "x-axis")
            .attr("transform", "translate(40," + this.height + ")");

        this.yAxis = this.svg.append("g").attr("class", "y-axis").attr("transform", "translate(40,0)");;
        this.xAxis
            .transition()
            .duration(300)
            .call(
                d3
                    .axisBottom(this.xScale)
                // .ticks(5)
            ).selectAll("text").style("text-anchor","start").attr("transform","rotate(45)");
            this.svg.selectAll(".tick text")
            .each(function (_, i, nodes) {
                if (i % Math.ceil(currentObj.data.length / 10) !== 0) {
                    d3.select(nodes[i]).remove();
                }
            });
            this.svg.selectAll(".tick line")
            .each(function (_, i, nodes) {
                if (i % Math.ceil(currentObj.data.length / 10) !== 0) {
                    d3.select(nodes[i]).remove();
                }
            });
        this.yAxis.transition().duration(300).call(d3.axisLeft(this.yScale));
        
    }
    generateLine() {
        this.line = d3
            .line()
            .x((d) => {
                return this.xScale(d.Time)
            })
            .y((d) => {
                return this.yScale(d.Amplitude)
            });
    }
    drawPath(data) {
        // console.log(data);
        // console.log(this.svg,this.line);
        this.graph
            .append("path")
            .datum(data)
            .attr("class", "line")
            .attr("fill", "none")
            .attr("stroke", "steelblue")
            .attr("stroke-width", 1.5)
            .attr("d", this.line)
            .attr("transform", "translate(40,0)");
    }
    renderCircles() {

        const min = Math.floor(this.minValue);
        const max = Math.ceil(this.maxValue);
        const numCircles = 4;
        const sides = this.totalLength;
        const radiusStep = (max - min) / numCircles;
        //   console.log(this.radiusScale.ticks(), this.radiusScale.range(), this.radiusScale.domain());
        for (let i = 0; i <= numCircles; i++) {
            const radius = min + i * radiusStep;
            const angleStep = (Math.PI * 2) / sides;
            const startAngle = -Math.PI / 2;
            const polygonVertices = d3.range(sides).map(j => ({
                x: Math.cos(startAngle + j * angleStep) * this.radiusScale(radius),
                y: Math.sin(startAngle + j * angleStep) * this.radiusScale(radius)
            }));

            this.graph.append("polygon")
                .attr("points", polygonVertices.map(v => `${v.x},${v.y}`).join(" "))
                .attr("fill", "none")
                .attr("stroke", "black")
                .attr("transform", `translate(${(this.width + margin.left + margin.right) / 2},${(this.height + margin.top + margin.bottom) / 2})`);
        }
        this.graph.selectAll(".circle-label")
            .data(d3.range(min, max + 1, (max - min) / numCircles))
            .enter().append("text")
            .attr("class", "circle-label")
            .attr("x", -35)
            .attr("y", d => -this.radiusScale(d))
            .text(d => d)
            .attr("transform", `translate(${(this.width + margin.left + margin.right) / 2},${(this.height + margin.top + margin.bottom) / 2})`);

    }
    renderLabels() {
        const labels = this.graph.selectAll(".label")
            .data(d3.range(1, this.totalLength + 1))
            .enter().append("text")
            .attr("class", "label")
            .attr("x", (_, i) => (this.radiusScale(this.maxValue) + 25) * Math.cos(this.angleScale(i) - Math.PI / 2))
            .attr("y", (_, i) => (this.radiusScale(this.maxValue) + 20) * Math.sin(this.angleScale(i) - Math.PI / 2))
            .text((d, i) => d)
            .attr("text-anchor", "middle")
            .attr("alignment-baseline", "middle")
            .attr("transform", `translate(${(this.width + margin.left + margin.right) / 2},${(this.height + margin.top + margin.bottom) / 2})`);
    }
    addLegend() {
        // let previousColor = this.color;
        const legend = this.graph.append("g")
            .attr("class", "legend")
            .attr("transform", `translate(${this.width - 100},${20})`)
            .attr("border", "2px solid steelblue")

        const legendItems = legend.selectAll(".legend-item")
            .data(this.data)
            .enter().append("g")
            .attr("class", "legend-item")
            .attr("transform", (_, i) => `translate(0, ${i * 20})`);
        legendItems.append("line")
            .attr("x1", -10)
            .attr("y1", 0)
            .attr("x2", 0)
            .attr("y2", 0)
            // .attr("stroke", d => (d.path === this.data[this.data.length - 1].path) ? this.color : previousColor)
            .attr("stroke", (d) => this.colorScale(d.path))
            .attr("stroke-width", 2);

        legendItems.append("text")
            .attr("x", 5)
            .attr("y", 0)
            .attr("dy", "0.35em")
            .text(d => d.path)
            .attr("fill", "black")
            .style("font-size", "12px")
            .style("font-family", "Arial");
        // previousColor = this.color;
    }
    windowResize() {
        this.width = this.container.node()?.getBoundingClientRect()?.width - margin.left - margin.right;
        this.height = 450 - margin.top - margin.bottom;
        console.log(this.width, this.height);
    }
}


function initAIPlotJs(radarId,demodata,graphType) {
    var radarPlot = new RadarPlotManager();
    const data = demodata;
    // console.log(data);
    radarPlot.createRadarPlot(radarId, data,graphType);
}
class RadarPlotManager {
    constructor() {
        this.svg = null;
        this.color = null;
        this.xAxis = null;
        this.yAxis = null;
        this.angleScale = null;
        this.radiusScale = null;
        this.circleScale = null;
        this.container = null;
        this.toDate = null;
        this.fromDate = null;
        this.tagName = null;
        this.toTime = null;
        this.fromTime = null;
        this.socketObject = {};
        this.socketObjects = [];
        this.pathTempData = [];
        this.totalLength = null;
    }
    createRadarPlot(radarId, data,graphType) {
        var svgHeight = 400;
        this.radarId = radarId;
        this.data = data;
        this.graphType = graphType;
        var container = d3.select("#" + radarId);
        // console.log(container)
        this.container = container;
        let width = container.node()?.getBoundingClientRect()?.width - margin.left - margin.right;
        console.log(width);
        let height = svgHeight - margin.top - margin.bottom;
        // console.log(width,height);
        this.width = width;
        this.height = height;
        // this.initHeader();
        var svgObject = new Svg();
        svgObject.createSvg(container, width, height);
        this.svg = svgObject.getSVG();

        this.showRadarGraph();
        // window.addEventListener("resize", this.showBarGraph(width, height))

    }
    initHeader() {
        var header = this.container
            .append("div")
            .attr("class", "header")
            .append("form")
            .attr("class", "headerForm")
        header.append("div")
            .attr("class", "mainHeader")
            .append("label")
            .text("Enter Tag Name")
            .attr("class", "label")
            .append("input")
            .attr("type", "text")
            .attr("class", "tagName form-control")
            .attr("remember", "true")
            .attr("autocomplete", "on")
            .on("change", (event) => {
                this.tagName = event.target.value;
                // if (this.fromDate !== null && this.toDate !== null) {
                //     this.loadMeasurments();
                // }
            });
        header.append("div")
            .attr("class", "mainHeader")
            .append("label")
            .text("From Date")
            .attr("class", "label")
            .append("input")
            .attr("type", "date")
            .attr("class", "date form-control")
            .attr("id", "fromDate")
            .on("change", (event) => {
                this.fromDate = new Date(event.target.value).getTime();
                // if (this.tagName !== null && this.toDate !== null) {
                //     this.loadMeasurments();
                // }
            });
        header.append("div").attr("class", "mainHeader")
            .append("label")
            .text("From Time")
            .attr("class", "label")
            .append("input")
            .attr("type", "time")
            .attr("class", "time_field form-control")
            .on("change", (event) => {
                this.fromTime = new Date(event.target.value).getTime();
            });
        header.append("div")
            .attr("class", "mainHeader")
            .append("label")
            .text("To Date")
            .attr("class", "label")
            .append("input")
            .attr("type", "date")
            .attr("class", "date form-control")
            .attr("id", "toDate")
            .on("change", (event) => {
                this.toDate = new Date(event.target.value).getTime();
                this.loadMeasurments();
                // if (this.tagName !== null && this.fromDate !== null) {
                //     this.loadMeasurments();
                // }

            });
        header.append("div").attr("class", "mainHeader")
            .append("label")
            .text("To Time")
            .attr("class", "label")
            .append("input")
            .attr("type", "time")
            .attr("class", "time_field form-control")
            .on("change", (event) => {
                this.toTime = new Date(event.target.value).getTime();
            });
    }
    loadMeasurments() {
        
    }
    handleWebSocketResponse(result) {
        this.resValue = result.value;
        this.loadTagNames();
    }
    
   
    showRadarGraph() {
        // d3.selectAll("g").remove();
        if(this.data.length === 0){
            return;
        }
        this.graph = this.svg.append("g").attr("class", "graphs");
        // this.totalLength = this.data.reduce((acc, d) => {
        //     return acc + d.dataArray.filter(value => value !== -1).length;
        // }, 0);
        this.xAxisLabel = this.svg.append("text").attr("transform",`translate(${this.width / 2 },${this.height+margin.top})`).text("Frequency")
        this.yAxisLabel = this.svg.append("text").attr("transform",`translate(10,${(this.height/2)+ 20}) rotate(-90)`).text("Amplitude")

        this.renderScales();
        this.drawAxis();
        this.generateLine();
        this.drawPath(this.data);
    }
    renderScales() {
        
        const allArrays = this.data;
        const allValues = allArrays.flat();
        

        
        // console.log(xmin,xmax,ymin,ymax)
        switch(this.graphType) {
            case "timeseries" : 
            allValues.forEach(d => {
                d.Time = d.Time;
                d.Amplitude = +d.Amplitude;
            });
            const xmax1 = d3.max(allValues, d => (d.Time));
            const xmin1 = d3.min(allValues, d => (d.Time));
            const ymax1 = d3.max(allValues, d => d.Amplitude);

            const ymin1 = d3.min(allValues, d => d.Amplitude);
            this.xScale = d3
                .scaleBand()
                .domain(allValues.map((d) => d.Time))
                .range([0, this.width])

            this.yScale = d3
                .scaleLinear()
                .domain([ymin1, ymax1])
                .range([this.height, 0]);
             break;
            case "linear" :
                const xmax = d3.max(allValues,d=>d.frequency);
                const xmin = d3.min(allValues,d=>d.frequency);
                const ymax = d3.max(allValues,d=>d.amplitude);

                const ymin = d3.min(allValues,d=>d.amplitude);
                this.xScale = d3
                .scaleLinear()
                .domain([xmin, 10500])
                .range([0, this.width]);
                this.yScale = d3
                    .scaleLinear()
                    .domain([ymin, ymax])
                    .range([this.height, 0]);
        }
        
      
        
    }
    drawAxis(){
        var currentObj = this;
        switch(this.graphType) {
            case "linear" :
                this.xAxis = this.svg
                .append("g")
                .attr("class", "x-axis")
                .attr("transform", "translate(40," + this.height + ")");

                this.yAxis = this.svg.append("g").attr("class", "y-axis").attr("transform", "translate(40,0)");;
                this.xAxis
                .transition()
                .duration(300)
                .call(
                d3
                    .axisBottom(this.xScale)
                    .ticks(this.tickSize)
                ).selectAll("text").style("text-anchor","start").attr("transform","rotate(45)");
                this.yAxis.transition().duration(300).call(d3.axisLeft(this.yScale));

            // case "timeseries" :
            //     this.xAxis = this.svg
            //     .append("g")
            //     .attr("class", "x-axis")
            //     .attr("transform", "translate(30," + this.height + ")");

            //     this.yAxis = this.svg.append("g").attr("class", "y-axis").attr("transform", "translate(30,0)");;
            //     this.xAxis
            //     .transition()
            //     .duration(300)
            //     .call(
            //     d3
            //         .axisBottom(this.xScale)
            //     ).selectAll("text").style("text-anchor","end").attr("transform","rotate(-45)");
            //     this.svg.selectAll(".tick text")
            //     .each(function (_, i, nodes) {
            //         if (i % Math.ceil(currentObj.data.length / 10) !== 0) {
            //             d3.select(nodes[i]).remove();
            //         }
            //     });
            //     this.svg.selectAll(".tick line")
            //     .each(function (_, i, nodes) {
            //         if (i % Math.ceil(currentObj.data.length / 10) !== 0) {
            //             d3.select(nodes[i]).remove();
            //         }
            //     });

            // this.yAxis.transition().duration(300).call(d3.axisLeft(this.yScale));
            // break;
        }
    }
    generateLine() {
        this.line = d3
          .line()
          .x((d) => this.xScale(d.frequency))
          .y((d) => this.yScale(d.amplitude));
    }
    drawPath(data){
    // console.log(this.svg,this.line);
        this.graph
            .append("path")
            .datum(data)
            .attr("class", "line")
            .attr("fill", "none")
            .attr("stroke","steelblue")
            .attr("stroke-width", 1.5)
            .attr("d", this.line)
            .attr("transform", "translate(40,0)");
    }
    renderCircles() {
        
        const min = Math.floor(this.minValue);
        const max = Math.ceil(this.maxValue);
        const numCircles = 4;
        const sides = this.totalLength;
        const radiusStep = (max - min) / numCircles;
              console.log(this.radiusScale.ticks(), this.radiusScale.range(), this.radiusScale.domain());
        for (let i = 0; i <= numCircles; i++) {
            const radius = min + i * radiusStep;
            const angleStep = (Math.PI * 2) / sides;
            const startAngle = -Math.PI / 2;
            const polygonVertices = d3.range(sides).map(j => ({
                x: Math.cos(startAngle + j * angleStep) * this.radiusScale(radius),
                y: Math.sin(startAngle + j * angleStep) * this.radiusScale(radius)
            }));

            this.graph.append("polygon")
                .attr("points", polygonVertices.map(v => `${v.x},${v.y}`).join(" "))
                .attr("fill", "none")
                .attr("stroke", "black")
                .attr("transform", `translate(${(this.width + margin.left + margin.right) / 2},${(this.height + margin.top + margin.bottom) / 2})`);
        }
               this.graph.selectAll(".circle-label")
            .data(d3.range(min, max + 1, (max - min) / numCircles))
            .enter().append("text")
            .attr("class", "circle-label")
            .attr("x", -35)
            .attr("y", d => -this.radiusScale(d))
            .text(d => d)
            .attr("transform", `translate(${(this.width + margin.left + margin.right) / 2},${(this.height + margin.top + margin.bottom) / 2})`);

    }
    renderLabels() {
        const labels = this.graph.selectAll(".label")
            .data(d3.range(1, this.totalLength + 1))
            .enter().append("text")
            .attr("class", "label")
            .attr("x", (_, i) => (this.radiusScale(this.maxValue) + 25) * Math.cos(this.angleScale(i) - Math.PI / 2))
            .attr("y", (_, i) => (this.radiusScale(this.maxValue) + 20) * Math.sin(this.angleScale(i) - Math.PI / 2))
            .text((d, i) => d)
            .attr("text-anchor", "middle")
            .attr("alignment-baseline", "middle")
            .attr("transform", `translate(${(this.width + margin.left + margin.right) / 2},${(this.height + margin.top + margin.bottom) / 2})`);
    }
    addLegend() {
        // let previousColor = this.color;
        const legend = this.graph.append("g")
            .attr("class", "legend")
            .attr("transform", `translate(${this.width - 100},${20})`)
            .attr("border", "2px solid steelblue")

        const legendItems = legend.selectAll(".legend-item")
            .data(this.data)
            .enter().append("g")
            .attr("class", "legend-item")
            .attr("transform", (_, i) => `translate(0, ${i * 20})`);
        legendItems.append("line")
            .attr("x1", -10)
            .attr("y1", 0)
            .attr("x2", 0)
            .attr("y2", 0)
            // .attr("stroke", d => (d.path === this.data[this.data.length - 1].path) ? this.color : previousColor)
            .attr("stroke", (d) => this.colorScale(d.path))
            .attr("stroke-width", 2);

        legendItems.append("text")
            .attr("x", 5)
            .attr("y", 0)
            .attr("dy", "0.35em")
            .text(d => d.path)
            .attr("fill", "black")
            .style("font-size", "12px")
            .style("font-family", "Arial");
        // previousColor = this.color;
    }
    windowResize() {
        this.width = this.container.node()?.getBoundingClientRect()?.width - margin.left - margin.right;
        this.height = 450 - margin.top - margin.bottom;
        console.log(this.width, this.height);
    }
}

class Svg {
    constructor() { }
    getSVG() {
        return this.svg;
    }
    createSvg(container, width, height) {
        this.svg = container
            .append("svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)

    }
}


var normal_Button = document.getElementById("normal");
var unbalance_Button = document.getElementById("unbalance");
var misalignment_Button = document.getElementById("misalignment");
var innerrace_Button = document.getElementById("innerrace");
var outerrace_Button = document.getElementById("outerrace");
var cage_Button = document.getElementById("cage");
var rolling_element_Button = document.getElementById("rolling_element");
var eccentricity_Button = document.getElementById("eccentricity");
var bent_shaft_Button = document.getElementById("bent_shaft");
var broken_impeller_Button = document.getElementById("broken_impeller");
var starvation_Button = document.getElementById("starvation");
var cavitation_Button = document.getElementById("cavitation");

normal_Button.disabled = true;

normal_Button.addEventListener("click", (e) => {
    e.preventDefault();
    $.get("/NormalDataRoute");
    normal_Button.disabled = true;
    unbalance_Button.disabled = false;
    misalignment_Button.disabled = false;
    innerrace_Button.disabled = false;
    outerrace_Button.disabled = false;
    cage_Button.disabled = false;
    // rolling_element_Button.disabled = false;
    eccentricity_Button.disabled = false;
    bent_shaft_Button.disabled = false;
    broken_impeller_Button.disabled = false;
    starvation_Button.disabled = false;
    cavitation_Button.disabled = false;
})

unbalance_Button.addEventListener("click", (e) => {
    e.preventDefault();
    $.get("/unbalanceDataRoute");
    normal_Button.disabled = false;
    unbalance_Button.disabled = true;
    misalignment_Button.disabled = false;
    innerrace_Button.disabled = false;
    outerrace_Button.disabled = false;
    cage_Button.disabled = false;
    // rolling_element_Button.disabled = false;
    eccentricity_Button.disabled = false;
    bent_shaft_Button.disabled = false;
    broken_impeller_Button.disabled = false;
    starvation_Button.disabled = false;
    cavitation_Button.disabled = false;
})

misalignment_Button.addEventListener("click", (e) => {
    e.preventDefault();
    $.get("/misalignmentDataRoute");
    normal_Button.disabled = false;
    unbalance_Button.disabled = false;
    misalignment_Button.disabled = true;
    innerrace_Button.disabled = false;
    outerrace_Button.disabled = false;
    cage_Button.disabled = false;
    // rolling_element_Button.disabled = false;
    eccentricity_Button.disabled = false;
    bent_shaft_Button.disabled = false;
    broken_impeller_Button.disabled = false;
    starvation_Button.disabled = false;
    cavitation_Button.disabled = false;
})

innerrace_Button.addEventListener("click", (e) => {
    e.preventDefault();
    $.get("/innerracefaultDataRoute");
    normal_Button.disabled = false;
    unbalance_Button.disabled = false;
    misalignment_Button.disabled = false;
    innerrace_Button.disabled = true;
    outerrace_Button.disabled = false;
    cage_Button.disabled = false;
    // rolling_element_Button.disabled = false;
    eccentricity_Button.disabled = false;
    bent_shaft_Button.disabled = false;
    broken_impeller_Button.disabled = false;
    starvation_Button.disabled = false;
    cavitation_Button.disabled = false;
})

outerrace_Button.addEventListener("click", (e) => {
    e.preventDefault();
    $.get("/outerracefaultDataRoute");
    normal_Button.disabled = false;
    unbalance_Button.disabled = false;
    misalignment_Button.disabled = false;
    innerrace_Button.disabled = false;
    outerrace_Button.disabled = true;
    cage_Button.disabled = false;
    // rolling_element_Button.disabled = false;
    eccentricity_Button.disabled = false;
    bent_shaft_Button.disabled = false;
    broken_impeller_Button.disabled = false;
    starvation_Button.disabled = false;
    cavitation_Button.disabled = false;
})

cage_Button.addEventListener("click", (e) => {
    e.preventDefault();
    $.get("/cagefaultDataRoute");
    normal_Button.disabled = false;
    unbalance_Button.disabled = false;
    misalignment_Button.disabled = false;
    innerrace_Button.disabled = false;
    outerrace_Button.disabled = false;
    cage_Button.disabled = true;
    // rolling_element_Button.disabled = false;
    eccentricity_Button.disabled = false;
    bent_shaft_Button.disabled = false;
    broken_impeller_Button.disabled = false;
    starvation_Button.disabled = false;
    cavitation_Button.disabled = false;
})

// rolling_element_Button.addEventListener("click", (e) => {
//     e.preventDefault();
//     $.get("/rollingelementfaultfaultDataRoute");
//     normal_Button.disabled = false;
//     unbalance_Button.disabled = false;
//     misalignment_Button.disabled = false;
//     innerrace_Button.disabled = false;
//     outerrace_Button.disabled = false;
//     cage_Button.disabled = false;
//     rolling_element_Button.disabled = true;
//     eccentricity_Button.disabled = false;
//     bent_shaft_Button.disabled = false;
//     broken_impeller_Button.disabled = false;
//     starvation_Button.disabled = false;
//     cavitation_Button.disabled = false;
// })

eccentricity_Button.addEventListener("click", (e) => {
    e.preventDefault();
    $.get("/eccentricityDataRoute");
    normal_Button.disabled = false;
    unbalance_Button.disabled = false;
    misalignment_Button.disabled = false;
    innerrace_Button.disabled = false;
    outerrace_Button.disabled = false;
    cage_Button.disabled = false;
    // rolling_element_Button.disabled = false;
    eccentricity_Button.disabled = true;
    bent_shaft_Button.disabled = false;
    broken_impeller_Button.disabled = false;
    starvation_Button.disabled = false;
    cavitation_Button.disabled = false;
})

bent_shaft_Button.addEventListener("click", (e) => {
    e.preventDefault();
    $.get("/bent_shaftDataRoute");
    normal_Button.disabled = false;
    unbalance_Button.disabled = false;
    misalignment_Button.disabled = false;
    innerrace_Button.disabled = false;
    outerrace_Button.disabled = false;
    cage_Button.disabled = false;
    // rolling_element_Button.disabled = false;
    eccentricity_Button.disabled = false;
    bent_shaft_Button.disabled = true;
    broken_impeller_Button.disabled = false;
    starvation_Button.disabled = false;
    cavitation_Button.disabled = false;
})

broken_impeller_Button.addEventListener("click", (e) => {
    e.preventDefault();
    $.get("/broken_impellerDataRoute");
    normal_Button.disabled = false;
    unbalance_Button.disabled = false;
    misalignment_Button.disabled = false;
    innerrace_Button.disabled = false;
    outerrace_Button.disabled = false;
    cage_Button.disabled = false;
    // rolling_element_Button.disabled = false;
    eccentricity_Button.disabled = false;
    bent_shaft_Button.disabled = false;
    broken_impeller_Button.disabled = true;
    starvation_Button.disabled = false;
    cavitation_Button.disabled = false;
})

starvation_Button.addEventListener("click", (e) => {
    e.preventDefault();
    $.get("/starvationDataRoute");
    normal_Button.disabled = false;
    unbalance_Button.disabled = false;
    misalignment_Button.disabled = false;
    innerrace_Button.disabled = false;
    outerrace_Button.disabled = false;
    cage_Button.disabled = false;
    // rolling_element_Button.disabled = false;
    eccentricity_Button.disabled = false;
    bent_shaft_Button.disabled = false;
    broken_impeller_Button.disabled = false;
    starvation_Button.disabled = true;
    cavitation_Button.disabled = false;
})

cavitation_Button.addEventListener("click", (e) => {
    e.preventDefault();
    $.get("/cavitationDataRoute");
    normal_Button.disabled = false;
    unbalance_Button.disabled = false;
    misalignment_Button.disabled = false;
    innerrace_Button.disabled = false;
    outerrace_Button.disabled = false;
    cage_Button.disabled = false;
    // rolling_element_Button.disabled = false;
    eccentricity_Button.disabled = false;
    bent_shaft_Button.disabled = false;
    broken_impeller_Button.disabled = false;
    starvation_Button.disabled = false;
    cavitation_Button.disabled = true;
})


// var normal_Button = document.getElementById("normal");
// var unbalance_Button = document.getElementById("unbalance");
// var misalignment_Button = document.getElementById("misalignment");
// var innerrace_Button = document.getElementById("innerrace");
// var outerrace_Button = document.getElementById("outerrace");
// var cage_Button = document.getElementById("cage");
// var rolling_element_Button = document.getElementById("rolling_element");
// var eccentricity_Button = document.getElementById("eccentricity");
// var bent_shaft_Button = document.getElementById("bent_shaft");
// var broken_impeller_Button = document.getElementById("broken_impeller");
// var starvation_Button = document.getElementById("starvation");
// var cavitation_Button = document.getElementById("cavitation");
// normal_Button.disabled = true;




// normal_Button.addEventListener("click", (e) => {
//     e.preventDefault();
//     $.get("/NormalDataRoute");
//     // plot_graphs();
//     normal_Button.disabled = true;
//     unbalance_Button.disabled = false;
//     misalignment_Button.disabled = false;
//     // looseness_Button.disabled = false;
//     innerrace_Button.disabled = false;
//     outerrace_Button.disabled = false;
//     cage_Button.disabled = false;
//     rolling_element_Button.disabled = false;
// })

// unbalance_Button.addEventListener("click", (e) => {
//     e.preventDefault();
//     // d3.selectAll("svg").remove();
//     $.get("/unbalanceDataRoute");
//     // plot_graphs();
//     normal_Button.disabled = false;
//     unbalance_Button.disabled = true;
//     misalignment_Button.disabled = false;
//     looseness_Button.disabled = false;
//     innerrace_Button.disabled = false;
//     outerrace_Button.disabled = false;
//     cage_Button.disabled = false;
//     rolling_element_Button.disabled = false;
// })

// misalignment_Button.addEventListener("click", (e) => {
//     e.preventDefault();
//     $.get("/misalignmentDataRoute");
//     // plot_graphs();
//     normal_Button.disabled = false;
//     unbalance_Button.disabled = false;
//     misalignment_Button.disabled = true;
//     looseness_Button.disabled = false;
//     innerrace_Button.disabled = false;
//     outerrace_Button.disabled = false;
//     cage_Button.disabled = false;
//     rolling_element_Button.disabled = false;
// })

// looseness_Button.addEventListener("click", (e) => {
//     e.preventDefault();
//     $.get("/loosenessDataRoute");
//     // plot_graphs();
//     normal_Button.disabled = false;
//     unbalance_Button.disabled = false;
//     misalignment_Button.disabled = false;
//     looseness_Button.disabled = true;
//     innerrace_Button.disabled = false;
//     outerrace_Button.disabled = false;
//     cage_Button.disabled = false;
//     rolling_element_Button.disabled = false;
// })

// innerrace_Button.addEventListener("click", (e) => {
//     e.preventDefault();
//     $.get("/innerracefaultDataRoute");
//     // plot_graphs();
//     normal_Button.disabled = false;
//     unbalance_Button.disabled = false;
//     misalignment_Button.disabled = false;
//     looseness_Button.disabled = false;
//     innerrace_Button.disabled = true;
//     outerrace_Button.disabled = false;
//     cage_Button.disabled = false;
//     rolling_element_Button.disabled = false;
// })
// outerrace_Button.addEventListener("click", (e) => {
//     e.preventDefault();
//     $.get("/outerracefaultDataRoute");
//     // plot_graphs();
//     normal_Button.disabled = false;
//     unbalance_Button.disabled = false;
//     misalignment_Button.disabled = false;
//     looseness_Button.disabled = false;
//     innerrace_Button.disabled = false;
//     outerrace_Button.disabled = true;
//     cage_Button.disabled = false;
//     rolling_element_Button.disabled = false;
// })
// cage_Button.addEventListener("click", (e) => {
//     e.preventDefault();
//     $.get("/cagefaultDataRoute");
//     // plot_graphs();
//     normal_Button.disabled = false;
//     unbalance_Button.disabled = false;
//     misalignment_Button.disabled = false;
//     looseness_Button.disabled = false;
//     innerrace_Button.disabled = false;
//     outerrace_Button.disabled = false;
//     cage_Button.disabled = true;
//     rolling_element_Button.disabled = false;
// })

// rolling_element_Button.addEventListener("click", (e) => {
//     e.preventDefault();
//     $.get("/rollingelementfaultfaultDataRoute");
//     // plot_graphs();
//     normal_Button.disabled = false;
//     unbalance_Button.disabled = false;
//     misalignment_Button.disabled = false;
//     looseness_Button.disabled = false;
//     innerrace_Button.disabled = false;
//     outerrace_Button.disabled = false;
//     cage_Button.disabled = false;
//     rolling_element_Button.disabled = true;
// })
