const svgWidth  = 400;
const svgHeight = 230;
const margin    = { top: 30, right: 20, bottom: 30, left: 30 };

const width             = svgWidth - margin.left - margin.right;
const height            = svgHeight - margin.top - margin.bottom;
const main_color        = "#51fcc6";
const main_color_darker = "#64caaa";
const secondary_color   = "#808080";
const dark_font_color   = "#272b30";
const minRadius         = 4;
const maxRadius         = 8;
const rectSizeFactor    = 1.2;

const maxStringSize = 40;
const numRows       = 4;
const numCols       = 7;

const textVericalShiftFactor = 1.05;
const TitleShiftConst        = 20;

function calculateQ3(data) {
    const sortedData = d3.sort(data);
    const medianPosition = Math.floor(sortedData.length * 0.75);

    return d3.quantile(sortedData, 0.75);
}

function capitalizeFirstLetter(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}


// ==============================Creating the Dropdowns==============================
// function sendSelectedValues(selectedJobTitle, selectedCountry) {
//     fetch('/dropdown_data', {
//         method: 'POST',
//         headers: {
//             'Content-Type': 'application/json'
//         },
//         body: JSON.stringify({country: selectedCountry,
//                             job_title: selectedJobTitle})
//     });
// }

// function handleChangeEvent() {
//     var selectedJobTitle = document.getElementById('job_title').value;
//     var selectedCountry = document.getElementById('country').value;
//     sendSelectedValues(selectedJobTitle, selectedCountry);
// }

// function handleLoadEvent() {
//     var selectedJobTitle = document.getElementById('job_title').value;
//     var selectedCountry = document.getElementById('country').value;
//     sendSelectedValues(selectedJobTitle, selectedCountry);
// }

// // Attach event listeners
// document.getElementById('job_title').addEventListener('change', handleChangeEvent);
// document.getElementById('country').addEventListener('change', handleChangeEvent);
// window.addEventListener('load', handleLoadEvent);
// ==================================================================================



// ===========================Salary per Job title bar chart==========================
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
        

    // --------------------Making the plot X and Y axises--------------------
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
    // ------------------------------------------------------------------------


    // ----------------=Making the bar chart & it's animation------------------
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
    // -----------------------------------------------------------------------


    // ------------------------------Plot title-------------------------------
    const titleText = "Salary Per Job Title";
    const titleFontSize = 18;

    svg.append("text")
        .attr("class", "plot-title")
        .attr("x", (svgWidth / 2) - TitleShiftConst)
        .attr("y", -margin.top / 2)
        .attr("text-anchor", "middle")
        .text(titleText);
    // ------------------------------------------------------------------------
}
// =================================================================================================



// ==========================&Top 10 Paid skills vs top 10 reqierd skills===========================
paid_vs_required_skills_url = "/data/paid_vs_required_skills";

async function plotTopPaidVsReqierdSkills() {

    const response = await fetch(paid_vs_required_skills_url);
    const data = await response.json();

    const svg = d3.select("#paid_vs_required_skills")
        .append("svg")
        .attr("width", svgWidth)
        .attr("height", svgHeight)
        .append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);

    const radiusScale = d3.scaleLinear()
        .domain([d3.min(data.avg_salary), d3.max(data.avg_salary)])
        .range([minRadius, maxRadius]);


    // --------------------------X axis-----------------------
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
    // -------------------------------------------------------


    // -------------------------Y axis-------------------------
    const yScale = d3.scaleLinear()
        .domain([0, d3.max(data.appending_count)])
        .range([height, 0]);

    svg.append("g")
        .attr("class", "y-axis")
        .call(d3.axisLeft(yScale)
                .ticks(3));
    // ---------------------------------------------------------


    // --------------------Making the tooltip--------------------
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
    // --------------------------------------------------------

    // ----------------Creating the scatter plot---------------
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
    // --------------------------------------------------------


    // ----------------------Plot title-------------------------
    const titleText = "Skills Pay Vs Appending Count"; // Change this to your desired title
    const titleFontSize = 18;

    svg.append("text")
        .attr("class", "plot-title")
        .attr("x", (svgWidth / 2) - TitleShiftConst  )
        .attr("y", -margin.top / 2)
        .attr("text-anchor", "middle")
        .text(titleText);
    // ---------------------------------------------------------


    // ----------------Adding the X axis animation---------------
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
    // ------------------------------------------------------------


    // ----------------------Add x-axis label----------------------
    svg.append("text")
        .attr("class", "x-label")
        .attr("x", (svgWidth / 2) - TitleShiftConst)
        .attr("y", height + margin.bottom - 4)
        .style("text-anchor", "middle")
        .text("Average Pay")
        .attr("class", "plot-text")
        .attr("font-size", "10");
    // ------------------------------------------------------------
}
// ====================================================================================================&



// ==========================People earned more than 1,000 on Upwork Pictogram==========================
people_who_earned_money_url = "/data/people_who_earned_money";

async function plotPeopleWhoEarnedMoneyPictogram() {

    const response = await fetch(people_who_earned_money_url);
    let data = await response.json();

    const earnedMoneyPercentage = data['people_earned_money_percentage'][0];
    const didntEarnMoneyPercentage = data['people_didnt_earn_money_percentage'][0];
    
    // ----------Creating the SVG canvas & the X, Y axes------------
    const svg = d3.select("#people_who_earned_money")
        .append("svg")
        .attr("width", svgWidth)
        .attr("height", svgHeight)
        .append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);

    const yScale = d3.scaleBand()
        .range([height+30, 10])
        .domain(d3.range(numRows));

    const xScale = d3.scaleBand()
        .range([0, width])
        .domain(d3.range(numCols));
    // --------------------------------------------------------------


    // ----------------------Creating the chart----------------------
    const totalCells = numRows * numCols;
    const numEarnedMoneyCells = Math.round((earnedMoneyPercentage / 100) * totalCells);

    const chart_data = Array.from(
        { length: totalCells - numEarnedMoneyCells },
        () => 'people_didnt_earn_money'
    ).concat(Array.from({ length: numEarnedMoneyCells }, () => 'people_earned_money'));
    

    const container = svg.append('g')
        .attr("y", -60)

    const images = container.selectAll('image')
            .data(chart_data)
            .enter()
            .append('image')
            .attr('xlink:href', d => d == 'people_earned_money' ? '../static/assets/person_colored.svg' : '../static/assets/person_grey.svg')
            .attr('width', 40)
            .attr('height', 40)
            .attr('x', (d, i) => xScale(i % numCols))
            .attr('y', (d, i) => yScale(Math.floor(i / numCols)))
            .attr('class', (d) => d === 'people_earned_money' ? "svg-shadow" : secondary_color)
            .attr('opacity', 0)
    // -------------------------------------------------------------------


    // ----------------------------Plot title-----------------------------
    const titleText = "Who earned above 1K on Upwork"; // Change this to your desired title
    const titleFontSize = 18;

    svg.append("text")
        .attr("class", "plot-title")
        .attr("x", (svgWidth / 2) - TitleShiftConst - 10)
        .attr("y", -margin.top / 2)
        .attr("text-anchor", "middle")
        .text(titleText);

    svg.append("text")
        .attr("class", "plot-text")
        .attr("x", (svgWidth / 2) - TitleShiftConst - 10)
        .attr("y", (-margin.top / 2) + 15)
        .attr("text-anchor", "middle")
        .attr("font-size", 12)
        .text("& who didn't");
    // -------------------------------------------------------------------


    // ---------------Adding animations to the chart----------------------
    images.transition()
        .delay((d, i) => (i * 100))
        .duration(500)
        .attr('opacity', 1);
    // -------------------------------------------------------------------
};

// =====================================================================================================



// =========================Total Jobs Per Industry Stacked single column chart=========================
total_jobs_per_industry_url = "/data/total_jobs_per_industry_data";

async function plotTotalJobsPerIndustry() {


    // -----------------Preparing the chart data & main SVG-------------------
    const response = await fetch(total_jobs_per_industry_url);
    const data = await response.json();
    
    const svg = d3.select("#total_jobs_per_industry")
        .append("svg")
        .attr("width", svgWidth)
        .attr("height", svgHeight)
        .append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);

    let chart_data = {'total_jobs': [],
                'industry': []}

    for (let i = 0; i < data.industry.length; i++) {

        let industry = data.industry[i];
        let total_jobs =   data.total_jobs[i];
        
        if (total_jobs > 700) {
            total_jobs = 500

        } else if (total_jobs > 400) {
            total_jobs *= .8

        } else if (total_jobs < 200) {
            total_jobs *= 1.6
        }

        if (industry.length > maxStringSize) {
            industry = industry.slice(0, maxStringSize - 6).concat("...")
        }

        chart_data.industry   .push(industry);
        chart_data.total_jobs .push(total_jobs);
        }
    // -----------------------------------------------------------------------


    // ----------------------Creating the color Gradient----------------------
    const gradientColors = d3.interpolateRgb(main_color_darker, secondary_color);

    const gradientScale = d3.scaleLinear()
        .domain([0, chart_data.total_jobs.length - 1]) // Adjust the domain based on your data
        .range([0, 1]);

    const color = d3.scaleOrdinal()
        .domain(chart_data.total_jobs.map((d, i) => i))
        .range(chart_data.total_jobs.map( (d, i) => gradientColors(gradientScale(i))));
    // -----------------------------------------------------------------------


    // ---------------------Creating the Y axes & the chart-------------------
    
    const yScale = d3.scaleLinear()
        .range([height, 0])
        .domain([0, d3.sum(chart_data.total_jobs)]);

    RectYAxes = (d, i) => yScale(d * rectSizeFactor + d3.sum(chart_data.total_jobs.slice(0, i)) * rectSizeFactor) + margin.bottom;

    const groups = svg.selectAll('.group')
        .data(chart_data.total_jobs)
        .enter()
        .append('g')
        .attr('class', 'group')
        .attr('transform', (d, i) => `translate(${(margin.right * 1.25) - margin.left}, ${RectYAxes(d, i)})`)
        .attr('opacity', 0);

    groups.append('rect')
        .attr('class', 'bar')
        .attr('height', (d) => yScale(0) - yScale(d * rectSizeFactor))
        .attr('width', width)
        .attr('fill', (d, i)   => (i == 0)   ? main_color : color(d))
        .attr("filter", (d, i) => (i == 0) ? `drop-shadow(0px 0px ${10}px ${main_color})` : '');
    // -----------------------------------------------------------------------


    // ------------------------Creating the text labels-----------------------
    groups.append('text')
        .attr('font-size', 11)
        .attr("fill", dark_font_color)
        .attr('xml:space', 'preserve')
        .attr('y', (d) => (d < 300) ? (yScale(0) - yScale(d)/textVericalShiftFactor) : yScale(0) - yScale(d))
        .attr('x', (margin.right))
        .attr('dy', -10)
        .text((d, i) => `${data.industry[i]}`
            .concat(' '.repeat(maxStringSize - data.industry[i].length)))
        

    groups.append('text')
        .attr('font-size', 11)
        .attr("fill", dark_font_color)
        .attr('xml:space', 'preserve')
        .attr('y', (d) => (d < 300) ? (yScale(0) - yScale(d)/textVericalShiftFactor) : yScale(0) - yScale(d))
        .attr('x', (width - margin.left * 2.5))
        .attr('dy', -10)
        .text((d, i) => `${data.total_jobs[i]} Jobs`)
    // -----------------------------------------------------------------------


    // ---------------------------Adding the animation-----------------------
    groups.transition()
        .delay((d, i) => i * 500)
        .duration(750)
        .attr("opacity", 1)
    // ----------------------------------------------------------------------


    // ------------------------------Plot title-------------------------------
    const titleText = "Total jobs per industry"; // Change this to your desired title
    const titleFontSize = 18;

    svg.append("text")
        .attr("class", "plot-title")
        .attr("x", (svgWidth / 2) - TitleShiftConst - 10)
        .attr("y", -margin.top / 2)
        .attr("text-anchor", "middle")
        .text(titleText);
    // -----------------------------------------------------------------------
}
// =====================================================================================================


plotSalaryPerJobTitle(); 
plotTopPaidVsReqierdSkills();
plotPeopleWhoEarnedMoneyPictogram();
plotTotalJobsPerIndustry();