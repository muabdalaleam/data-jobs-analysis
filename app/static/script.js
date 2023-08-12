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

    const bars = svg.selectAll(".bar")
        .data(data.avg_salary)
        .enter()
        .append("rect")
        .attr("class", "bar")
        .attr("x", (d, i) => xScale(data.job_title[i]))
        .attr("width", xScale.bandwidth())
        .attr("y", d => yScale(d))
        .attr("height", d => height - yScale(d))
        .attr("fill", (d, i) => d == data.avg_salary[0] ? main_color : "gray");


    const xAxis = d3.axisBottom(xScale);
    const yAxis = d3.axisLeft(yScale)
        .tickFormat(d3.format(".2s"));;


    svg.append("g")
        .attr("class", "x-axis")
        .attr("transform", `translate(0,${height})`)
        .call(xAxis);

    svg.append("g")
        .attr("class", "y-axis")
        .call(yAxis);

    const titleText = "Product Prices"; // Change this to your desired title
    const titleFontSize = 18;

    svg.append("text")
        .attr("class", "plot-title")
        .attr("x", svgWidth / 2) // Centered horizontally
        .attr("y", -margin.top / 2) // Adjust for top margin
        .attr("text-anchor", "middle") // Centered text
        .text(titleText);
}
// -------------------------------------------------------------------------------


plotSalaryPerJobTitle();    