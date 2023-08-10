const express = require('express');
const { BigQuery } = require('@google-cloud/bigquery');
require('dotenv').config({path: '../.env'}); 

const app = express();
const port = 3000;

const bigquery = new BigQuery();
const AUTH_PASSWORD = process.env.AUTH_PASSWORD;


async function executeQuery(query) {
    try {
        const options = {
            query: query,
            location: 'EU', // Set the appropriate location
        };
        const [rows] = await bigquery.query(options);
        return rows;
    } catch (error) {
        console.error('Error querying BigQuery:', error);
        throw new Error('Internal Server Error');
}}


app.get('/query', async (req, res) => {
    try {
        const password = req.query.password;
        if (password !== AUTH_PASSWORD) {
            return res.status(401).json({ error: 'Unauthorized' });
        }

        const query = req.query.query;
        const data = await executeQuery(query);
        res.json(data);
    } catch (error) {
        console.error('Error processing request:', error);
        res.status(500).json({ error: 'Internal Server Error' });
    }
});

app.get('/', (req, res) => {
    res.sendFile(__dirname + '/index.html');
});


app.listen(port, () => {
    console.log(`Server listening at http://localhost:${port}`);
});
