// Sample data in the specified format

const svgWidth  = 400;
const svgHeight = 240;
const margin    = { top: 30, right: 20, bottom: 30, left: 30 };

const width          = svgWidth - margin.left - margin.right;
const height         = svgHeight - margin.top - margin.bottom;
const main_color     = "#51fcc6";
const secondry_color = "#666666";
const minRadius      = 4;
const maxRadius      = 8;
const numRows = 4;
const numCols = 7;

const title_shift_const = 20

function calculateQ3(data) {
    const sortedData = d3.sort(data);
    const medianPosition = Math.floor(sortedData.length * 0.75);

    return d3.quantile(sortedData, 0.75);
}

function capitalizeFirstLetter(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}

// &&&&&&&&&&&&&&&&&&&&&&&&&&&Salary per Job title bar chart&&&&&&&&&&&&&&&&&&&&&&&&&&&
let salary_per_job_title_url = "/data/salary_per_job_title";

async function plotSalaryPerJobTitle() {

    const response = await fetch(salary_per_job_title_url);
    const data     = await response.json();

    const svg = d3.select("#salary_per_job_title")
        .append("svg")
        .attr("width", svgWidth)
        .attr("height", svgHeight)
        .append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);
        

    // ====================Making the plot X and Y axises====================
    const xScale = d3.scaleBand()
        .domain(data.job_title)
        .range([0, width])
        .padding(0.1)

    const yScale = d3.scaleLinear()
        .domain([0, d3.max(data.avg_salary)])
        .nice()
        .range([height, 0]);

    const xAxis = d3.axisBottom(xScale);
    const yAxis = d3.axisLeft(yScale)
        .tickFormat(d3.format(".2s"));

    svg.append("g")
        .attr("class", "x-axis")
        .attr("transform", `translate(0,${height})`)
        .call(xAxis);

    svg.append("g")
        .attr("class", "y-axis")
        .call(yAxis);
    // =======================================================================


    // =================Making the bar chart & it's animation==================
    const bars = svg.selectAll(".bar")
        .data(data.avg_salary)
        .enter()
        .append("rect")
        .attr("class", "bar")
        .attr("x", (d, i) => xScale(data.job_title[i]))
        .attr("width", xScale.bandwidth())
        .attr("y", yScale(0)) // Start from the bottom
        .attr("height", 0)    // Initial height is 0
        .attr("rx", 3)
        .attr("fill", (d, i) => d == data.avg_salary[0] ? main_color : "gray")
        .attr('class', (d, i) => d == data.avg_salary[0] ? "svg-shadow" : "gray")

    bars.transition()
        .delay((d, i) => i * 500) // Adjust the delay time (in milliseconds)
        .duration(750)            // Transition duration
        .attr("y", d => yScale(d))
        .attr("height", d => height - yScale(d));
    // =======================================================================


    // ====================Plot title====================
    const titleText = "Salary Per Job Title";
    const titleFontSize = 18;

    svg.append("text")
        .attr("class", "plot-title")
        .attr("x", (svgWidth / 2) - title_shift_const)
        .attr("y", -margin.top / 2)
        .attr("text-anchor", "middle")
        .text(titleText);
    // ==================================================
}
// &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&



// &&&&&&&&&&&&&&&&&&&&&&&&&&&Top 10 Paid skills vs top 10 reqierd skills&&&&&&&&&&&&&&&&&&&&&&&&&&&
paid_vs_required_skills_url = "/data/paid_vs_required_skills";

async function plotTopPaidVsReqierdSkills() {

    const response = await fetch(paid_vs_required_skills_url);
    const data = await response.json();

    console.log(data);
    
    const svg = d3.select("#paid_vs_required_skills")
        .append("svg")
        .attr("width", svgWidth)
        .attr("height", svgHeight)
        .append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);

    const radiusScale = d3.scaleLinear()
        .domain([d3.min(data.avg_salary), d3.max(data.avg_salary)])
        .range([minRadius, maxRadius]);


    // ====================X axis====================
    const xScale = d3.scaleLinear()
        .domain([0, 0])
        .range([0, width]);

    svg.append("g")
        .attr("class", "x-axis")
        .attr("transform", "translate(0," + height + ")")
        .call(d3.axisBottom(xScale)
                .ticks(7)
                .tickFormat(d3.format(".2s")))

        .attr("opacity", "0");
    // ==============================================


    // ====================Y axis====================
    const yScale = d3.scaleLinear()
        .domain([0, d3.max(data.appending_count)])
        .range([height, 0]);

    svg.append("g")
        .attr("class", "y-axis")
        .call(d3.axisLeft(yScale)
                .ticks(3));
    // ==============================================


    // ====================Making the tooltip====================
    const mouseover = function (event, d, i) {
        tooltipText.style("opacity", 1);
        tooltipRect.style("opacity", 1);
    };
    
    const mousemove = function (event, d, i) {
        const [mouseX, mouseY] = d3.pointer(event);
    
        const tooltipPadding = 5;
    
        tooltipText.text(capitalizeFirstLetter(d))
            .attr("x", (mouseX - 10) + tooltipPadding)
            .attr("y", mouseY - 15)
            .attr("class", "plot-text");

        tooltipRect
            .attr("x", (mouseX - 10))
            .attr("y", mouseY - 30)
            .attr("width", tooltipText.node().getComputedTextLength() + 2 * tooltipPadding)
            .attr("height", 20)
    };
    
    const mouseleave = function (event, d, i) {
        tooltipText.style("opacity", 0);
        tooltipRect.style("opacity", 0);
    };
    
    var tooltipRect = svg.append("rect")
        .attr("class", "tooltip")
        .style("opacity", 0)
        .style("fill", "black")
        .style("stroke", "black")
        .attr("rx", 3)
        .style("stroke-width", "1px");

    var tooltipText = svg.append("text")
        .attr("class", "tooltip")
        .style("opacity", 0)
        .style("font-size", "12px");
    // ==================================================================


    // ====================Creating the scatter plot====================
    svg.selectAll(".dot")
        .data(data.skill)
        .enter().append("circle")
        .attr("class", "dot")
        .attr("cx", (d, i) => xScale(data.avg_salary[i]))
        .attr("cy", (d, i) => yScale(data.appending_count[i] + 15))
        .attr("r", (d, i) => radiusScale(data.avg_salary[i]))
        .style("fill", (d, i) => data.avg_salary[i] > calculateQ3(data.avg_salary) ? main_color : "gray")
        .attr('class', (d, i) => data.avg_salary[i] > calculateQ3(data.avg_salary) ? "svg-shadow" : "gray")
        .on("mouseover", mouseover)
        .on("mousemove", mousemove)
        .on("mouseleave", mouseleave)
        .attr("opacity", "0");
    // ==================================================================


    // ====================Plot title====================
    const titleText = "Skills Pay Vs Appending Count"; // Change this to your desired title
    const titleFontSize = 18;

    svg.append("text")
        .attr("class", "plot-title")
        .attr("x", (svgWidth / 2) - title_shift_const  )
        .attr("y", -margin.top / 2)
        .attr("text-anchor", "middle")
        .text(titleText);
    // ===================================================


    // ====================Adding the X axis animation====================
    xScale.domain([d3.min(data.avg_salary) / 1.2, d3.max(data.avg_salary) * 1.1]);

    svg.select(".x-axis")
        .transition()
        .duration(2000)
        .attr("opacity", "1")
        .call(d3.axisBottom(xScale)
                .tickFormat(d3.format(".2s"))
                .ticks(7));
    
    svg.selectAll("circle")
        .attr("cx", 20)
        .transition()
        .delay(function(d, i) { return (i * 3); })
        .duration(3000)
        .attr("cx", (d, i) => xScale(data.avg_salary[i]))
        .attr("cy", (d, i) => yScale(data.appending_count[i] + 15))
        .attr("opacity", "1");

    svg.selectAll("circle")
        .transition()
        .delay(3000) // Wait for the first transition to finish
        .duration(3000)
        .attr("cx", (d, i) => xScale(data.avg_salary[i]))
        .attr("cy", (d, i) => yScale(data.appending_count[i] + 15))
        .attr("opacity", "1")
    // ==================================================================


    // ====================Add x-axis label====================
    svg.append("text")
        .attr("class", "x-label")
        .attr("x", (svgWidth / 2) - title_shift_const)
        .attr("y", height + margin.bottom - 4)
        .style("text-anchor", "middle")
        .text("Average Pay")
        .attr("class", "plot-text")
        .attr("font-size", "10");
    // =========================================================
}
// &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&



// &&&&&&&&&&&&&&&&&&&&&&&&&&People earned more than 1,000 on Upwork Pictogram&&&&&&&&&&&&&&&&&&&&&&&&&&
people_who_earned_money_url = "/data/people_who_earned_money";

async function plotPeopleWhoEarnedMoneyPictogram() {

    const response = await fetch(people_who_earned_money_url);
    let data = await response.json();

    // console.log(data);
    
    // ============================Creating the SVG canvas & the X, Y axes============================
    const svg = d3.select("#people_who_earned_money")
        .append("svg")
        .attr("width", svgWidth)
        .attr("height", svgHeight)
        .append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);

    const yScale = d3.scaleLinear()
        .range([0,250])
        .domain(d3.range(numRows));

    const xScale = d3.scaleLinear(numCols)
        .range([0, 250])
        .domain(d3.range(7));
    // ===============================================================================================


    // ======================================Creating the chart=======================================
    console.log(data_)

    var container = svg.append('g').attr('transform', 'translate(135,130)');

    container.selectAll('circle')
        .data(data_)
        .enter()
        .append('circle')
        .attr('id', function(d, i) {
            return 'id' + i;
        })
        .attr('cx', function(d, i) {
            return xScale(i % numCols);
        })
        .attr('cy', function(d, i) {
            return yScale(Math.floor(i / numCols));
        })
        .attr('r', 12)
        .attr('fill', function(d) {
            return d === 'people_earned_money' ? main_color : secondary_color;
        })
        .style('stroke', 'black');
    // ===============================================================================================
};

// &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&



// &&&&&&&&&&&&&&&&&&&&&&&&&&&$$$$$$$$$$$$$$Average Salaries Map&&&&&&&&&&$$$$$$$$$$$$$$&&&&&&&&&&&&&&&&&
// async
// function plotAverageSalariesMap() {

//     const data = {
//         'address': ['Menlo Park, CA', 'San Francisco, CA', 'Concord, CA'],
//         'avg_salary': [80000, 150000, 70000]
//     };
    
//     // Preparing the addresses data
//     async function getCoordinates(address) {
//         const geocoder = new google.maps.Geocoder();
//         return new Promise((resolve, reject) => {
//             geocoder.geocode({ address: address }, (results, status) => {
//                 if (status === google.maps.GeocoderStatus.OK) {
//                     const location = results[0].geometry.location;
//                     resolve({ lat: location.lat(), lon: location.lng() });
//                 } else {
//                     reject(status);
//                 }
//             });
//         });
//     }
    
//     // Create map function
//     async function createMap() {
//         // Get coordinates for addresses
//         const coordinatesPromises = data.address.map(address => getCoordinates(address));
//         const coordinates = await Promise.all(coordinatesPromises);
    
//         // Create map layout
//         const layout = {
//             title: 'Average Salary by City in California',
//             geo: {
//                 projection: { type: 'mercator' },
//                 center: { lat: 36.7783, lon: -119.4179 },
//                 scope: 'usa',
//                 bgcolor: 'rgba(0,0,0,0)',
//                 showland: true,
//                 landcolor: 'rgb(48,48,48)',
//                 countrycolor: 'rgb(48,48,48)',
//                 showlakes: true,
//                 lakecolor: 'rgb(0,0,0)',
//                 showocean: true,
//                 oceancolor: 'rgb(0,0,0)',
//                 showrivers: true,
//                 rivercolor: 'rgb(0,0,0)',
//             }
//         };
    
//         // Create map data
//         const mapData = [{
//             type: 'scattergeo',
//             mode: 'markers+text',
//             locations: coordinates.map(coord => [coord.lat, coord.lon]),
//             text: data.avg_salary.map(salary => `$${salary.toLocaleString()}`),
//             marker: {
//                 size: data.avg_salary.map(salary => Math.sqrt(salary) / 1000),
//                 sizemode: 'diameter',
//                 opacity: 0.7,
//                 color: 'red'
//             }
//         }];
    
//         // Create the plot using Plotly
//         Plotly.newPlot('avg_salaries_map', mapData, layout);
//     }
    
//     // Call the createMap function
//     createMap();
// }

// &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&

plotSalaryPerJobTitle(); 
plotTopPaidVsReqierdSkills();
plotPeopleWhoEarnedMoneyPictogram();
// plotAverageSalariesMap();
