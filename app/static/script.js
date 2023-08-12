// Sample data in the specified format

const svgWidth = 400;
const svgHeight = 220;
const margin = { top: 30, right: 20, bottom: 20, left: 30 };

const width = svgWidth - margin.left - margin.right;
const height = svgHeight - margin.top - margin.bottom;
const main_color = "#51fcc6"



// -------------------Salary per Job title pictogram chart-----------------------
const api_url = "/data/salary_per_job_title_data";

async function plotSalaryPerJobTitle() {

    const response = await fetch(api_url);
    console.log(response)
    const data = await response.json();


    const svg = d3.select("#salary_per_job_title")
        .append("svg")
        .attr("width", svgWidth)
        .attr("height", svgHeight)
        .append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);

    const xScale = d3.scaleBand()
        .domain(data.job_title)
        .range([0, width])
        .padding(0.1)

    const yScale = d3.scaleLinear()
        .domain([0, d3.max(data.avg_salary)])
        .nice()
        .range([height, 0]);

const yTicks = yScale.ticks();

svg.selectAll(".circle-group")
    .data(data.avg_salary)
    .enter()
    .append("g")
    .attr("class", "circle-group")
    .attr("transform", (d, i) => `translate(${xScale(data.job_title[i]) + xScale.bandwidth() / 2}, ${yScale(data.avg_salary[i])})`)
    // .each(function(d, i) {
const group = d3.select(this)

        // let numCircles = Math.ceil(yScale(yTicks[0]) - yScale(data.avg_salary[i]));
        // numCircles = Math.ceil(numCircles * 0.05); // Down scaling the count of circles so it's more readable

        // console.log(numCircles);

        // for (let j = 0; j < numCircles; j++) {
        //     let circleY = (j * 20); // Adjusted the calculation for y-coordinate

        //     group.append("circle")
        //         .attr("cx", 0)
        //         .attr("cy", circleY)
        //         .attr("r", 10)
        //         .style("fill", "steelblue"); 
        // }
    // });

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

    const titleText = "Salary Per Job Title"; // Change this to your desired title
    const titleFontSize = 18;

    svg.append("text")
        .attr("class", "plot-title")
        .attr("x", svgWidth / 2) // Centered horizontally
        .attr("y", -margin.top / 2) // Adjust for top margin
        .attr("text-anchor", "middle") // Centered text
        .text(titleText);
}
// -------------------------------------------------------------------------------


// ----------------------------Top 10 Paid skills vs top 10 reqierd skills-----------------------------


plotSalaryPerJobTitle();    