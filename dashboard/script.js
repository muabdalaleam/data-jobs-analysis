`use strict`

//  This script should be:
// - Effecient
// - Modefieable
// - Easy to read
// - Consice functions

let linkedinJSON
let upworkJSON
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
			text: 'Chart Title',
			padding: { top: 0, bottom: 10 }
		}
	}
}

function deepFreeze(obj) {
	// https://codesynopsis.com/posts/how-to-prevent-mutating-an-object-in-javascript
	if (obj === null || typeof obj !== 'object') return obj
	
	Object.keys(obj).forEach((key) => {
		deepFreeze(obj[key])
	})
	
	return Object.freeze(obj)
}

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

function drawSkillsScatter(jobsData);

function drawMedianSalary(jobsData);

function drawAvgHourRate(freelancersData);

function drawEarningsHistogram(freelancersData);

async function main() {
	await loadRawJSON()

	// deepFreeze(defaultOptions)
	// deepFreeze(linkedinJSON)
	// deepFreeze(upworkJSON)
	
	let jobsData        = linkedinJSON;
	let freelancersData = upworkJSON;

	// ==================== Chart 1 ====================
	{
		let skillsScatterCtx = document.getElementById('chart1').children[0].getContext("2d")

		let options = JSON.parse(JSON.stringify(defaultOptions))
		let data = {} // keys: skill name, values: object holding occurances as x & earnings as y 

		Object.values(jobsData["skills"]).forEach((skills_str, i) => {
			if (jobsData["salary"][i] <= 5000) return

			let skills = skills_str.split(",")

			skills.forEach((skill) => {
				if (!(skill in data)) data[skill] = {"x": 0, "y": []} // the y array should be converted into a number
				data[skill]["x"] += 1
				data[skill]["y"].push(jobsData["salary"][i]) // this must be devided later to get the mean
			})
		})

		Object.keys(data).forEach((skill) => {
			// calculating the salary median
			let salaries = data[skill]["y"].sort()
			data[skill]["y"] = (
				salaries[Math.floor((salaries.length+1)/2)-1] + 
				salaries[Math.ceil((salaries.length+1)/2)-1]
			) / 2

			if (data[skill]["x"] < 10) delete data[skill]
		})

		options["radius"] = 5
		options["plugins"]["title"]["text"] = "Median skill salary vs. skill frequency"

		new Chart(skillsScatterCtx, {
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
	// =================================================
	

	// ==================== Chart 2 ====================
	{
		let medianSalaryDiv = document.getElementById('chart2')
		let median = (
			jobsData["salary"][Math.floor((jobsData["salary"].length+1)/2)-1] + 
			jobsData["salary"][Math.ceil((jobsData["salary"].length+1)/2)-1]
		) / 2

		let titleElm = document.createElement("h2")
		let valueElm = document.createElement("h1")

		titleElm.textContent += "Median salary from job postings"
		valueElm.textContent += `${(median / 1000).toFixed(0)}K`

		medianSalaryDiv.append(titleElm)
		medianSalaryDiv.append(valueElm)
	}
	// =================================================


	// ==================== Chart 3 ====================
	{
		let avgHourRateDiv = document.getElementById('chart3')
		let sum = freelancersData["hour_rate"].reduce((acc, curr) => { return acc + curr }, 0)
		let n = freelancersData["hour_rate"].filter(Number.isFinite).length
		
		let titleElm = document.createElement("h2")
		let valueElm = document.createElement("h1")

		titleElm.textContent += "Avg. freelancer hour rate"
		valueElm.textContent += `${(sum / n).toFixed(1)}$`

		avgHourRateDiv.append(titleElm)
		avgHourRateDiv.append(valueElm)
	}
	// =================================================


	// ==================== Chart 4 ====================
	{
		let earningsHistogramCtx = document.getElementById('chart4').children[0].getContext("2d")

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

		options["plugins"]["title"]["text"] = "Freelancers earnings distribution"	

		new Chart(earningsHistogramCtx, {
			type: 'bar',
			data: {
				labels: labels,
				datasets: [{
					label: 'Frequency',
					data: Array.from(data.values()),
					backgroundColor: '#1DCD9F'
				}]
			},
			options: options,
		})
	}
	// =================================================
}

// Should work when: DOM loaded, Refreshed, Color theme changed,
document.addEventListener("DOMContentLoaded", () => {
	document.getElementById("countries").addEventListener("change", main)
	main()
})
