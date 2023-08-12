// Sample data in the specified format

const chart_data = '{{ chart_data|tojson }}';


const data = {
    'price': [1, 2, 4, 5, 2],
    'product': ['shampoo', 'toy', 'game', 'blender', 'soup']
  };

const svgWidth = 400;
const svgHeight = 220;
const margin = { top: 30, right: 20, bottom: 20, left: 30 };

const width = svgWidth - margin.left - margin.right;
const height = svgHeight - margin.top - margin.bottom;
const main_color = "#51fcc6"

let max_price = data.price.reduce((a, b) => Math.max(a, b))


// -------------------Salary per Job title pictogram chart-----------------------
const svg = d3.select("#salary_per_job_title")
  .append("svg")
  .attr("width", svgWidth)
  .attr("height", svgHeight)
  .append("g")
  .attr("transform", `translate(${margin.left},${margin.top})`);

const xScale = d3.scaleBand()
    .domain(data.product)
    .range([0, width])
    .padding(0.1)

const yScale = d3.scaleLinear()
    .domain([0, d3.max(data.price)])
    .range([height, 0]);

const bars = svg.selectAll(".bar")
    .data(data.price)
    .enter()
    .append("rect")
    .attr("class", "bar")
    .attr("x", (d, i) => xScale(data.product[i]))
    .attr("width", xScale.bandwidth())
    .attr("y", d => yScale(d))
    .attr("height", d => height - yScale(d))
    .attr("fill", (d, i) => d == max_price ? main_color : "gray");

const xAxis = d3.axisBottom(xScale);
const yAxis = d3.axisLeft(yScale);
  
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
// -------------------------------------------------------------------------------

