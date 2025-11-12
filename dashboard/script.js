`use strict`

let linkedinJSON
let upworkJSON

var skillsScatter
var earningsHistogram

const defaultOptions = {
	scales: { y: { beginAtZero: true } },
	responsive: true,
	maintainAspectRatio: false,
	plugins: {
		legend: {"display" : false },
		title: {
			display: true,
			font: {"size": 25, "weight": "normal"},
			color: "white",
			padding: { top: 0, bottom: 10 }
		},
		tooltip: {
			titleFont: {"size": 20, "weight": "bold"},
			bodyFont: {"size": 13, "weight": "normal"},
			displayColors: false,
			intersect: true
		}
	},
	scales: {
		x: {
			ticks: { color: "#CCCCCC"},
			grid: {display: false},
			title: {display: true, color: "#CCCCCC", font: {"size": 13, "weight": "normal"}} 
		},
		y: {
			ticks: { color: "#666666"},
			grid: {color: "#666666"} 
		}
	},
	animation: {
		duration: 1000, // Animation duration in milliseconds
		easing: 'easeInOutQuart' // Ease in-out animation
	}
}

// XXX: animations not working
Chart.defaults.animation = true;

async function loadRawJSON() {
	// if this function was called before don't execute it
    if (linkedinJSON !== undefined && upworkJSON !== undefined) {
		return
	}

	let [response1, response2] = await Promise.all([
        fetch('data/linkedin.json'),
        fetch('data/upwork.json')
    ])

	try {
		linkedinJSON = await response1.json()
		upworkJSON   = await response2.json()
	} catch (error) {
		throw new Error("JSON data didn't load", error)
	}

	Object.keys(linkedinJSON).forEach((column) => {
		if (typeof(linkedinJSON[column]) !== "object") {
			throw new Error("Invalid format for data/linkedin.json")
		}
		linkedinJSON[column] = Object.values(linkedinJSON[column])
	})

	Object.keys(upworkJSON).forEach((column) => {
		if (typeof(upworkJSON[column]) !== "object") {
			throw new Error("Invalid format for data/upwork.json")
		}
		upworkJSON[column] = Object.values(upworkJSON[column])
	})
}


function drawMedianSalary(jobsData) {
	let salaries = jobsData["salary"].sort((a, b) => { return a - b})
	let median = (
		salaries[Math.floor((salaries.length+1)/2)-1] + 
		salaries[Math.ceil( (salaries.length+1)/2)-1]
	) / 2

	let titleElm = document.createElement("h2")
	let valueElm = document.createElement("h1")

	let medianSalaryDiv = document.getElementById('chart1')
	medianSalaryDiv.textContent = '';

	titleElm.textContent += "Median salary from job postings"
	valueElm.textContent += `${(median / 1000).toFixed(0)}K`

	medianSalaryDiv.append(titleElm)
	medianSalaryDiv.append(valueElm)
}

function drawSkillsScatter(jobsData) {
	if (skillsScatter !== undefined) skillsScatter.destroy()

	let options = JSON.parse(JSON.stringify(defaultOptions))
	let data = {} // keys: skill name, values: object holding occurances as x & earnings as y 

	let skillsScatterCtx = document.getElementById('chart2').children[0].getContext("2d")

	Object.values(jobsData["skills"]).forEach((skills_str, i) => {
		let skills = skills_str.split(",")

		skills.forEach((skill) => {
			if (!(skill in data)) data[skill] = {"x": 0, "y": []} // the y array should be converted into a number
			data[skill]["x"] += 1
			data[skill]["y"].push(jobsData["salary"][i]) // this must be devided later to get the mean
		})
	})

	Object.keys(data).forEach((skill) => {
		// calculating the salary median
		let salaries = data[skill]["y"].sort((a, b) => { return a - b })

		data[skill]["y"] = (
			salaries[Math.floor((salaries.length+1)/2)-1] + 
			salaries[Math.ceil((salaries.length+1)/2)-1]
		) / 2

		if (data[skill]["x"] < 10) delete data[skill]
	})

	options["radius"] = 9
	options["hoverRadius"] = 12
	options["borderColor"] = "#111111" 
	options["borderWidth"] = 4

	options["plugins"]["title"]["text"] = "Median skill salary vs. skill frequency"
	options["scales"]["x"]["title"]["text"] = "Frequency"
	options["scales"]["y"]["ticks"]["callback"] = (val, _, __) => { return (val / 1000) + "K" }

	options["plugins"]["tooltip"]["callbacks"] = {}
	options["plugins"]["tooltip"]["callbacks"]["label"] = (ctx) => {
		return `Avg skill salary: ${(ctx.parsed.y/1000).toFixed(0)}K`
	}

	skillsScatter = new Chart(skillsScatterCtx, {
		type: 'scatter',
		data: {
			labels: Object.keys(data),
			datasets: [{
				data: Object.values(data),
				backgroundColor: '#1DCD9F'
			}]
		},
		options: options
	})
}

function drawEarningsHistogram(freelancersData) {
	let earningsHistogramCtx = document.getElementById('chart3').children[0].getContext("2d")
	if (earningsHistogram !== undefined) earningsHistogram.destroy()

	let data = new Map() // keys: earning range, values: frequency
	let options = JSON.parse(JSON.stringify(defaultOptions))

	Object.values(freelancersData["earnings"]).forEach((earning) => {
		let roundedEarning
		roundedEarning = (() => {
			if      (earning == null)                                               return NaN
			else if (earning / Math.pow(10, Math.floor(Math.log10(earning+1))) < 4) return 1
			else if (earning / Math.pow(10, Math.floor(Math.log10(earning+1))) < 7) return 5
			else    return 10
		})() * Math.pow(10, Math.floor(Math.log10(earning+1)))

		if (!(data.has(roundedEarning))) data.set(roundedEarning, 1)
		data.set(roundedEarning, data.get(roundedEarning) + 1) 
	})

	data = new Map([...data.entries()].sort((a, b) => {
		return isNaN(a[0]) ? -1 : isNaN(b[0]) ? 1 : a[0] - b[0]
	}))

	let labels = Array.from(data.keys()).map((n) => {
		return isNaN(n) ? "NaN" : `~${n >= 1e6 ? n/1e6 + "M" : n >= 1e3 ? n/1e3 + "K" : n}`
	})

	options["borderColor"] = "#1DCD9F"
	options["borderWidth"] = 4
	options["plugins"]["title"]["text"] = "Freelancers earnings distribution"	
	options["scales"]["x"]["title"]["text"] = "Earnings"

	earningsHistogram = new Chart(earningsHistogramCtx, {
		type: 'bar',
		data: {
			labels: labels,
			datasets: [{
				label: 'Frequency',
				data: Array.from(data.values()),
				backgroundColor: "#111111"
			}]
		},
		options: options,
	})
}

function drawAvgHourRate(freelancersData) {
	let sum = freelancersData["hour_rate"].reduce((acc, curr) => { return acc + curr }, 0)
	let n = freelancersData["hour_rate"].filter(Number.isFinite).length

	let avgHourRateDiv = document.getElementById("chart4")
	avgHourRateDiv.textContent = "";
	
	let titleElm = document.createElement("h2")
	let valueElm = document.createElement("h1")

	titleElm.textContent += "Avg. freelancer hour rate"
	valueElm.textContent += `${(sum / n).toFixed(1)}$`

	avgHourRateDiv.append(titleElm)
	avgHourRateDiv.append(valueElm)
}

let render = () => {
	// let country  = document.getElementById("countries").value
	let jobField = document.getElementById("job-field").value

	let jobsData = {}
	let freelancersData = {}

	let jobsIndecies = linkedinJSON["job_title"]
		.map((jt, i) => { return (jt === jobField || jobField === "all" ? i : NaN) })
		.filter((idx) => { return (!isNaN(idx)) })

	let freelancersIndecies = upworkJSON["job_title"]
		.map((jt, i) => { return (jt === jobField || jobField === "all" ? i : NaN) })
		.filter((idx) => { return (!isNaN(idx)) })

	Object.keys(linkedinJSON).forEach((key) => {
		jobsData[key] = []
		jobsIndecies.forEach((idx) => {
			jobsData[key].push(linkedinJSON[key][idx])
		})
	})

	Object.keys(upworkJSON).forEach((key) => {
		freelancersData[key] = []
		freelancersIndecies.forEach((idx) => {
			freelancersData[key].push(upworkJSON[key][idx])
		})
	})

	console.log(jobsData)
	
	drawSkillsScatter(jobsData)
	drawMedianSalary(jobsData)

	drawAvgHourRate(freelancersData)
	drawEarningsHistogram(freelancersData)
}

// Should work when: DOM loaded, Refreshed, Color theme changed,
document.addEventListener("DOMContentLoaded", async () => {
	await loadRawJSON();

	document.getElementById("job-field").addEventListener("change", render)

	render()
})
