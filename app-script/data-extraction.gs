// API data
const baseUrl = 'https://analytics.api.aiesec.org/v2/applications/analyze';
const accessToken = '0b085db925bfe08eb8b7acbe9c53eefd26fbe6347cb943ac1da87b1204e5c8db';

// Constants
const entitiesList = [
    { id: 222, name: 'CC' },
    { id: 872, name: 'CN' },
    { id: 1340, name: 'CS' },
    { id: 221, name: 'USJ' },
    { id: 2204, name: 'Kandy' },
    { id: 2175, name: 'Ruhuna' },
    { id: 2188, name: 'SLIIT' },
    { id: 2186, name: 'NSBM' },
    { id: 4535, name: 'NIBM' },
    { id: 5490, name: 'Rajarata' }
];


const regexList = [
  // {name: "Total", pattern: /^.*_total$/},

  {name: "oGV", pattern: /^o_.*_[7]$/},
  {name: "oGTa", pattern: /^o_.*_[8]$/},
  {name: "oGTe", pattern: /^o_.*_[9]$/},

  {name: "iGV", pattern: /^i_.*_[7]$/},
  {name: "iGTa", pattern: /^i_.*_[8]$/},
  {name: "iGTe", pattern: /^i_.*_[9]$/}
];

// Configs
const startDate = '2024-10-01';
const endDate = '2024-10-31';

const sheetName = "NLDS24"

const keysList = [
  // "matched",
  "applied",
  // "an_accepted",
  "approved",
  // "realized",
  // "remote_realized",
  // "finished",
  // "completed"
]

const headersList = [
  "Entity",
  "Function",
  // "Matched",
  "Applied",
  // "An-Accepted",
  "Approved",
  // "Realized",
  // "Remote Realized",
  // "Finished",
  // "Completed",
  // "APP_Points",
  // "APD_Points"
]

// Helper functions
function fetchData(startDate, endDate) {
  const url = `${baseUrl}?access_token=${accessToken}&start_date=${startDate}&end_date=${endDate}&performance_v3[office_id]=${1623}`;
  const json = UrlFetchApp.fetch(url).getContentText();
  const data = JSON.parse(json);
  return data;
}

function extractData(apiOutput) {
  let extractedData = {}

  regexList.forEach((regex) => {
    let obj = {}

    const regexMatches = Object.entries(apiOutput).filter(([key, value]) => regex.pattern.test(key));

    regexMatches.forEach((match)=> {
      keysList.forEach((key) => {
        if(match[0].includes(key)){
          obj[key] = obj[key] ? obj[key] : 0 + (match[1]?.doc_count || 0)
        };
      });

      // Add any more calculations here

      // if(match[0].includes("applied")){
      //     obj["app_points"] = match[1]?.applicants?.value * 10;
      // }

      // if(match[0].includes("approved")){
      //     obj["apd_points"] = match[1]?.applicants?.value * 30;
      // }
    })

    extractedData[regex.name] = obj
  })

  return extractedData;
}

function prepareSheet() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(sheetName);

  if (!sheet) {
    throw new Error($`Sheet with name ${sheetName} does not exist.`);
  }

  sheet.getRange(1, 1, 1 , headersList.length).setValues([headersList]); 
}

function writeRowToSheet(rowIndex, rowData){
    const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(sheetName);

    // row --- int --- top row of the range
    // column --- int--- leftmost column of the range
    // optNumRows --- int --- number of rows in the range
    // optNumColumns --- int --- number of columns in the range
    sheet.getRange(1 + rowIndex, 1, 1 , rowData.length).setValues([rowData]); 
}

// =================

function startProcess(){
  console.log("Starting process...");
  prepareSheet();

  let finalOutput = {}
  let allData= fetchData(startDate, endDate);

  console.log("Fetching data...")
  entitiesList.forEach((entity) => {
    let entityData=allData[entity.id.toString()]
    console.log(entityData)
    const extractedData = extractData(entityData);

    finalOutput[entity.name] = extractedData;
  });

  console.log(finalOutput);
  console.log("Writing to sheet edited...");

  entitiesList.forEach((entity, index1) => {
    regexList.forEach((regex, index2)=> {
      const dynamicColumns = keysList.map((key) => finalOutput[entity.name][regex.name][key]);

        const rowData = [
        entity.name,
        regex.name,
        ...dynamicColumns
      ];

    writeRowToSheet((index1 * regexList.length)+(index2+1), rowData);
    });
  });

  console.log("Done writing to sheet :)");
}